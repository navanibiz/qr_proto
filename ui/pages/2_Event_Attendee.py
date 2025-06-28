import streamlit as st
from PIL import Image
import io
import re
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from main import main  # This should import decode_with_role via main(role, img_bytes)

st.set_page_config(page_title="Event Attendee QR Scanner", layout="centered")
st.title("🎟️ Event Attendee – QR Code Scanner")

def render_event_sections(event_data: dict):
    general = event_data.get("general", {})
    st.markdown("### 🪪 Event Overview")

    event_id = general.get("event_id", "")
    name = general.get("name", "")
    location = general.get("location", "")
    start = general.get("start_time", "").split("T")[0]
    end = general.get("end_time", "").split("T")[0]

    st.markdown(f"""
    <div style="background-color:#1e3d59; color:white; padding:10px; border-radius:8px; margin-bottom:10px;">
        <div style="font-size:22px;"><strong>{name}</strong></div>
        <div style="font-size:14px; text-align:right;">{event_id}</div>
    </div>
    <div style="margin-bottom:10px;">
        <strong>📍 Venue:</strong> {location}  
        &nbsp;&nbsp;&nbsp;&nbsp;
        <strong>📅 Dates:</strong> {start} – {end}
    </div>
    """, unsafe_allow_html=True)

    def render_section(title: str, data: dict, bg_color="#f0f0f0", text_color="#000000"):
        # Header
        st.markdown(f"""
        <div style="background-color:{bg_color}; color:{text_color}; padding:8px 12px; border-radius:6px; margin-top:20px; margin-bottom:10px; font-size:18px; font-weight:bold;">
            {title}
        </div>
        """, unsafe_allow_html=True)

        # Build the full content block as HTML
        content_html = """
        <div style="
            background-color: #ffffff;
            border-left: 5px solid #1e3d59;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            padding: 16px 24px;
            margin: 10px 0 30px 0;
            border-radius: 6px;
            line-height: 1.6;
        ">
        """

        for key, val in data.items():
            label = re.sub(r"_", " ", key).capitalize()
            if isinstance(val, list):
                content_html += f"<p><strong>{label}:</strong><br>"
                content_html += "<br>".join(f"• {item}" for item in val)
                content_html += "</p>"
            else:
                content_html += f"<p><strong>{label}:</strong> {val}</p>"

        content_html += "</div>"
        st.markdown(content_html, unsafe_allow_html=True)




    if "public_data" in general:
        render_section("General Information", general["public_data"])
    if "vip" in event_data:
        render_section("VIP Information", event_data["vip"])
    if "staff" in event_data:
        render_section("Staff Information", event_data["staff"])


img_file = st.file_uploader("📤 Upload your event QR code", type=["png", "jpg", "jpeg"])
if img_file:
    st.image(img_file, caption="Uploaded QR Code", use_container_width=False)

    role = st.selectbox("Select your role", ["General", "VIP", "Staff", "Admin"])

    if st.button("🔍 Decode and Show My Event Info"):
        with st.spinner("Decoding..."):
            image_bytes = img_file.getvalue()
            result = main(role.lower(), image_bytes)

        st.success("✅ Done!")
        render_event_sections(result)
        with st.expander("📦 Show Raw JSON"):
            st.json(result)
