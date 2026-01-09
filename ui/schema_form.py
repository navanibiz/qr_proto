import json
from typing import Dict, Any

import streamlit as st


def load_schema(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def render_event_fields(schema: Dict[str, Any]) -> Dict[str, Any]:
    values = {}
    for field in schema.get("event_fields", []):
        if field["type"] == "text":
            values[field["id"]] = st.text_input(field["label"], field.get("default", ""))
    return values


def render_layer_section(section: Dict[str, Any]) -> Dict[str, Any]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader(section["title"])
    values = {}
    for field in section.get("fields", []):
        f_id = field["id"]
        label = field["label"]
        f_type = field["type"]
        default = field.get("default", "")
        description = field.get("description")
        if f_type == "text":
            values[f_id] = st.text_input(label, default)
        elif f_type == "multiline":
            values[f_id] = st.text_area(label, default)
        elif f_type == "bool":
            values[f_id] = st.checkbox(label, bool(default))
        if description:
            st.caption(description)
    st.markdown("</div>", unsafe_allow_html=True)

    # Normalize multiline lists
    for field in section.get("fields", []):
        if field["type"] == "multiline":
            raw = values.get(field["id"], "")
            values[field["id"]] = [line.strip() for line in raw.splitlines() if line.strip()]
    # Optional key paths (MVP local paths).
    if section.get("keys"):
        with st.expander("Key paths (MVP local)", expanded=False):
            keys = section["keys"]
            values["_keys"] = {
                "public_key": st.text_input(
                    "Public key path",
                    keys.get("public_key", ""),
                    key=f"{section['id']}_pub_key",
                ),
                "private_key": st.text_input(
                    "Private key path",
                    keys.get("private_key", ""),
                    key=f"{section['id']}_priv_key",
                ),
            }
    return values


def build_event_dict(event_fields: Dict[str, Any], sections: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    event_dict = {
        "event_id": event_fields["event_id"],
        "name": event_fields["name"],
        "location": event_fields["location"],
        "start_time": event_fields["start_time"],
        "end_time": event_fields["end_time"],
    }
    for target, data in sections.items():
        event_dict[target] = data
    return event_dict


def render_layers(schema: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    sections = {}
    for layer in schema.get("layers", []):
        sections[layer["target"]] = render_layer_section(layer)
    return sections
