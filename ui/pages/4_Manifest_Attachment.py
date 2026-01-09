import io
import math
import os
import sys
import tempfile
import streamlit as st
from PIL import Image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from main import append_overlay_to_existing_qr, encrypt_rsa, extract_header_from_qr, load_key
from proto.event_pb2 import AccessLevelAsserter
from structured_codec import encode_sections_protobuf
from config import FILLER_TILE_COUNT, MODULE_SIZE, MODULE_SIZE_RECURSIVE_CANDIDATES
from c2pa_integration import (
    build_manifest_payload,
    compute_commitments,
    get_c2pa_import_error,
    is_c2pa_available,
    sign_png_with_c2pa,
)
from ui.style import inject_style, page_title, render_sidebar_nav
from ui.schema_form import load_schema, render_layers

st.set_page_config(page_title="Manifest Attachment", layout="centered")
inject_style()
render_sidebar_nav()
page_title("Manifest Attachment")
st.markdown("Attach signed metadata to a QR received from the issuer, with or without an additional attester overlay layer.")
st.caption("Uses C2PA for interoperable verification.")
st.caption("If you need more overlay capacity, request a reissued QR from the issuer before signing.")

img_file = st.file_uploader("Upload QR code for attestation", type=["png"])

st.subheader("Optional: Add Asserter Overlay")
with st.expander("Optional: Add Asserter Overlay", expanded=False):
    st.caption("Use this when the verifier/asserter adds an extra layer before signing.")
    add_overlay = st.checkbox("Add asserter overlay before signing", False)

    asserter_schema = load_schema("schema/asserter_schema.json")
    asserter_layers = {}
    overlay_depth = 1
    issuer_max_depth = None
    if add_overlay:
        if img_file:
            tmp_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(img_file.getvalue())
                    tmp_path = tmp.name
                for candidate_size in [MODULE_SIZE] + MODULE_SIZE_RECURSIVE_CANDIDATES:
                    try:
                        header, _ = extract_header_from_qr(tmp_path, module_size=candidate_size)
                        issuer_max_depth = header.get("asserter_max_depth")
                        break
                    except Exception:
                        continue
            finally:
                if tmp_path and os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        max_depth = issuer_max_depth or 3
        overlay_depth = st.slider("Overlay depth", min_value=1, max_value=max_depth, value=1)
        st.caption(f"Allowed max depth from issuer: {issuer_max_depth or 'Unknown'}")
        asserter_layers = render_layers(asserter_schema)

st.subheader("Attach Manifest")
issuer_name = st.text_input("Issuer name", "Example Event Org")
event_id = st.text_input("Event ID", "EVT-2025-001")
ticket_id = st.text_input("Ticket ID", "TICKET-001")
valid_from = st.text_input("Valid from (ISO)", "2025-09-12T08:00:00Z")
valid_to = st.text_input("Valid to (ISO)", "2025-09-12T20:00:00Z")
cert_path = st.text_input("Issuer certificate path (PEM)", "c2pa_integration/trust_store/issuer_cert.pem")
key_path = st.text_input("Issuer private key path (PEM)", "c2pa_integration/trust_store/issuer_private_key.pem")

