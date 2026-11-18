"""
app/main.py
Giao diện workspace chính (CKPA-38) của CRM Knowledge and Policy Assistant.
Tuân thủ:
  - CKPA-38: Workspace giao diện làm việc chính
  - CKPA-39: Trích dẫn nguyên văn, phân biệt với giải thích AI
  - CKPA-40: 7 field cố định
  - CKPA-45: Referral cục bộ (qua referral_service)
  - CKPA-46: Feedback 5 nhóm (qua feedback_service)
  - CKPA-47: HOLD và Fail Visibly
  - KNW 01: Hiển thị câu hỏi cùng kết quả
  - KNW 02: Banner chỉ dùng nội bộ
  - ANS 08: Chống Prompt Injection (qua input_guard trong pipeline)

Quy tắc kiến trúc tầng UI:
  - TUYỆT ĐỐI KHÔNG import sqlite3, llm_client, evidence_provider hoặc database
    ở bất kỳ cấp độ nào (kể cả trong hàm hoặc khối điều kiện).
  - Mọi thao tác đều ủy thác qua các hàm dịch vụ trong app/services.
  - KHÔNG streaming: hiển thị kết quả chỉ sau khi pipeline hoàn tất.
  - KHÔNG hiển thị traceback ra màn hình người dùng.
  - DEMO_MODE=1: hiển thị banner cảnh báo dữ liệu giả lập.
"""

import os
import sys
from pathlib import Path

# Đảm bảo đường dẫn gốc dự án luôn được nhận diện
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

from app import config
from app.services.system_service import init_system, check_system_health, create_policy_service
from app.components.policy_display import render_policy_response
from app.components.feedback_form import render_feedback_form
from app.components.referral_modal import render_referral_form

# ---------------------------------------------------------------------------
# 1. Cấu hình trang
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="CRM Knowledge & Policy Assistant",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# 2. DEMO_MODE và Dark Mode (session_state)
# ---------------------------------------------------------------------------
DEMO_MODE = os.environ.get("DEMO_MODE", "").strip() == "1"

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ---------------------------------------------------------------------------
# 3. CSS Enterprise Banking — Navy Blue, Light / Dark adaptive
# ---------------------------------------------------------------------------
_DARK = st.session_state.dark_mode

# Bảng màu
if _DARK:
    BG_PAGE        = "#0D1B2E"
    BG_CARD        = "#152238"
    BG_CARD2       = "#1C2F45"
    BG_SIDEBAR     = "#0F1E30"
    BORDER         = "#1E3550"
    BORDER_SUBTLE  = "#233D58"
    TEXT_PRIMARY   = "#E8EDF5"
    TEXT_MUTED     = "#7B92AD"
    TEXT_CAPTION   = "#4E6882"
    ACCENT         = "#2E7DD1"
    ACCENT_HOVER   = "#2366B8"
    ACCENT_SUBTLE  = "#1A3A5C"
    BANNER_BG      = "#152C4A"
    BANNER_FG      = "#93C5FD"
    BANNER_BORDER  = "#1E4A7A"
    INPUT_BG       = "#152238"
    INPUT_BORDER   = "#2D4A6A"
    TAG_BG         = "#1A3A5C"
    TAG_FG         = "#7CB9F4"
    SUCCESS_BG     = "#052e16"
    SUCCESS_FG     = "#86efac"
    WARN_BG        = "#231500"
    WARN_FG        = "#FCD34D"
    HOLD_BG        = "#1C1200"
    HOLD_BORDER    = "#B45309"
    SIDEBAR_RULE   = "#1A3250"
