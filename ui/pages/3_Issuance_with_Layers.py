import io
import os
import sys
import streamlit as st
from PIL import Image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from main import encode_from_dict
from ui.schema_form import load_schema, render_event_fields, render_layers, build_event_dict
from ui.style import inject_style, page_title, render_sidebar_nav

st.set_page_config(page_title="Issuance with Layers", layout="centered")
inject_style()
render_sidebar_nav()
page_title("Issuance with Layers")
st.markdown("Create **General QR + issuer layers** in a single step.")

issuer_schema = load_schema("schema/issuer_schema.json")
asserter_reserve = issuer_schema.get("asserter_reserve", {})
asserter_max_depth = asserter_reserve.get("max_depth")
reserve_bits = asserter_reserve.get("reserve_bits", 0)

with st.form("full_form"):
    event_fields = render_event_fields(issuer_schema)
    issuer_layers = render_layers(issuer_schema)

    depth = st.slider("Overlay Depth", min_value=1, max_value=3, value=1)
    default_name = f"qr_{event_fields['event_id'].replace(' ', '_')}.png"
    filename = st.text_input("Base file name", default_name)
    submitted = st.form_submit_button("Save QR (General + Issuer Layers)")

if submitted:
    sections = {}
    sections.update(issuer_layers)
    event_dict = build_event_dict(event_fields, sections)
    filename = filename or f"qr_{event_fields['event_id'].replace(' ', '_')}.png"
    output_dir = "QRcodes"
    os.makedirs(output_dir, exist_ok=True)
    stem, _ = os.path.splitext(filename)
    if stem.startswith("issuer_"):
        output_name = f"{stem}.png"
    else:
        output_name = f"issuer_{stem}.png"
    output_path = os.path.join(output_dir, output_name)
    try:
        metadata = encode_from_dict(
            event_dict,
            output_path,
            dimension=depth,
            return_metadata=True,
            reserve_bits=reserve_bits,
            asserter_max_depth=asserter_max_depth,
        )
        st.session_state["last_qr_metadata"] = metadata
        st.success(f"QR code generated and saved as `{output_path}`")
        st.image(Image.open(output_path), caption="Generated QR", use_container_width=False)
    except Exception as e:
        st.error(f"Failed to generate QR: {e}")
