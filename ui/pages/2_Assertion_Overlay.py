import math
import os
import sys
import tempfile
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from main import (
    append_overlay_to_existing_qr,
    encrypt_rsa,
    extract_header_from_qr,
    load_key,
)
from config import FILLER_TILE_COUNT, MODULE_SIZE, MODULE_SIZE_RECURSIVE_CANDIDATES
from proto.event_pb2 import AccessLevelAsserter
from structured_codec import encode_sections_protobuf
from ui.style import inject_style, page_title, render_sidebar_nav
from ui.schema_form import load_schema, render_layers

st.set_page_config(page_title="Assertion — Overlay", layout="centered")
inject_style()
render_sidebar_nav()
page_title("Assertion — Overlay")
st.markdown("Upload an existing QR and add an **asserter-only** overlay.")
st.caption("If the QR lacks enough reserved capacity, request a reissued QR from the issuer.")

asserter_schema = load_schema("schema/asserter_schema.json")

l0_file = st.file_uploader("Upload General QR PNG", type=["png"], key="l0_upload")
overlay_depth = None
header_error = None
issuer_max_depth = None
if l0_file:
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(l0_file.getvalue())
            tmp_path = tmp.name
        for candidate_size in [MODULE_SIZE] + MODULE_SIZE_RECURSIVE_CANDIDATES:
            try:
                header, _ = extract_header_from_qr(tmp_path, module_size=candidate_size)
                issuer_max_depth = header.get("asserter_max_depth")
                break
            except Exception:
                continue
    except Exception as exc:
        header_error = str(exc)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
    max_depth = issuer_max_depth or 3
    overlay_depth = st.slider("Overlay Depth", min_value=1, max_value=max_depth, value=1)
    st.caption(f"Allowed max depth from issuer: {issuer_max_depth or 'Unknown'}")
else:
    st.caption("Upload a General QR to select overlay depth.")

with st.form("overlay_form"):
    asserter_layers = render_layers(asserter_schema)
    submit_disabled = l0_file is None or header_error is not None or overlay_depth is None
    submitted = st.form_submit_button("Apply Overlays", disabled=submit_disabled)

if submitted:
    if not l0_file:
        st.error("Please upload a General QR PNG first.")
    elif header_error:
        st.error(f"Failed to read header from QR: {header_error}")
    elif overlay_depth is None:
        st.error("Select an overlay depth after uploading a QR.")
    else:
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                tmp.write(l0_file.getvalue())
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
                    f"Requested depth {overlay_depth} exceeds issuer allowance ({asserter_max_depth})."
                )

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

            output_img = append_overlay_to_existing_qr(
                image_path=tmp_path,
                bitstream=secret_bitstream,
                module_size=header.get("module_size", MODULE_SIZE),
                depth=overlay_depth,
                start_tile=tile_start,
            )
            output_dir = "QRcodes"
            os.makedirs(output_dir, exist_ok=True)
            base_name = os.path.splitext(l0_file.name)[0]
            if base_name.startswith("asserter_"):
                out_name = f"{base_name}.png"
            else:
                out_name = f"asserter_{base_name}.png"
            out_path = os.path.join(output_dir, out_name)
            output_img.save(out_path)
            st.success(f"Overlay image saved as `{out_path}`")
            st.image(output_img, caption="QR with overlays", use_container_width=False)
        except Exception as e:
            st.error(f"Failed to apply overlays: {e}")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)
