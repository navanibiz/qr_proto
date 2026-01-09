import json
import os
import sys
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from ui.style import inject_style, page_title, render_sidebar_nav
from ui.schema_form import load_schema

SCHEMA_PATH = "schema/asserter_schema.json"

st.set_page_config(page_title="Attester Schema", layout="centered")
inject_style()
render_sidebar_nav()
page_title("Attester Schema")
st.caption("Edit the attester schema to control overlay fields and defaults.")

schema = load_schema(SCHEMA_PATH)
schema_text = st.text_area(
    "Schema JSON",
    value=json.dumps(schema, indent=2),
    height=420,
)

if st.button("Save Attester Schema"):
    try:
        parsed = json.loads(schema_text)
        with open(SCHEMA_PATH, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2)
        st.success("Attester schema saved.")
    except json.JSONDecodeError as exc:
        st.error(f"Invalid JSON: {exc}")
