import json
import os
import sys
import streamlit as st
from PIL import Image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from main import encode_from_dict
from ui.schema_form import load_schema, render_event_fields, render_layers, build_event_dict
from ui.style import inject_style, page_title, render_sidebar_nav

st.set_page_config(page_title="Issuance — General QR", layout="centered")
inject_style()
render_sidebar_nav()
page_title("Issuance — General QR")
st.markdown("Create a **public-only** QR with just the General section.")
st.caption("If an asserter needs more capacity or depth later, reissue this QR with updated reserves.")

issuer_schema = load_schema("schema/issuer_schema.json")
asserter_reserve = issuer_schema.get("asserter_reserve", {})
asserter_max_depth = asserter_reserve.get("max_depth")
reserve_bits = asserter_reserve.get("reserve_bits", 0)

with st.form("general_form"):
    event_fields = render_event_fields(issuer_schema)
    issuer_sections = render_layers({"layers": [issuer_schema["layers"][0]]})
    default_name = f"qr_{event_fields['event_id'].replace(' ', '_')}.png"
    filename = st.text_input("Base file name", default_name)
    submitted = st.form_submit_button("Save General QR")

if submitted:
    event_dict = build_event_dict(event_fields, issuer_sections)
    filename = filename or f"qr_{event_fields['event_id'].replace(' ', '_')}.png"
    output_dir = "QRcodes"
    os.makedirs(output_dir, exist_ok=True)
    stem, _ = os.path.splitext(filename)
    if stem.startswith("general_"):
        output_name = f"{stem}.png"
    else:
        output_name = f"general_{stem}.png"
    output_path = os.path.join(output_dir, output_name)
    try:
        metadata = encode_from_dict(
            event_dict,
            output_path,
            dimension=1,
            return_metadata=True,
            reserve_bits=reserve_bits,
            asserter_max_depth=asserter_max_depth,
        )
        st.session_state["last_qr_metadata"] = metadata
        st.success(f"General QR saved as `{output_path}`")
        st.image(Image.open(output_path), caption="General QR", use_container_width=False)
    except Exception as e:
        st.error(f"Failed to generate General QR: {e}")