if st.button("Attach Signed Metadata + Sign"):
    if not img_file:
        st.error("Upload a ticket PNG first.")
    elif not is_c2pa_available():
        err = get_c2pa_import_error()
        msg = "c2pa-python is not installed or unavailable."
        if err:
            msg = f"{msg} Import error: {err}"
        st.error(msg)
    else:
        try:
            image_bytes = img_file.getvalue()
            if add_overlay:
                asserter_data = asserter_layers.get("asserter_data", {})
                asserter_keys = asserter_data.pop("_keys", {}) if asserter_data else {}
                asserter_pub_path = asserter_keys.get("public_key", "keys/asserter_public.pem")
                asserter_pub = load_key(asserter_pub_path)

                asserter_proto = AccessLevelAsserter()
                asserter_proto.asserter_app_version = encrypt_rsa(
                    asserter_pub, asserter_data.get("asserter_app_version", "")
                )
                asserter_proto.geolocation = encrypt_rsa(
                    asserter_pub, asserter_data.get("geolocation", "")
                )
                asserter_proto.assertion_valid_until = encrypt_rsa(
                    asserter_pub, asserter_data.get("assertion_valid_until", "")
                )

                secret_bitstream = encode_sections_protobuf({"ASSERTER": asserter_proto}, depth=overlay_depth)

                tmp_path = None
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                        tmp.write(image_bytes)
                        tmp_path = tmp.name

                    header = None
                    header_end_tile = None
                    for candidate_size in [MODULE_SIZE] + MODULE_SIZE_RECURSIVE_CANDIDATES:
                        try:
                            header, header_end_tile = extract_header_from_qr(tmp_path, module_size=candidate_size)
                            break
                        except Exception:
                            continue
                    if header is None or header_end_tile is None:
                        raise ValueError("Failed to extract header from the uploaded QR.")

                    reserve_bits = header.get("asserter_reserve_bits") or header.get("reserve_bits") or 0
                    asserter_max_depth = header.get("asserter_max_depth")
                    if asserter_max_depth and overlay_depth > asserter_max_depth:
                        raise ValueError(
                            f"Overlay depth {overlay_depth} exceeds issuer allowance ({asserter_max_depth})."
                        )
                    if reserve_bits and len(secret_bitstream) > reserve_bits:
                        raise ValueError(
                            f"Asserter overlay needs {len(secret_bitstream)} bits, "
                            f"but only {reserve_bits} were reserved."
                        )

                    filler_bits = header.get("filler_bits", FILLER_TILE_COUNT * 8)
                    filler_tiles = math.ceil(filler_bits / 8)
                    issuer_bits_per_tile = header.get("bits_per_tile", 8)
                    issuer_tiles = math.ceil(header.get("bit_length", 0) / issuer_bits_per_tile)
                    tile_start = header_end_tile + filler_tiles + issuer_tiles

                    overlay_img = append_overlay_to_existing_qr(
                        image_path=tmp_path,
                        bitstream=secret_bitstream,
                        module_size=header.get("module_size", MODULE_SIZE),
                        depth=overlay_depth,
                        start_tile=tile_start,
                    )
                finally:
                    if tmp_path and os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                overlay_buf = io.BytesIO()
                overlay_img.save(overlay_buf, format="PNG")
                image_bytes = overlay_buf.getvalue()
                output_dir = "QRcodes"
                os.makedirs(output_dir, exist_ok=True)
                stem = os.path.splitext(img_file.name)[0] if img_file else "qr"
                if stem.startswith("asserter_"):
                    overlay_name = f"{stem}.png"
                else:
                    overlay_name = f"asserter_{stem}.png"
                overlay_path = os.path.join(output_dir, overlay_name)
                overlay_img.save(overlay_path)
                st.success(f"Overlay applied and saved as `{overlay_path}`")

            metadata = st.session_state.get("last_qr_metadata")
            if metadata:
                commitments = compute_commitments(
                    image_bytes=image_bytes,
                    public_payload=metadata["public_payload"],
                    hidden_payload_bytes=metadata["secret_bytes"],
                )
            else:
                commitments = {
                    "image_sha256": compute_commitments(image_bytes, "", b"")["image_sha256"],
                    "l0_payload_sha256": "",
                    "hidden_payload_sha256": "",
                }
            manifest = build_manifest_payload(
                issuer_name=issuer_name,
                intent="event_access_admit",
                event_id=event_id,
                ticket_id=ticket_id,
                valid_from=valid_from,
                valid_to=valid_to,
                commitments=commitments,
            )
            output_dir = "QRcodes"
            os.makedirs(output_dir, exist_ok=True)
            stem = os.path.splitext(img_file.name)[0] if img_file else "qr"
            if stem.startswith("signed_"):
                signed_name = f"{stem}.png"
            else:
                signed_name = f"signed_{stem}.png"
            signed_filename = os.path.join(output_dir, signed_name)
            signed_bytes = sign_png_with_c2pa(
                input_png_bytes=image_bytes,
                manifest_payload=manifest,
                cert_path=cert_path,
                key_path=key_path,
                output_path=signed_filename,
            )
            st.success(f"Signed PNG saved as `{signed_filename}`")
            st.image(Image.open(signed_filename), caption="Signed Ticket", use_container_width=False)
        except Exception as e:
            st.error(f"Signing failed: {e}")
