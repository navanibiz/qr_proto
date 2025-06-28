import streamlit as st

def render_event_sections(title, data_dict):
    st.markdown(f"### {title}")
    for key, value in data_dict.items():
        label = key.replace("_", " ").capitalize()
        if isinstance(value, list):
            st.markdown(f"**{label}:**")
            for item in value:
                st.markdown(f"- {item}")
        else:
            st.markdown(f"**{label}:** {value}")
