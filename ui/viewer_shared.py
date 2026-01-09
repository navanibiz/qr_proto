import re
import os
import sys
import tempfile
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import MODULE_SIZE, MODULE_SIZE_RECURSIVE_CANDIDATES
from c2pa_integration import is_c2pa_available, verify_png_with_c2pa
from main import main, decode_asserter_overlay, extract_header_from_qr


def render_event_sections(event_data: dict) -> None:
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
        st.markdown(f"""
        <div style="background-color:{bg_color}; color:{text_color}; padding:8px 12px; border-radius:6px; margin-top:20px; margin-bottom:10px; font-size:18px; font-weight:bold;">
            {title}
        </div>
        """, unsafe_allow_html=True)

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
    if "vip" in event_data and event_data.get("vip"):
        render_section("VIP Information", event_data["vip"])
    if "staff" in event_data and event_data.get("staff"):
        render_section("Staff Information", event_data["staff"])
    if "asserter" in event_data and event_data.get("asserter"):
        render_section("Asserter Information", event_data["asserter"])

    if "notice" in event_data:
        st.info(event_data["notice"])


def _detect_asserter_overlay(image_bytes: bytes) -> str:
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(image_bytes)
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
            return "Unknown"
        decoded = decode_asserter_overlay(tmp_path, header, header_end_tile)
        return "Present" if decoded and decoded.get("sections", {}).get("ASSERTER") else "Absent"
    except Exception:
        return "Unknown"
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def _detect_signed_metadata(image_bytes: bytes, trust_store_dir: str) -> tuple[str, dict | None]:
    if not is_c2pa_available():
        return "Unknown", None
    try:
        result = verify_png_with_c2pa(image_bytes, trust_store_dir=trust_store_dir)
        manifest_present = result.get("manifest_present")
        if manifest_present is True:
            return "Present", result
        if manifest_present is False:
            return "Absent", result
    except Exception:
        return "Unknown", None
    return "Unknown", None


def render_viewer(
    role_options: list[str],
    default_role: str,
    button_label: str,
    description: str | None = None,
    show_role_select: bool = True,
    show_presence_checks: bool = False,
    presence_title: str = "Attester Signals",
    trust_store_dir: str = "c2pa_integration/trust_store",
) -> None:
    if description:
        st.markdown(description)

    img_file = st.file_uploader("📤 Upload your event QR code", type=["png", "jpg", "jpeg"])
    if img_file:
        st.image(img_file, caption="Uploaded QR Code", use_container_width=False)
        image_bytes = img_file.getvalue()

        if show_presence_checks:
            overlay_status = _detect_asserter_overlay(image_bytes)
            signed_status, signed_result = _detect_signed_metadata(image_bytes, trust_store_dir)
            st.subheader(presence_title)
            st.markdown(f"- Attester overlay detected: **{overlay_status}**")
            st.markdown(f"- Signed metadata (C2PA) present: **{signed_status}**")
            if signed_status == "Present" and signed_result:
                st.subheader("Signed Metadata (C2PA)")
                summary_rows = [
                    {"Field": "Status", "Value": signed_result.get("status", "unknown")},
                    {"Field": "Manifest Present", "Value": signed_result.get("manifest_present", "unknown")},
                    {"Field": "Validation State", "Value": signed_result.get("validation_state", "unknown")},
                    {"Field": "Assertions", "Value": ", ".join(signed_result.get("assertions", []))},
                ]
                st.table(summary_rows)
                with st.expander("Show Raw JSON"):
                    st.json(signed_result)

        if show_role_select:
            role = st.selectbox("Select your role", role_options, index=role_options.index(default_role))
        else:
            role = default_role
            st.caption(f"Viewing as: {default_role}")

        if st.button(button_label):
            with st.spinner("Decoding..."):
                result = main(role.lower(), image_bytes)

            st.success("✅ Done!")
            render_event_sections(result)

            with st.expander("📦 Show Raw JSON"):
                st.json(result)
