import streamlit as st
import json
import sys
import os
import traceback
# Add the project root (qr_proto) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from main import encode_from_dict  # Use the central encoding logic
from PIL import Image

st.set_page_config(page_title="Event QR Creator", layout="centered")
st.title("🛠️ Event Coordinator – QR Code Generator")

st.markdown("Fill in the event details below to generate a QR code.")

with st.form("event_form"):
    # Basic event metadata
    event_id = st.text_input("Event ID", "EVT-2025-001")
    name = st.text_input("Event Name", "FutureTech Expo 2025")
    location = st.text_input("Location", "Convention Center, San Francisco")
    start_time = st.text_input("Start Time (ISO format)", "2025-09-12T09:00:00Z")
    end_time = st.text_input("End Time (ISO format)", "2025-09-12T18:00:00Z")

    # Public section
    st.subheader("📣 Public Data")
    agenda = st.text_input("Agenda Summary", "Talks on AI, IoT, and Sustainable Tech")
    dress = st.text_input("Dress Code", "Smart Casual")
    guidelines = st.text_area("General Guidelines (one per line)", "Carry a valid photo ID\nNo outside food allowed\nArrive 15 minutes early")

    # VIP section
    st.subheader("🔒 VIP Data")
    vip_location = st.text_input("VIP Lounge Location", "2nd Floor, Sapphire Lounge")
    vip_contact = st.text_input("VIP Contact", "vip@futuretech.com")
    vip_sessions = st.text_area("Exclusive Sessions (one per line)", "AI Founders Roundtable\nPrivate Tour with CTO")

    # Staff section
    st.subheader("🛡️ Staff Data")
    staff_briefing = st.text_area("Internal Briefing", "Ensure secure entry checkpoints are staffed by 08:30AM.")
    staff_codes = st.text_area("Security Codes (one per line)", "SEC-ALPHA-2025\nSEC-BETA-2025")
    background_check = st.checkbox("Requires Background Check", True)
    dimension = st.slider("Fractal Recursion Depth", min_value=1, max_value=3, value=1, help="Higher depth = more data per tile")

    submitted = st.form_submit_button("Generate QR Code")

if submitted:
    # Construct the JSON object
    event_dict = {
        "event_id": event_id,
        "name": name,
        "location": location,
        "start_time": start_time,
        "end_time": end_time,
        "public_data": {
            "agenda_summary": agenda,
            "dress_code": dress,
            "general_guidelines": [line.strip() for line in guidelines.splitlines() if line.strip()]
        },
        "vip_data": {
            "vip_lounge_location": vip_location,
            "vip_contact": vip_contact,
            "exclusive_sessions": [line.strip() for line in vip_sessions.splitlines() if line.strip()]
        },
        "staff_data": {
            "internal_briefing": staff_briefing,
            "security_codes": [line.strip() for line in staff_codes.splitlines() if line.strip()],
            "requires_background_check": background_check
        }
    }

    st.subheader("📄 Preview JSON Payload")
    st.json(event_dict)

    # Save using the same backend logic
    filename = f"qr_{event_id.replace(' ', '_')}.png"
    try:
        encode_from_dict(event_dict, filename, dimension=dimension)
        st.success(f"QR code generated and saved as `{filename}`")
        st.image(Image.open(filename), caption="Generated Fractal QR", use_container_width=False)
    except Exception as e:
        st.error(f"Failed to generate QR: {e}")
        st.code(traceback.format_exc(), language="python")
