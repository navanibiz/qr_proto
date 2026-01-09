import json
import os
import sys
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from ui.style import inject_style, page_title, render_sidebar_nav
from ui.schema_form import load_schema

SCHEMA_PATH = "schema/issuer_schema.json"

st.set_page_config(page_title="Issuer Schema", layout="centered")
inject_style()
render_sidebar_nav()
page_title("Issuer Schema")
st.caption("Edit the issuer schema to control field labels, defaults, and layer structure.")

schema = load_schema(SCHEMA_PATH)
schema_text = st.text_area(
    "Schema JSON",
    value=json.dumps(schema, indent=2),
    height=420,
)

if st.button("Save Issuer Schema"):
    try:
        parsed = json.loads(schema_text)
        with open(SCHEMA_PATH, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2)
        st.success("Issuer schema saved.")
    except json.JSONDecodeError as exc:
        st.error(f"Invalid JSON: {exc}")
