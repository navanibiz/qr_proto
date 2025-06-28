import streamlit as st
from PIL import Image
import io
import re
from main import main  # imports decode_with_role via main(role, img_bytes)

st.set_page_config(page_title="Fractal QR Scanner", layout="centered")
st.title("📷 Fractal QR Code Scanner")

def format_label(key: str) -> str:
    return re.sub(r"[_\-]+", " ", key).capitalize()

def render_section(title: str, data: dict):
    st.markdown(f"### {title}")
    for key, value in data.items():
        label = format_label(key)
        if isinstance(value, list):
            st.markdown(f"**{label}:**")
            st.markdown("<br>".join(f"• {item}" for item in value), unsafe_allow_html=True)
        else:
            st.markdown(f"**{label}:** {value}")

def render_event_sections(event_data: dict):
    general = event_data.get("general", {})

    st.markdown("### 🪪 Event Overview")

    event_id = general.get("event_id", "")
    name = general.get("name", "")
    location = general.get("location", "–")
    start = general.get("start_time", "").split("T")[0]
    end = general.get("end_time", "").split("T")[0]

    st.markdown(f"""
        <div style="background-color:#1e3d59; color:white; padding:10px; border-radius:8px; margin-bottom:10px;">
            <div style="font-size:22px;"><strong>{name}</strong></div>
            <div style="text-align:right; font-size:14px; color:#d1d1d1;">{event_id}</div>
        </div>
        <div style="margin-bottom:10px;">
            <strong>📍 Venue:</strong> {location}  
            &nbsp;&nbsp;&nbsp;&nbsp;
            <strong>📅 Dates:</strong> {start} – {end}
        </div>
        """, unsafe_allow_html=True)


    # Render known nested sections
    if "public_data" in general:
        render_section("General Information", general["public_data"])

    for section_key in ("vip", "staff"):
        if section_key in event_data:
            render_section(f"{section_key.upper()} Information", event_data[section_key])

# --- UI Input ---
img_file = st.file_uploader("Upload a QR code image", type=["png", "jpg", "jpeg"])
if img_file:
    # 📸 Show uploaded QR code image
    import base64

    # 📸 Show uploaded QR code image (centered, base64, small)
    img_base64 = base64.b64encode(img_file.getvalue()).decode("utf-8")
    st.markdown(
        f"""
        <div style="text-align: center; margin-top: 10px; margin-bottom: 20px;">
            <img src="data:image/png;base64,{img_base64}" style="width: 180px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);" alt="QR Code" />
            <div style="font-size: 14px; color: grey;">Uploaded QR Code</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    role = st.selectbox("Select your role", ["General", "VIP", "Staff", "Admin"])
    if st.button("🔍 Decode and Show Data"):
        with st.spinner("Decoding..."):
            image_bytes = img_file.getvalue()
            result = main(role.lower(), image_bytes)
        st.success("✅ Done!")
        render_event_sections(result)
        with st.expander("📦 Show Raw JSON"):
            st.json(result)