else:
    BG_PAGE        = "#F4F7FB"
    BG_CARD        = "#FFFFFF"
    BG_CARD2       = "#EEF3FA"
    BG_SIDEBAR     = "#FAFCFF"
    BORDER         = "#D6E0EE"
    BORDER_SUBTLE  = "#E8EFF8"
    TEXT_PRIMARY   = "#0C1F3A"
    TEXT_MUTED     = "#4A6484"
    TEXT_CAPTION   = "#8FAABB"
    ACCENT         = "#1F5C99"
    ACCENT_HOVER   = "#174F87"
    ACCENT_SUBTLE  = "#EEF5FF"
    BANNER_BG      = "#1F5C99"
    BANNER_FG      = "#FFFFFF"
    BANNER_BORDER  = "#174F87"
    INPUT_BG       = "#FFFFFF"
    INPUT_BORDER   = "#C3D0E4"
    TAG_BG         = "#E8F0FB"
    TAG_FG         = "#1A4A85"
    SUCCESS_BG     = "#F0FDF4"
    SUCCESS_FG     = "#166534"
    WARN_BG        = "#FFFBEB"
    WARN_FG        = "#92400E"
    HOLD_BG        = "#FFFBEB"
    HOLD_BORDER    = "#D97706"
    SIDEBAR_RULE   = "#D6E0EE"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* ── Reset & base ── */
    html, body, [data-testid="stApp"] {{
        background-color: {BG_PAGE} !important;
        color: {TEXT_PRIMARY} !important;
        font-family: 'Inter', 'Segoe UI', system-ui, sans-serif !important;
        -webkit-font-smoothing: antialiased !important;
    }}

    /* ── Main container ── */
    div[data-testid="stMainBlockContainer"], .block-container {{
        max-width: 1100px !important;
        padding: 1.5rem 2.25rem 4rem 2.25rem !important;
        margin: 0 auto !important;
        background-color: {BG_PAGE} !important;
    }}

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {{
        background-color: {BG_SIDEBAR} !important;
        border-right: 1px solid {SIDEBAR_RULE} !important;
    }}
    [data-testid="stSidebar"] * {{
        color: {TEXT_PRIMARY} !important;
    }}
    /* Sidebar scrollbar tinh tế */
    [data-testid="stSidebar"]::-webkit-scrollbar {{
        width: 4px;
    }}
    [data-testid="stSidebar"]::-webkit-scrollbar-track {{
        background: transparent;
    }}
    [data-testid="stSidebar"]::-webkit-scrollbar-thumb {{
        background: {BORDER};
        border-radius: 4px;
    }}

    /* ── Cards / containers ── */
    [data-testid="stVerticalBlockBorderWrapper"] > div {{
        background-color: {BG_CARD} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 10px !important;
        box-shadow: 0 1px 6px rgba(15,34,74,0.06) !important;
        padding: 1rem 1.25rem !important;
    }}

    /* ── Form inputs ── */
    textarea, input[type="text"] {{
        background-color: {INPUT_BG} !important;
        border: 1.5px solid {INPUT_BORDER} !important;
        color: {TEXT_PRIMARY} !important;
        border-radius: 8px !important;
        font-size: 0.95rem !important;
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
    }}
    textarea:focus, input[type="text"]:focus {{
        border-color: {ACCENT} !important;
        box-shadow: 0 0 0 3px {ACCENT}22 !important;
        outline: none !important;
    }}

    /* ── Primary button ── */
    button[kind="primary"], [data-testid="baseButton-primary"] {{
        background-color: {ACCENT} !important;
        border-color: {ACCENT} !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        letter-spacing: 0.03em !important;
        text-transform: uppercase !important;
        transition: background 0.15s ease !important;
        padding: 0.5rem 1.25rem !important;
    }}
    button[kind="primary"]:hover, [data-testid="baseButton-primary"]:hover {{
        background-color: {ACCENT_HOVER} !important;
        border-color: {ACCENT_HOVER} !important;
    }}

    /* ── Secondary button ── */
    button[kind="secondary"], [data-testid="baseButton-secondary"] {{
        background-color: transparent !important;
        border: 1.5px solid {ACCENT} !important;
        color: {ACCENT} !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
    }}

    /* ── Headings ── */
    h1 {{
        font-size: 1.7rem !important;
        font-weight: 800 !important;
        color: {TEXT_PRIMARY} !important;
        letter-spacing: -0.025em !important;
        margin-bottom: 0.2rem !important;
        line-height: 1.25 !important;
    }}
    h2, h3 {{
        font-weight: 700 !important;
        color: {TEXT_PRIMARY} !important;
        letter-spacing: -0.01em !important;
    }}

    /* ── Caption / muted text ── */
    [data-testid="stCaptionContainer"], small, .stCaption {{
        color: {TEXT_MUTED} !important;
        font-size: 0.78rem !important;
    }}

    /* ── Metric / info box ── */
    [data-testid="stMetric"] {{
        background-color: {BG_CARD2} !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        border: 1px solid {BORDER} !important;
    }}

    /* ── Expander ── */
    [data-testid="stExpander"] {{
        border: 1px solid {BORDER} !important;
        border-radius: 8px !important;
        background-color: {BG_CARD} !important;
        margin-bottom: 0.5rem !important;
    }}
    [data-testid="stExpander"] summary {{
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        color: {TEXT_PRIMARY} !important;
        letter-spacing: 0.01em !important;
    }}

    /* ── Status box ── */
    [data-testid="stStatusContainer"] {{
        border-radius: 8px !important;
        border: 1px solid {BORDER} !important;
    }}

    /* ── Divider ── */
    hr {{
        border: none !important;
        border-top: 1px solid {BORDER} !important;
        margin: 1.25rem 0 !important;
    }}

    /* ── Tag / badge ── */
    .crm-tag {{
        display: inline-block;
        background: {TAG_BG};
        color: {TAG_FG};
        border-radius: 4px;
        padding: 2px 9px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin: 2px;
    }}

    /* ── KNW-02 internal banner ── */
    .crm-internal-banner {{
        background: {BANNER_BG};
        color: {BANNER_FG};
        border: 1px solid {BANNER_BORDER};
        padding: 10px 18px;
        border-radius: 8px;
        font-size: 0.83rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: 500;
        letter-spacing: 0.01em;
    }}

    /* ── Question echo card ── */
    .crm-question-card {{
        background: {BG_CARD2};
        border-left: 4px solid {ACCENT};
        border-radius: 0 8px 8px 0;
        padding: 12px 18px;
        margin-bottom: 1rem;
        font-size: 0.95rem;
        color: {TEXT_PRIMARY};
        line-height: 1.6;
    }}

    /* ── Footer ── */
    .crm-footer {{
        text-align: center;
        color: {TEXT_CAPTION};
        font-size: 0.72rem;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid {BORDER};
        letter-spacing: 0.03em;
    }}

    /* ── Sidebar: Safety rule row ── */
    .crm-safety-row {{
        display: flex;
        align-items: flex-start;
        gap: 10px;
        padding: 7px 0;
        border-bottom: 1px solid {SIDEBAR_RULE};
        font-size: 0.82rem;
        color: {TEXT_MUTED};
        line-height: 1.4;
    }}
    .crm-safety-row:last-child {{
        border-bottom: none;
    }}
    .crm-safety-icon {{
        flex-shrink: 0;
        margin-top: 1px;
    }}

    /* ── Sidebar: System meta footer ── */
    .crm-sys-meta {{
        font-size: 0.72rem;
        color: {TEXT_CAPTION};
        line-height: 1.9;
        padding-top: 10px;
        border-top: 1px solid {SIDEBAR_RULE};
    }}
    .crm-sys-meta code {{
        background: {BG_CARD2};
        border: 1px solid {BORDER};
        border-radius: 3px;
        padding: 0 5px;
        font-size: 0.72rem;
        color: {ACCENT};
        font-family: 'Cascadia Code', 'Consolas', monospace;
    }}

    /* ── Shortcut table in sidebar ── */
    .crm-kb-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 5px 0;
        border-bottom: 1px solid {SIDEBAR_RULE};
        font-size: 0.8rem;
    }}
    .crm-kb-key {{
        background: {BG_CARD2};
        border: 1px solid {BORDER};
        border-radius: 4px;
        padding: 1px 7px;
        font-family: 'Cascadia Code', 'Consolas', monospace;
        font-size: 0.75rem;
        color: {ACCENT};
    }}

    /* ── Sidebar section header ── */
    .crm-sidebar-section {{
        font-size: 0.65rem;
        font-weight: 800;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: {TEXT_CAPTION};
        padding: 12px 0 7px 0;
        display: flex;
        align-items: center;
        gap: 7px;
    }}

    /* Hide default streamlit footer ── */
    footer {{ visibility: hidden !important; }}

    /* ── Stray markdown paragraph spacing ── */
    [data-testid="stMarkdownContainer"] p {{
        margin-bottom: 0.5rem !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# 4. Khởi tạo dịch vụ hệ thống
# ---------------------------------------------------------------------------
init_system()
db_ok = check_system_health()


def get_current_user_context():
    """
    Trả về ngữ cảnh người dùng tối thiểu.
    LƯU Ý TẠM THỜI: Quyền hạn được gán cố định ở đây trong giai đoạn phát triển.
    Cần tích hợp SSO/IAM thực tế khi triển khai sản xuất (xem docs/OPEN_QUESTIONS.md).
    """
    return {"roles": ["CRM_STAFF"]}


if "policy_service" not in st.session_state:
    st.session_state.policy_service = create_policy_service(demo_mode=DEMO_MODE)

if "last_response" not in st.session_state:
    st.session_state.last_response = None

if "last_question" not in st.session_state:
    st.session_state.last_question = ""

# ---------------------------------------------------------------------------
# 5. Sidebar — Enterprise Banking layout
# ---------------------------------------------------------------------------

# SVG icons an ninh cho sidebar
_SB_SHIELD = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M12 2L4 7v5c0 5.25 3.4 10.15 8 11.35C17.6 22.15 21 17.25 21 12V7l-8-5z" fill="{c}"/></svg>'
_SB_LOCK   = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none"><rect x="5" y="11" width="14" height="10" rx="2" stroke="{c}" stroke-width="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4" stroke="{c}" stroke-width="2" stroke-linecap="round"/></svg>'
_SB_SCALE  = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M12 3v18M5 8l7-5 7 5" stroke="{c}" stroke-width="2" stroke-linecap="round"/><path d="M3 12l4 6H3M21 12l-4 6h4" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
_SB_PAUSE  = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none"><rect x="6" y="4" width="4" height="16" rx="2" fill="{c}"/><rect x="14" y="4" width="4" height="16" rx="2" fill="{c}"/></svg>'
_SB_BAN    = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="9" stroke="{c}" stroke-width="2"/><path d="M5.6 5.6l12.8 12.8" stroke="{c}" stroke-width="2" stroke-linecap="round"/></svg>'
_SB_DOC    = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2M9 5a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2M9 5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2" stroke="{c}" stroke-width="1.8" stroke-linecap="round"/></svg>'

def _sb_icon(svg_tpl: str, color: str) -> str:
    return svg_tpl.replace("{c}", color)

with st.sidebar:

    # ── Logo + Phiên bản + Dark Mode ──
    col_logo, col_toggle = st.columns([4, 1])
    with col_logo:
        st.markdown(
            f"""<div style="display:flex;align-items:center;gap:9px;padding:4px 0 2px 0">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
                    <rect width="24" height="24" rx="6" fill="{ACCENT}"/>
                    <path d="M4 12h16M12 4l8 8-8 8" stroke="white" stroke-width="2.5"
                          stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <div>
                    <div style="font-size:0.88rem;font-weight:800;color:{TEXT_PRIMARY};
                                letter-spacing:-0.01em;line-height:1.1">CRM Assistant</div>
                    <div style="font-size:0.68rem;color:{TEXT_CAPTION};letter-spacing:0.04em">
                        v{config.CONFIG_VERSION} &nbsp;·&nbsp; Nội bộ
                    </div>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col_toggle:
        st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
        dark_btn_label = "☀" if _DARK else "◑"
        if st.button(dark_btn_label, key="toggle_dark", help="Chuyển Light / Dark mode"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

    st.divider()

    # ── Trạng thái hệ thống ──
    st.markdown(
        f"""<div class="crm-sidebar-section">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="9" stroke="{TEXT_CAPTION}" stroke-width="2"/>
                <path d="M12 7v5l3 3" stroke="{TEXT_CAPTION}" stroke-width="2"
                      stroke-linecap="round"/>
            </svg>
            Trạng thái hệ thống
        </div>""",
        unsafe_allow_html=True,
    )

    if db_ok:
        st.markdown(
            f"""<div style="display:flex;align-items:center;gap:8px;padding:7px 10px;
                           background:{SUCCESS_BG};border:1px solid #BBF7D0;
                           border-radius:7px;margin-bottom:6px">
                <div style="width:8px;height:8px;border-radius:50%;
                            background:#22C55E;flex-shrink:0"></div>
                <div style="font-size:0.8rem;color:{SUCCESS_FG};font-weight:600">
                    Cơ sở dữ liệu: Sẵn sàng
                </div>
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""<div style="display:flex;align-items:center;gap:8px;padding:7px 10px;
                           background:#FFF1F2;border:1px solid #FECACA;
                           border-radius:7px;margin-bottom:6px">
                <div style="width:8px;height:8px;border-radius:50%;
                            background:#EF4444;flex-shrink:0"></div>
                <div style="font-size:0.8rem;color:#991B1B;font-weight:600">
                    Cơ sở dữ liệu: Lỗi kết nối
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

    if DEMO_MODE:
        st.markdown(
            f"""<div style="display:flex;align-items:center;gap:8px;padding:7px 10px;
                           background:{WARN_BG};border:1px solid #FDE68A;
                           border-radius:7px">
                <div style="width:8px;height:8px;border-radius:50%;
                            background:#F59E0B;flex-shrink:0"></div>
                <div style="font-size:0.8rem;color:{WARN_FG};font-weight:600">
                    DEMO MODE đang bật
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Nguyên tắc kiểm soát an toàn (SVG icons, không dùng emoji) ──
    st.markdown(
        f"""<div class="crm-sidebar-section">
            {_sb_icon(_SB_SHIELD, TEXT_CAPTION)}
            Nguyên tắc kiểm soát an toàn
        </div>""",
        unsafe_allow_html=True,
    )

    safety_rules = [
        (_sb_icon(_SB_BAN,    TEXT_MUTED), "Không tự suy diễn ngoại lệ chính sách"),
        (_sb_icon(_SB_DOC,    TEXT_MUTED), "Phải có văn bản dẫn chiếu trước khi trả lời"),
        (_sb_icon(_SB_PAUSE,  TEXT_MUTED), "Kích hoạt HOLD khi thiếu căn cứ xác thực"),
        (_sb_icon(_SB_SCALE,  TEXT_MUTED), "Không tư vấn hoặc giải thích pháp lý"),
        (_sb_icon(_SB_LOCK,   TEXT_MUTED), "Không cam kết hay hứa hẹn với khách hàng"),
    ]
    for icon_svg, rule in safety_rules:
        st.markdown(
            f"""<div class="crm-safety-row">
                <div class="crm-safety-icon">{icon_svg}</div>
                <div>{rule}</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Hướng dẫn sử dụng ──
    with st.expander("Hướng dẫn sử dụng", expanded=False):
        st.markdown(
            f"""<div style="font-size:0.81rem;line-height:1.7;color:{TEXT_PRIMARY}">
<strong style="font-size:0.72rem;letter-spacing:0.08em;text-transform:uppercase;
color:{TEXT_MUTED}">Bước 1 — Nhập câu hỏi</strong><br>
Mô tả tình huống khách hàng bằng tiếng Việt. Không cần dùng mã điều khoản.<br><br>

<strong style="font-size:0.72rem;letter-spacing:0.08em;text-transform:uppercase;
color:{TEXT_MUTED}">Bước 2 — Tra cứu</strong><br>
Nhấn <strong>Tra cứu chính sách</strong>. Hệ thống kiểm tra đầu vào, lấy bằng chứng
và xác minh trước khi trả lời.<br><br>

<strong style="font-size:0.72rem;letter-spacing:0.08em;text-transform:uppercase;
color:{TEXT_MUTED}">Bước 3 — Đọc kết quả</strong><br>
· <strong>Trích dẫn nguyên văn</strong> = văn bản gốc, không chỉnh sửa<br>
· <strong>Giải thích AI</strong> = diễn giải, cần kiểm tra lại<br>
· <strong>HOLD</strong> = thiếu căn cứ, không tự suy diễn<br><br>

<strong style="font-size:0.72rem;letter-spacing:0.08em;text-transform:uppercase;
color:{TEXT_MUTED}">Bước 4 — Phản hồi / Chuyển tuyến</strong><br>
Dùng Feedback để cải thiện hệ thống. Dùng Referral khi cần chuyển tuyến chính sách.
</div>""",
            unsafe_allow_html=True,
        )

    # ── Phím tắt ──
    with st.expander("Phím tắt thao tác", expanded=False):
        shortcuts = [
            ("Ctrl + Enter", "Gửi câu hỏi"),
            ("Ctrl + R",     "Tải lại trang"),
            ("Tab",          "Chuyển trường"),
            ("Esc",          "Đóng modal"),
        ]
        for key, desc in shortcuts:
            st.markdown(
                f"""<div class="crm-kb-row">
                    <span style="color:{TEXT_MUTED}">{desc}</span>
                    <kbd class="crm-kb-key">{key}</kbd>
                </div>""",
                unsafe_allow_html=True,
            )

    # ── Thông số kỹ thuật — thu gọn ở chân sidebar ──
    st.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)
    # Spacer
    for _ in range(2):
        st.markdown("", unsafe_allow_html=True)

    st.markdown(
        f"""<div class="crm-sys-meta">
            <div style="display:flex;justify-content:space-between;margin-bottom:2px">
                <span>Config</span>
                <code>{config.CONFIG_VERSION}</code>
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:2px">
                <span>Prompt</span>
                <code>{config.PROMPT_VERSION}</code>
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:2px">
                <span>Max in</span>
                <code>{config.MAX_INPUT_TOKENS} tok</code>
            </div>
            <div style="display:flex;justify-content:space-between">
                <span>Max out</span>
                <code>{config.MAX_OUTPUT_TOKENS} tok</code>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# 6. KNW-02 Banner — Chỉ dùng nội bộ
# ---------------------------------------------------------------------------
_SVG_LOCK_BANNER = (
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none">'
    '<rect x="5" y="11" width="14" height="10" rx="2" fill="white" fill-opacity="0.9"/>'
    '<path d="M8 11V7a4 4 0 0 1 8 0v4" stroke="white" stroke-width="2.2"'
    ' stroke-linecap="round"/>'
    '</svg>'
)
st.markdown(
    f"""
    <div class="crm-internal-banner">
        {_SVG_LOCK_BANNER}
        <div>
            <strong>CHỈ DÙNG NỘI BỘ</strong>
            &nbsp;—&nbsp;
            Thông tin tra cứu chỉ phục vụ nhân viên CRM trong quá trình tư vấn.
            Không xuất hoặc gửi nội dung này cho khách hàng.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Banner DEMO_MODE
if DEMO_MODE:
    st.error(
        "⚠️ **DỮ LIỆU GIẢ LẬP CHỈ ĐỂ KIỂM THỬ** — "
        "Mọi thông tin hiển thị là giả lập, không phản ánh chính sách thực.",
        icon="🧪",
    )

# ---------------------------------------------------------------------------
# 7. Tiêu đề trang
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div style="margin-bottom:0.5rem">
        <div style="font-size:0.68rem;font-weight:800;letter-spacing:0.14em;
                    text-transform:uppercase;color:{TEXT_MUTED};margin-bottom:4px">
            Hệ thống nội bộ &nbsp;·&nbsp; AI-06
        </div>
        <h1 style="margin-bottom:0;line-height:1.2">
            CRM Knowledge &amp; Policy Assistant
        </h1>
        <p style="color:{TEXT_MUTED};font-size:0.88rem;margin-top:6px;line-height:1.5">
            Hệ thống tra cứu, đối chiếu và giải thích chính sách ngân hàng
            dành riêng cho nhân viên CRM &nbsp;·&nbsp; Có căn cứ văn bản xác thực
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ---------------------------------------------------------------------------
# 8. Khu vực nhập câu hỏi (CKPA-38)
# ---------------------------------------------------------------------------
MAX_CHARS = config.MAX_QUESTION_CHARS

st.markdown(
    f"""<div style="font-size:0.68rem;font-weight:800;letter-spacing:0.12em;
                   text-transform:uppercase;color:{TEXT_MUTED};margin-bottom:6px">
        Tra cứu chính sách
    </div>
    <div style="font-size:1.0rem;font-weight:700;color:{TEXT_PRIMARY};margin-bottom:12px">
        Nhập câu hỏi hoặc tình huống cần tra cứu
    </div>""",
    unsafe_allow_html=True,
)

with st.form(key="question_form", clear_on_submit=False):
    user_question = st.text_area(
        label="Câu hỏi hoặc tình huống khách hàng:",
        placeholder=(
            "Ví dụ: Khách hàng cá nhân mở tài khoản trực tuyến (eKYC) "
            "thì hạn mức giao dịch một ngày là bao nhiêu?"
        ),
        height=130,
        max_chars=MAX_CHARS,
        help=f"Tối đa {MAX_CHARS} ký tự. Không nhập thông tin cá nhân khách hàng.",
        label_visibility="collapsed",
    )

    col_note, col_btn = st.columns([3, 1])
    with col_note:
        st.markdown(
            f"""<div style="font-size:0.76rem;color:{TEXT_MUTED};padding-top:4px">
                Tối đa {MAX_CHARS} ký tự &nbsp;·&nbsp;
                Không nhập thông tin cá nhân khách hàng &nbsp;·&nbsp;
                Chỉ dùng ngôn ngữ nghiệp vụ nội bộ
            </div>""",
            unsafe_allow_html=True,
        )
    with col_btn:
        submitted = st.form_submit_button(
            "Tra cứu chính sách",
            use_container_width=True,
            type="primary",
        )

# ---------------------------------------------------------------------------
# 9. Xử lý khi submit
# ---------------------------------------------------------------------------
if submitted:
    q = user_question.strip() if user_question else ""

    if not q:
        st.warning("Vui lòng nhập nội dung câu hỏi trước khi thực hiện tra cứu.")
    else:
        if q != st.session_state.last_question:
            st.session_state.last_response = None
            st.session_state.last_question = q

        with st.status("Đang xử lý yêu cầu tra cứu…", expanded=True) as status_box:
            st.write("Kiểm tra an toàn đầu vào…")
            st.write("Lấy bằng chứng từ kho chính sách…")
            st.write("Xác minh nguồn và quyền truy cập…")

            try:
                user_ctx = get_current_user_context()
                response = st.session_state.policy_service.process_question(
                    question=q,
                    user_context=user_ctx,
                )
                st.session_state.last_response = response
                st.write("Hoàn tất — Đang hiển thị kết quả…")
                status_box.update(label="Xử lý hoàn tất", state="complete", expanded=False)
            except Exception as exc:
                status_box.update(label="Lỗi xử lý yêu cầu", state="error", expanded=False)
                st.error(
                    "**Lỗi hệ thống** — Không thể xử lý yêu cầu tra cứu. "
                    "Vui lòng thử lại hoặc liên hệ bộ phận kỹ thuật.\n\n"
                    f"Mã lỗi: `{type(exc).__name__}`",
                )
                st.session_state.last_response = None

st.divider()

# ---------------------------------------------------------------------------
# 10. Hiển thị kết quả
# ---------------------------------------------------------------------------
if st.session_state.last_response:
    response = st.session_state.last_response

    # KNW 01 — Câu hỏi luôn hiển thị cùng kết quả
    st.markdown(
        f'<div class="crm-question-card">'
        f'<div style="font-size:0.68rem;text-transform:uppercase;'
        f'letter-spacing:0.1em;color:{TEXT_MUTED};font-weight:700;margin-bottom:5px">'
        f'Yêu cầu tra cứu</div>'
        f'<div style="font-size:0.95rem;line-height:1.6">'
        f'{st.session_state.last_question}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    render_policy_response(response)

    st.divider()

    # Feedback và Referral trong 2 cột
    col_fb, col_ref = st.columns(2)
    with col_fb:
        render_feedback_form(
            question=st.session_state.last_question,
            hold_reason_code=response.hold_reason_code,
        )
    with col_ref:
        render_referral_form(
            question=st.session_state.last_question,
            default_policy_owner=response.policy_owner or "Chưa xác định",
        )

else:
    if not submitted:
        st.markdown(
            f"""
            <div style="
                background:{BG_CARD};
                border:1.5px dashed {BORDER};
                border-radius:12px;
                padding:2.5rem 2rem;
                text-align:center;
                color:{TEXT_MUTED};
            ">
                <div style="margin-bottom:14px">
                    <svg width="40" height="40" viewBox="0 0 24 24" fill="none">
                        <circle cx="11" cy="11" r="7" stroke="{BORDER}"
                                stroke-width="2"/>
                        <path d="m21 21-4-4" stroke="{BORDER}" stroke-width="2"
                              stroke-linecap="round"/>
                    </svg>
                </div>
                <div style="font-size:1.0rem;font-weight:700;margin-bottom:6px;color:{TEXT_PRIMARY}">
                    Chưa có yêu cầu tra cứu nào được thực hiện
                </div>
                <div style="font-size:0.85rem;color:{TEXT_MUTED};line-height:1.6">
                    Nhập câu hỏi hoặc tình huống nghiệp vụ ở trên,
                    sau đó nhấn <strong>Tra cứu chính sách</strong> để bắt đầu.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# 11. Chân trang
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="crm-footer">
        <svg width="11" height="11" viewBox="0 0 24 24" fill="none"
             style="vertical-align:middle;margin-right:5px;margin-bottom:1px">
            <rect x="5" y="11" width="14" height="10" rx="2" fill="{TEXT_CAPTION}"/>
            <path d="M8 11V7a4 4 0 0 1 8 0v4" stroke="{TEXT_CAPTION}" stroke-width="2"
                  stroke-linecap="round"/>
        </svg>
        AI-06 &nbsp;CRM Knowledge &amp; Policy Assistant
        &nbsp;&nbsp;·&nbsp;&nbsp;
        Config <code>{config.CONFIG_VERSION}</code>
        &nbsp;·&nbsp;
        Prompt <code>{config.PROMPT_VERSION}</code>
        &nbsp;&nbsp;·&nbsp;&nbsp;
        CHỈ DÙNG NỘI BỘ
    </div>
    """,
    unsafe_allow_html=True,
)
