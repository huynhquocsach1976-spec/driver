import streamlit as st
import requests
import io
import pandas as pd
from datetime import date
import html as _html
try:
    import streamlit.components.v1 as components
except Exception:
    components = None

# =========================================================
# CẤU HÌNH TRANG
# =========================================================

BACKEND_URL = "https://driver-ynpg.onrender.com"

st.set_page_config(
    page_title="Hệ Thống Đào Tạo Lái Xe AI Pro",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# GIAO DIỆN (CSS)
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --primary: #2563eb;
    --primary-light: #3b82f6;
    --cyan: #06b6d4;
    --text: #0f172a;
    --muted: #64748b;
    --border: #e2e8f0;
}

/* ---------- NỀN & KHUNG ---------- */
html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
    color: var(--text);
    -webkit-font-smoothing: antialiased;
}
.stApp {
    background: #f4f7fb;
}
.main .block-container,
div[data-testid="stMainBlockContainer"] {
    padding-top: 1.5rem;
    padding-bottom: 5rem;
    max-width: 1280px;
    background: transparent !important;
}
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1.2rem 0 !important;
}
h3, h5 {
    color: var(--text);
    letter-spacing: -0.3px;
}

/* ---------- ẨN CÁC THÀNH PHẦN MẶC ĐỊNH CỦA STREAMLIT (KỂ CẢ MANAGE APP) ---------- */
#MainMenu, footer {
    visibility: hidden;
}
header[data-testid="stHeader"] {
    background: transparent !important;
    box-shadow: none !important;
    border-bottom: none !important;
}
div[data-testid="stToolbar"],
div[data-testid="stMainMenu"],
div[data-testid="stDeployButton"],
div[data-testid="stAppDeployButton"],
div[data-testid="stStatusWidget"],
div[data-testid="stDecoration"],
[data-testid="manage-app-button"],
button[aria-label*="Manage app" i],
a[aria-label*="Manage app" i],
a[href*="manage-app"],
[class*="viewerBadge"],
[class*="_terminalButton_"] {
    display: none !important;
}
/* Nút mở lại sidebar khi đã thu gọn */
[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapsedControl"] button,
[data-testid="collapsedControl"] button {
    background: linear-gradient(135deg, var(--primary-light), var(--cyan)) !important;
    color: #ffffff !important;
    border-radius: 10px !important;
    box-shadow: 0 6px 16px -4px rgba(59, 130, 246, 0.55) !important;
}

/* ---------- THANH CUỘN ---------- */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

/* ---------- SIDEBAR ---------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1220 0%, #131c2e 55%, #0f172a 100%) !important;
    border-right: none !important;
    box-shadow: 6px 0 28px -14px rgba(0, 0, 0, 0.5);
}
section[data-testid="stSidebar"]::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #3b82f6, #06b6d4, #8b5cf6);
    z-index: 10;
}
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label {
    color: #e2e8f0 !important;
}
.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 18px 14px;
    margin-bottom: 18px;
    border-radius: 16px;
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.22), rgba(6, 182, 212, 0.08));
    border: 1px solid rgba(147, 197, 253, 0.2);
}
.sidebar-brand-icon {
    width: 46px; height: 46px;
    flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px;
    border-radius: 12px;
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    box-shadow: 0 6px 16px rgba(59, 130, 246, 0.45);
}
.sidebar-title {
    margin: 0;
    font-size: 15px;
    font-weight: 800;
    line-height: 1.3;
    letter-spacing: 0.3px;
    background: linear-gradient(135deg, #60a5fa, #22d3ee);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.sidebar-subtitle {
    margin: 2px 0 0 0 !important;
    font-size: 11px;
    font-weight: 500;
    color: #94a3b8 !important;
}
.sidebar-menu-label {
    margin: 6px 4px 10px 4px !important;
    padding-left: 4px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #64748b !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 3px;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    width: 100%;
    padding: 11px 14px !important;
    border: 1px solid transparent;
    border-left: 3px solid transparent;
    border-radius: 10px;
    transition: all 0.2s ease;
    cursor: pointer;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label p {
    font-size: 13.5px;
    font-weight: 600;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(59, 130, 246, 0.14);
    transform: translateX(3px);
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(90deg, rgba(59, 130, 246, 0.38), rgba(6, 182, 212, 0.08));
    border-left-color: #60a5fa;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
    color: #ffffff !important;
    font-weight: 800;
}
section[data-testid="stSidebar"] button[kind="secondary"] {
    background: rgba(239, 68, 68, 0.14) !important;
    color: #f87171 !important;
    border: 1px solid rgba(239, 68, 68, 0.32) !important;
    font-weight: 700 !important;
}
section[data-testid="stSidebar"] button[kind="secondary"]:hover {
    background: linear-gradient(135deg, #ef4444, #dc2626) !important;
    color: #ffffff !important;
    border-color: #ef4444 !important;
    box-shadow: 0 8px 18px -6px rgba(239, 68, 68, 0.6) !important;
}

/* ---------- BANNER TIÊU ĐỀ TRANG ---------- */
.page-hero {
    position: relative;
    overflow: hidden;
    padding: 26px 32px;
    margin-bottom: 24px;
    border-radius: 18px;
    background: linear-gradient(120deg, #0f172a 0%, #1e3a8a 52%, #2563eb 100%);
    box-shadow: 0 18px 34px -16px rgba(30, 58, 138, 0.65);
}
.page-hero::after {
    content: "";
    position: absolute;
    right: -50px; top: -80px;
    width: 250px; height: 250px;
    border-radius: 50%;
    background: rgba(96, 165, 250, 0.18);
}
.page-hero::before {
    content: "";
    position: absolute;
    right: 120px; bottom: -100px;
    width: 190px; height: 190px;
    border-radius: 50%;
    background: rgba(6, 182, 212, 0.14);
}
.hero-title {
    position: relative; z-index: 1;
    font-size: 25px;
    font-weight: 800;
    letter-spacing: -0.4px;
    color: #ffffff;
}
.hero-sub {
    position: relative; z-index: 1;
    margin-top: 6px;
    font-size: 13.5px;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.82);
}

.section-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 26px 0 16px 0;
}
.section-header-title {
    font-size: 16px;
    font-weight: 800;
    color: #1e293b;
    white-space: nowrap;
}
.section-header-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, #cbd5e1, transparent);
}

/* ---------- THẺ CHỈ SỐ ---------- */
div[data-testid="stColumn"]:nth-child(1), div[data-testid="column"]:nth-child(1) { --acc: #2563eb; }
div[data-testid="stColumn"]:nth-child(2), div[data-testid="column"]:nth-child(2) { --acc: #f59e0b; }
div[data-testid="stColumn"]:nth-child(3), div[data-testid="column"]:nth-child(3) { --acc: #10b981; }
div[data-testid="stColumn"]:nth-child(4), div[data-testid="column"]:nth-child(4) { --acc: #8b5cf6; }

div[data-testid="stMetric"] {
    position: relative;
    overflow: hidden;
    padding: 18px 18px 14px 18px !important;
    background: #ffffff;
    border: 1px solid var(--border);
    border-radius: 16px;
    box-shadow: 0 8px 20px -12px rgba(15, 23, 42, 0.2);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
div[data-testid="stMetric"]::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: var(--acc, #2563eb);
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 18px 30px -14px rgba(15, 23, 42, 0.3);
}
div[data-testid="stMetricLabel"] p {
    font-size: 12px !important;
    font-weight: 700 !important;
    letter-spacing: 0.3px;
    color: var(--muted) !important;
}
div[data-testid="stMetricValue"] {
    font-weight: 800 !important;
    letter-spacing: -0.6px;
    color: var(--text) !important;
}

/* Khung thẻ: dùng viền mặc định của st.container(border=True), không ghi đè selector toàn cục */

/* ---------- DÒNG DANH SÁCH ---------- */
.row-flex {
    display: flex;
    align-items: center;
    gap: 14px;
}
.row-main { flex: 1; min-width: 0; }
.row-title {
    font-size: 15px;
    font-weight: 700;
    color: var(--text);
}
.row-sub {
    margin-top: 3px;
    font-size: 12.5px;
    color: var(--muted);
}
.row-end { flex-shrink: 0; }

.avatar-circle {
    flex-shrink: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    font-size: 15px;
    font-weight: 700;
    color: #ffffff;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.18);
}
.icon-tile {
    flex-shrink: 0;
    width: 46px; height: 46px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
    border-radius: 12px;
    background: linear-gradient(135deg, #eff6ff, #dbeafe);
    border: 1px solid #bfdbfe;
}
.date-tile {
    flex-shrink: 0;
    width: 54px;
    padding: 6px 0;
    text-align: center;
    border-radius: 12px;
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: #ffffff;
    box-shadow: 0 8px 16px -8px rgba(37, 99, 235, 0.7);
}
.date-tile b { display: block; font-size: 20px; line-height: 1.1; }
.date-tile small { font-size: 10px; font-weight: 600; opacity: 0.85; }
.time-chip {
    display: inline-block;
    padding: 2px 10px;
    margin-left: 6px;
    font-size: 11.5px;
    font-weight: 700;
    color: #0e7490;
    background: #cffafe;
    border-radius: 999px;
}
.cell-label {
    margin-bottom: 4px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.4px;
    text-transform: uppercase;
    color: #94a3b8;
}
.cell-value {
    font-size: 14.5px;
    font-weight: 700;
    color: var(--text);
}
.progress-track {
    width: 100%;
    height: 7px;
    margin-top: 8px;
    overflow: hidden;
    background: #e2e8f0;
    border-radius: 99px;
}
.progress-fill {
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, #3b82f6, #06b6d4);
}
.eval-comment {
    margin-top: 8px;
    padding: 10px 14px;
    font-size: 13px;
    color: #475569;
    background: #f8fafc;
    border-left: 3px solid #cbd5e1;
    border-radius: 8px;
}

/* ---------- HUY HIỆU ---------- */
.badge-danger, .badge-success, .badge-info, .badge-warning {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    font-size: 11.5px;
    font-weight: 700;
    letter-spacing: 0.2px;
    border-radius: 999px;
    white-space: nowrap;
}
.badge-danger::before, .badge-success::before, .badge-warning::before {
    content: "";
    width: 6px; height: 6px;
    border-radius: 50%;
}
.badge-danger  { background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }
.badge-danger::before  { background: #ef4444; box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2); }
.badge-success { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
.badge-success::before { background: #22c55e; box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.2); }
.badge-warning { background: #fef3c7; color: #b45309; border: 1px solid #fde68a; }
.badge-warning::before { background: #f59e0b; box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.2); }
.badge-info    { background: #dbeafe; color: #1d4ed8; border: 1px solid #bfdbfe; }
.student-code {
    display: inline-block;
    margin-bottom: 6px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #4f46e5;
    background: linear-gradient(135deg, #eff6ff, #e0e7ff);
    border: 1px solid #c7d2fe;
    border-radius: 999px;
}

/* ---------- HỒ SƠ HỌC VIÊN ---------- */
.profile-header-card {
    position: relative;
    overflow: hidden;
    margin-bottom: 16px;
    padding: 24px 28px;
    color: #ffffff;
    border-radius: 16px;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
    box-shadow: 0 14px 28px -14px rgba(15, 23, 42, 0.6);
}
.profile-header-card::before {
    content: "";
    position: absolute;
    top: -50%; right: -10%;
    width: 300px; height: 300px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(59, 130, 246, 0.35) 0%, transparent 70%);
}

/* ---------- FORM, EXPANDER ---------- */
div[data-testid="stForm"],
div[data-testid="stExpander"] {
    background: #ffffff;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    box-shadow: 0 6px 18px -12px rgba(15, 23, 42, 0.2);
}
div[data-testid="stExpander"] summary {
    padding: 14px 18px;
    font-weight: 700;
}
div[data-testid="stExpander"] summary:hover {
    color: var(--primary);
}

/* ---------- Ô NHẬP LIỆU ---------- */
div[data-baseweb="input"],
div[data-baseweb="select"] > div,
div[data-baseweb="textarea"] {
    background: #f8fafc;
    border-color: var(--border) !important;
    border-radius: 10px !important;
    transition: all 0.2s ease;
}
div[data-baseweb="input"]:focus-within,
div[data-baseweb="select"] > div:focus-within,
div[data-baseweb="textarea"]:focus-within {
    background: #ffffff;
    border-color: var(--primary-light) !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.16);
}
label[data-testid="stWidgetLabel"] p {
    font-size: 13px;
    font-weight: 600;
    color: #334155;
}

/* ---------- NÚT BẤM ---------- */
.stButton > button,
div[data-testid="stFormSubmitButton"] > button,
div[data-testid="stDownloadButton"] > button,
div[data-testid="stPopover"] > div > button {
    padding: 0.5rem 1.2rem;
    font-size: 13.5px;
    font-weight: 600;
    letter-spacing: 0.2px;
    border: 1px solid var(--border);
    border-radius: 10px !important;
    transition: all 0.2s ease;
}
.stButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover,
div[data-testid="stDownloadButton"] > button:hover {
    color: var(--primary);
    border-color: var(--primary-light);
    transform: translateY(-1px);
    box-shadow: 0 8px 16px -8px rgba(37, 99, 235, 0.5);
}
button[kind="primary"],
button[data-testid="stBaseButton-primary"],
button[data-testid="stBaseButton-primaryFormSubmit"] {
    color: #ffffff !important;
    border: none !important;
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    box-shadow: 0 10px 18px -10px rgba(37, 99, 235, 0.85);
}
button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover,
button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
    color: #ffffff !important;
    filter: brightness(1.1);
}
div[data-testid="stPopover"] > div > button {
    color: #15803d;
    background: linear-gradient(135deg, #f0fdf4, #dcfce7);
    border-color: #bbf7d0;
}

/* ---------- CHÚ THÍCH, THÔNG BÁO, CHAT, BẢNG, BIỂU ĐỒ ---------- */
div[data-testid="stCaptionContainer"] {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.4px;
    text-transform: uppercase;
    color: #94a3b8;
}
div[data-testid="stAlert"] {
    border-radius: 12px;
    box-shadow: 0 4px 12px -8px rgba(15, 23, 42, 0.2);
}
div[data-testid="stChatMessage"] {
    padding: 14px 18px;
    margin-bottom: 10px;
    background: #ffffff;
    border: 1px solid var(--border);
    border-radius: 16px;
    box-shadow: 0 6px 16px -12px rgba(15, 23, 42, 0.25);
}
div[data-testid="stDataFrame"] {
    overflow: hidden;
    border: 1px solid var(--border);
    border-radius: 12px;
}
div[data-testid="stArrowVegaLiteChart"],
div[data-testid="stVegaLiteChart"] {
    padding: 12px;
    background: #ffffff;
    border: 1px solid var(--border);
    border-radius: 14px;
    box-shadow: 0 6px 18px -12px rgba(15, 23, 42, 0.2);
}
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    padding: 5px;
    background: #e2e8f0;
    border-radius: 12px;
}
.stTabs [data-baseweb="tab"] {
    height: 40px;
    padding: 0 18px;
    font-weight: 600;
    background: transparent;
    border-radius: 9px;
}
.stTabs [aria-selected="true"] {
    background: #ffffff;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.14);
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# ẨN NÚT "MANAGE APP" (Streamlit Community Cloud)
# Nút này do nền tảng chèn vào trang, nên ngoài CSS còn dùng JS để dò và ẩn.
# =========================================================

HIDE_MANAGE_APP_JS = """
<script>
(function () {
  var STYLE_ID = 'hide-manage-app-style';
  var CSS = '[data-testid="manage-app-button"], [class*="viewerBadge"], [class*="_terminalButton_"],' +
            ' button[aria-label*="Manage app" i], a[aria-label*="Manage app" i], a[href*="manage-app"]' +
            ' { display: none !important; }';

  function hideIn(doc) {
    try {
      if (!doc.getElementById(STYLE_ID)) {
        var style = doc.createElement('style');
        style.id = STYLE_ID;
        style.textContent = CSS;
        (doc.head || doc.documentElement).appendChild(style);
      }
      var nodes = doc.querySelectorAll('button, a, div[role="button"]');
      for (var i = 0; i < nodes.length; i++) {
        var text = (nodes[i].textContent || '').trim().toLowerCase();
        if (text === 'manage app') {
          nodes[i].style.setProperty('display', 'none', 'important');
          var parent = nodes[i].parentElement;
          if (parent && (parent.textContent || '').trim().toLowerCase() === 'manage app') {
            parent.style.setProperty('display', 'none', 'important');
          }
        }
      }
    } catch (e) { /* khác origin: bỏ qua */ }
  }

  function run() {
    var wins = [window.parent, window.parent.parent, window.top];
    for (var i = 0; i < wins.length; i++) {
      try { hideIn(wins[i].document); } catch (e) {}
    }
  }
  run();
  setInterval(run, 700);
})();
</script>
"""

# Đổi thành True nếu muốn thử ẩn nút "Manage app" bằng JS (mặc định tắt cho an toàn)
ENABLE_MANAGE_APP_HIDER = False

if ENABLE_MANAGE_APP_HIDER:
    st.markdown(
        "<style>div[data-testid='stElementContainer']:has(iframe)"
        "{height:0 !important;margin:0 !important;overflow:hidden;}</style>",
        unsafe_allow_html=True
    )
    if hasattr(st, "iframe"):
        st.iframe(HIDE_MANAGE_APP_JS.strip(), height=1)
    elif components is not None:
        components.html(HIDE_MANAGE_APP_JS, height=0)


# =========================================================
# HÀM HỖ TRỢ GIAO DIỆN
# =========================================================

AVATAR_COLORS = ["#3b82f6", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b", "#ec4899"]


def esc(value):
    return _html.escape(str(value if value is not None else ""))


def page_header(title, subtitle):
    st.markdown(
        f'<div class="page-hero"><div class="hero-title">{title}</div>'
        f'<div class="hero-sub">{subtitle}</div></div>',
        unsafe_allow_html=True
    )


def section_header(title):
    st.markdown(
        f'<div class="section-header"><span class="section-header-title">{title}</span>'
        f'<span class="section-header-line"></span></div>',
        unsafe_allow_html=True
    )


def avatar_html(name, index=0, size=44):
    parts = str(name or "").strip().split()
    initials = (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else (parts[0][0].upper() if parts else "?")
    color = AVATAR_COLORS[index % len(AVATAR_COLORS)]
    return (
        f'<div class="avatar-circle" style="background:{color};width:{size}px;height:{size}px;">'
        f'{esc(initials)}</div>'
    )


def status_badge(status):
    key = str(status or "").strip().lower()
    if key in ("active", "đang hoạt động", "hoạt động"):
        return '<span class="badge-success">Đang hoạt động</span>'
    if key in ("maintenance", "bảo dưỡng"):
        return '<span class="badge-warning">Bảo dưỡng</span>'
    if key in ("inactive", "ngừng hoạt động", "nghỉ"):
        return '<span class="badge-danger">Ngừng hoạt động</span>'
    return f'<span class="badge-info">{esc(status or "Không rõ")}</span>'


def score_badge(score):
    try:
        value = float(score)
    except (TypeError, ValueError):
        return '<span class="badge-info">Chưa có</span>'
    if value >= 8:
        return f'<span class="badge-success">{value:.2f}</span>'
    if value >= 6.5:
        return f'<span class="badge-info">{value:.2f}</span>'
    return f'<span class="badge-warning">{value:.2f}</span>'


def date_tile(value):
    parts = str(value or "").split("-")
    if len(parts) == 3:
        return f'<div class="date-tile"><b>{esc(parts[2][:2])}</b><small>Thg {esc(parts[1])}</small></div>'
    return f'<div class="date-tile"><b>—</b><small>{esc(value or "")}</small></div>'


# =========================================================
# 1. KHỞI TẠO STATE & HỆ THỐNG PHÂN QUYỀN / TÀI KHOẢN
# =========================================================

if "users_db" not in st.session_state:
    st.session_state.users_db = {
        "admin": {"password": "123", "role": "Quản lý", "name": "Quản Trị Viên"},
        "teacher": {"password": "123", "role": "Giáo viên", "name": "Thầy Giáo Mẫu"},
        "accountant": {"password": "123", "role": "Kế toán", "name": "Cô Kế Toán"}
    }

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_name = None

# Màn hình Đăng nhập
if not st.session_state.logged_in:
    st.markdown("""
    <style>
    .stApp {
        background:
            radial-gradient(circle at 12% 18%, rgba(59, 130, 246, 0.35) 0, transparent 38%),
            radial-gradient(circle at 88% 82%, rgba(6, 182, 212, 0.28) 0, transparent 40%),
            linear-gradient(135deg, #0b1220 0%, #16294a 50%, #0b1220 100%);
    }
    section[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    div[data-testid="stForm"] {
        padding: 26px 26px 18px 26px;
        border: none !important;
        border-radius: 22px !important;
        box-shadow: 0 30px 60px -20px rgba(0, 0, 0, 0.6);
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
    with col_l2:
        st.markdown("""
        <div style="text-align:center; margin-bottom: 22px;">
            <div style="width:68px;height:68px;margin:0 auto 14px;display:flex;align-items:center;justify-content:center;font-size:34px;border-radius:20px;background:linear-gradient(135deg,#3b82f6,#06b6d4);box-shadow:0 14px 30px -8px rgba(59,130,246,0.7);">🚗</div>
            <div style="font-size:26px;font-weight:800;color:#ffffff;letter-spacing:-0.5px;">Đào Tạo Lái Xe AI Pro</div>
            <div style="font-size:13px;font-weight:500;color:#94a3b8;margin-top:6px;">Hệ thống quản lý trung tâm thông minh</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username_input = st.text_input("Tên đăng nhập", placeholder="Nhập tên đăng nhập...")
            password_input = st.text_input("Mật khẩu", type="password", placeholder="Nhập mật khẩu...")

            submit_login = st.form_submit_button("🚀 Đăng Nhập Hệ Thống", use_container_width=True, type="primary")
            if submit_login:
                user_info = st.session_state.users_db.get(username_input.strip())
                if user_info and user_info["password"] == password_input:
                    st.session_state.logged_in = True
                    st.session_state.user_role = user_info["role"]
                    st.session_state.user_name = user_info["name"]
                    st.rerun()
                else:
                    st.error("❌ Tên đăng nhập hoặc mật khẩu không chính xác!")

        st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 11px; margin-top: 18px;'>💡 Tài khoản mẫu: <b>admin</b> / 123 (Quản lý) | <b>teacher</b> / 123 (Giáo viên) | <b>accountant</b> / 123 (Kế toán)</p>", unsafe_allow_html=True)
    st.stop()

# =========================================================
# CÁC HÀM GỌI BACKEND API
# =========================================================

def api_get(endpoint, params=None):
    try:
        response = requests.get(f"{BACKEND_URL}{endpoint}", params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Không thể kết nối đến Backend (`{BACKEND_URL}`). Hãy đảm bảo server FastAPI đã khởi động!")
        return None
    except Exception:
        return None


def api_error_detail(response):
    """Lấy nội dung lỗi mà backend trả về (trường detail hoặc nội dung thô)."""
    try:
        data = response.json()
        detail = data.get("detail", data) if isinstance(data, dict) else data
        return str(detail)[:600]
    except Exception:
        return (response.text or "Máy chủ không trả về nội dung.")[:600]


def get_students(params=None):
    res = api_get("/students/management", params)
    return res.get("data", []) if res else []


def get_teachers():
    res = api_get("/teachers")
    return res.get("data", []) if res else []


def get_vehicles():
    res = api_get("/vehicles")
    return res.get("data", []) if res else []


def get_lessons():
    res = api_get("/lessons")
    return res.get("data", []) if res else []


def get_evaluations():
    res = api_get("/evaluations")
    return res.get("data", []) if res else []


def get_dashboard_data():
    res = api_get("/dashboard")
    return res.get("data", {}) if res else {}


# =========================================================
# SIDEBAR ĐIỀU HƯỚNG THEO PHÂN QUYỀN
# =========================================================

with st.sidebar:
    st.markdown(
        f'''
        <div class="sidebar-brand">
            <div class="sidebar-brand-icon">🚗</div>
            <div>
                <p class="sidebar-title">ĐÀO TẠO LÁI XE PRO</p>
                <p class="sidebar-subtitle"><b>{esc(st.session_state.user_name)}</b> · {esc(st.session_state.user_role)}</p>
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )
    st.markdown("<p class='sidebar-menu-label'>📋 Menu Điều Hướng</p>", unsafe_allow_html=True)

    role = st.session_state.user_role
    if role == "Quản lý":
        menu_options = [
            "📊 Tổng quan", "👨‍🏫 Quản lý giáo viên", "🚗 Quản lý xe",
            "👨‍🎓 Quản lý học viên", "💰 Quản lý học phí", "🔑 Quản lý tài khoản",
            "📚 Lịch học & Buổi học", "⭐ Đánh giá & AI", "🤖 Trợ lý AI Trung tâm"
        ]
    elif role == "Giáo viên":
        menu_options = [
            "📊 Tổng quan", "👨‍🎓 Quản lý học viên", "📚 Lịch học & Buổi học",
            "⭐ Đánh giá & AI", "🤖 Trợ lý AI Trung tâm"
        ]
    else:  # Kế toán
        menu_options = [
            "📊 Tổng quan", "👨‍🎓 Quản lý học viên", "💰 Quản lý học phí",
            "🤖 Trợ lý AI Trung tâm"
        ]

    menu = st.radio("MENU", menu_options, label_visibility="collapsed")
    st.markdown("<br><br>", unsafe_allow_html=True)

    if st.button("🚪 Đăng xuất tài khoản", use_container_width=True, type="secondary"):
        st.session_state.logged_in = False
        st.rerun()

# =========================================================
# 1. TỔNG QUAN
# =========================================================

if menu == "📊 Tổng quan":
    page_header("📊 Tổng Quan Hệ Thống Trung Tâm", "Thống kê hoạt động, tài chính và tiến độ đào tạo theo thời gian thực")

    dash = get_dashboard_data()
    overview = dash.get("overview", {})
    eval_info = dash.get("evaluations", {})
    by_teacher = dash.get("students_by_teacher", [])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👨‍🎓 Tổng học viên", overview.get("total_students", 0))
    c2.metric("👨‍🏫 Tổng giáo viên", overview.get("total_teachers", 0))
    c3.metric("🚗 Tổng số xe", overview.get("total_vehicles", 0))
    c4.metric("⏱️ Tổng giờ thực hành", f"{overview.get('total_hours', 0):g}h")

    st.write("")

    fc1, fc2, fc3 = st.columns(3)
    fc1.metric("💰 Tổng học phí cam kết", f"{overview.get('total_tuition', 0):,.0f} đ")
    fc2.metric("💵 Đã thu thực tế", f"{overview.get('total_paid', 0):,.0f} đ")
    fc3.metric("🔴 Tổng công nợ còn lại", f"{overview.get('total_remaining', 0):,.0f} đ")

    section_header("📈 Biểu đồ phân tích trực quan")

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.markdown("##### 👨‍🏫 Số lượng học viên phụ trách theo giáo viên")
        if by_teacher:
            df_teacher = pd.DataFrame(by_teacher)
            if not df_teacher.empty and "full_name" in df_teacher and "total_students" in df_teacher:
                st.bar_chart(df_teacher.set_index("full_name")["total_students"])
        else:
            st.info("Chưa có dữ liệu phân công giáo viên.")

    with chart_col2:
        st.markdown("##### ⭐ Thống kê chất lượng đánh giá")
        st.metric("Tổng số lượt đánh giá kỹ năng", eval_info.get("total_evaluations", 0))
        st.metric("Điểm trung bình toàn trung tâm", f"{eval_info.get('average_score', 0):.2f} / 10")

# =========================================================
# 2. QUẢN LÝ HỌC VIÊN & XUẤT EXCEL
# =========================================================

elif menu == "👨‍🎓 Quản lý học viên":
    page_header("👨‍🎓 Quản Lý Học Viên & Báo Cáo", "Thêm mới, tìm kiếm, tra cứu hồ sơ chi tiết và xuất danh sách học viên ra Excel")

    if st.button("📥 Xuất danh sách học viên & công nợ ra Excel", type="primary"):
        df_export = pd.DataFrame([{
            "Mã HV": s.get("student_code"),
            "Họ Tên": s.get("full_name"),
            "SĐT": s.get("phone"),
            "Hạng Bằng": s.get("license_class"),
            "Học Phí": s.get("tuition", {}).get("total", 0),
            "Đã Đóng": s.get("tuition", {}).get("paid", 0),
            "Còn Nợ": s.get("tuition", {}).get("remaining", 0),
            "Điểm TB": s.get("evaluation", {}).get("average_score", 0),
            "Trạng Thái": s.get("status")
        } for s in get_students()])

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_export.to_excel(writer, sheet_name='HocVien', index=False)

        st.download_button(
            label="💾 Tải file Excel ngay (.xlsx)",
            data=output.getvalue(),
            file_name="Danh_Sach_Hoc_Vien_Driving_Center.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.write("")
    with st.expander("➕ Thêm học viên mới vào hệ thống", expanded=False):
        teacher_list = get_teachers()
        with st.form("add_student_form"):
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                s_code = st.text_input("Mã học viên *", placeholder="VD: HV010")
                s_name = st.text_input("Họ và tên học viên *", placeholder="VD: Nguyễn Văn An")
                s_phone = st.text_input("Số điện thoại", placeholder="0901234567")
                s_dob = st.date_input("Ngày sinh", value=date(1995, 1, 1))
            with col_s2:
                s_address = st.text_input("Địa chỉ", placeholder="Quận 1, TP.HCM")
                s_license = st.selectbox("Hạng bằng lái", ["B1", "B2", "C", "D", "E"])
                s_teacher = st.selectbox("Giáo viên phụ trách", [None] + teacher_list, format_func=lambda x: "Chưa phân công" if x is None else f"{x.get('teacher_code')} - {x.get('full_name')}")
                s_tuition = st.number_input("Tổng học phí (VNĐ)", min_value=0.0, value=15000000.0, step=500000.0, format="%.0f")

            if st.form_submit_button("💾 Lưu học viên mới", use_container_width=True, type="primary"):
                if s_code.strip() and s_name.strip():
                    payload = {
                        "student_code": s_code.strip(),
                        "full_name": s_name.strip(),
                        "phone": s_phone.strip() or None,
                        "date_of_birth": str(s_dob),
                        "address": s_address.strip() or None,
                        "license_class": s_license,
                        "tuition_fee": float(s_tuition),
                        "status": "Đang học",
                        "teacher_id": int(s_teacher["id"]) if s_teacher else None
                    }
                    res = None
                    try:
                        res = requests.post(f"{BACKEND_URL}/students", json=payload, timeout=30)
                        res.raise_for_status()
                        st.success("✅ Thêm học viên thành công!")
                        st.rerun()
                    except requests.exceptions.HTTPError:
                        st.error(f"❌ Máy chủ từ chối ({res.status_code}): {api_error_detail(res)}")
                        with st.expander("🔍 Dữ liệu đã gửi lên máy chủ (để kiểm tra)"):
                            st.json(payload)
                    except Exception as e:
                        st.error(f"❌ Lỗi khi thêm học viên: {e}")
                else:
                    st.warning("⚠️ Vui lòng nhập Mã học viên và Họ tên.")

    st.write("")
    f_col1, f_col2 = st.columns([3, 2])
    with f_col1:
        debt_only = st.checkbox("💰 Chỉ lọc học viên còn nợ học phí")
    with f_col2:
        min_score = st.number_input("⭐ Lọc điểm trung bình tối thiểu", min_value=0.0, max_value=10.0, value=0.0, step=0.5)

    params = {}
    if debt_only:
        params["debt_only"] = "true"
    if min_score > 0:
        params["min_score"] = min_score

    filtered_students = get_students(params)

    st.write("")
    if not filtered_students:
        st.info("Không tìm thấy học viên phù hợp với điều kiện lọc.")
    else:
        for student in filtered_students:
            sid = student.get("id")
            code = student.get("student_code", "")
            name = student.get("full_name", "")
            phone = student.get("phone", "")
            teacher_name = (student.get("teacher") or {}).get("full_name", "Chưa phân công")
            lessons_count = student.get("learning", {}).get("total_lessons", 0)
            hours_count = student.get("learning", {}).get("total_hours", 0)
            score = student.get("evaluation", {}).get("average_score")
            remaining = student.get("tuition", {}).get("remaining", 0)

            badge_tuition = '<span class="badge-danger">Còn nợ</span>' if remaining > 0 else '<span class="badge-success">Đã hoàn tất</span>'

            with st.container(border=True):
                c1, c2, c3, c4, c5, c6 = st.columns([2.2, 2, 1, 1, 1.2, 1.4])
                with c1:
                    st.markdown(f'<span class="student-code">{esc(code)}</span>', unsafe_allow_html=True)
                    st.markdown(f'<div class="row-title">{esc(name)}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="row-sub">📞 {esc(phone or "Chưa có")}</div>', unsafe_allow_html=True)
                with c2:
                    st.caption("👨‍🏫 Giáo viên")
                    st.write(teacher_name)
                with c3:
                    st.caption("📚 Buổi")
                    st.write(lessons_count)
                with c4:
                    st.caption("⏱️ Giờ")
                    st.write(f"{float(hours_count):g}h")
                with c5:
                    st.caption("⭐ Điểm TB")
                    st.markdown(score_badge(score), unsafe_allow_html=True)
                with c6:
                    st.caption("Học phí")
                    st.markdown(badge_tuition, unsafe_allow_html=True)
                    st.write("")
                    if st.button("👤 Xem hồ sơ", key=f"prof_{sid}", use_container_width=True, type="primary"):
                        st.session_state.selected_student = sid

            if st.session_state.get("selected_student") == sid:
                profile_res = api_get(f"/students/{sid}/full-profile")
                if profile_res and "data" in profile_res:
                    p_data = profile_res["data"]
                    p_student = p_data.get("student", {})
                    p_learning = p_data.get("learning", {})
                    p_eval = p_data.get("evaluations", {})
                    p_tuition = p_data.get("tuition", {})

                    st.divider()
                    st.markdown(f"""
                        <div class="profile-header-card">
                            <div style="position: relative; z-index: 1;">
                                <div style="font-size: 20px; font-weight: 800; letter-spacing: -0.3px;">👤 Hồ sơ chi tiết: {esc(p_student.get('full_name'))}</div>
                                <div style="color: #94a3b8; font-size: 12px; margin-top: 6px; display: flex; gap: 16px; flex-wrap: wrap;">
                                    <span>📋 Mã HV: <b style="color: #60a5fa;">{esc(p_student.get('student_code'))}</b></span>
                                    <span>🎯 Hạng bằng: <b style="color: #60a5fa;">{esc(p_student.get('license_class'))}</b></span>
                                    <span>📌 Trạng thái: <b style="color: #34d399;">{esc(p_student.get('status'))}</b></span>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    pc1, pc2, pc3, pc4 = st.columns(4)
                    pc1.metric("Tổng buổi học", p_learning.get("total_lessons", 0))
                    pc2.metric("Tổng giờ học", f"{p_learning.get('total_hours', 0):g}h")
                    pc3.metric("Điểm trung bình", p_eval.get("average_score") or "Chưa có")
                    pc4.metric("Còn nợ học phí", f"{p_tuition.get('remaining', 0):,.0f} đ")

                    st.write("")
                    if st.button("🤖 Yêu cầu AI Lập Kế Hoạch Ôn Thi Riêng", key=f"ai_plan_{sid}", use_container_width=True):
                        with st.spinner("🤖 Trí tuệ nhân tạo Gemini đang phân tích tiến độ học tập..."):
                            try:
                                plan_res = requests.post(f"{BACKEND_URL}/students/{sid}/training-plan", timeout=30)
                                plan_res.raise_for_status()
                                plan_data = plan_res.json().get("data", {})
                                st.session_state[f"plan_{sid}"] = plan_data.get("training_plan", "Không có dữ liệu kế hoạch.")
                                st.success("✅ AI đã lập kế hoạch thành công!")
                            except Exception as e:
                                st.error(f"Lỗi gọi AI: {e}")

                    if f"plan_{sid}" in st.session_state:
                        st.markdown("##### 💡 Kế hoạch đào tạo đề xuất từ AI:")
                        st.info(st.session_state[f"plan_{sid}"])

                    if st.button("❌ Đóng hồ sơ chi tiết", key=f"close_{sid}"):
                        st.session_state.selected_student = None
                        st.rerun()

# =========================================================
# 3. QUẢN LÝ GIÁO VIÊN
# =========================================================

elif menu == "👨‍🏫 Quản lý giáo viên":
    page_header("👨‍🏫 Quản Lý Giáo Viên Trung Tâm", "Thêm mới, cập nhật thông tin và trạng thái giảng dạy của giáo viên")

    teachers = get_teachers()
    st.metric("👨‍🏫 Tổng số giáo viên", len(teachers))
    st.write("")

    with st.expander("➕ Thêm giáo viên mới", expanded=False):
        with st.form("add_teacher_form"):
            t_code = st.text_input("Mã giáo viên *", placeholder="VD: GV005")
            t_name = st.text_input("Họ và tên giáo viên *", placeholder="VD: Trần Văn B")
            t_phone = st.text_input("Số điện thoại")
            t_license = st.text_input("Số giấy phép lái xe (GPLX)")

            if st.form_submit_button("💾 Lưu giáo viên", use_container_width=True, type="primary"):
                if t_code.strip() and t_name.strip():
                    payload = {
                        "teacher_code": t_code.strip(),
                        "full_name": t_name.strip(),
                        "phone": t_phone.strip() or None,
                        "license_number": t_license.strip() or None,
                        "status": "active"
                    }
                    try:
                        res = requests.post(f"{BACKEND_URL}/teachers", json=payload, timeout=10)
                        res.raise_for_status()
                        st.success("✅ Thêm giáo viên thành công!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi: {e}")
                else:
                    st.warning("Vui lòng nhập Mã giáo viên và Họ tên.")

    section_header("📋 Danh sách giáo viên")
    if not teachers:
        st.info("Chưa có giáo viên nào trong hệ thống.")
    for idx, t in enumerate(teachers):
        with st.container(border=True):
            st.markdown(
                f'''
                <div class="row-flex">
                    {avatar_html(t.get("full_name"), idx)}
                    <div class="row-main">
                        <div class="row-title">{esc(t.get("full_name"))}</div>
                        <div class="row-sub">Mã: <b>{esc(t.get("teacher_code"))}</b> · 📞 {esc(t.get("phone") or "Chưa có")}</div>
                    </div>
                    <div class="row-end">{status_badge(t.get("status"))}</div>
                </div>
                ''',
                unsafe_allow_html=True
            )

# =========================================================
# 4. QUẢN LÝ XE TẬP LÁI
# =========================================================

elif menu == "🚗 Quản lý xe":
    page_header("🚗 Quản Lý Phương Tiện & Xe Tập Lái", "Quản lý biển số xe, hãng sản xuất, dòng xe và trạng thái bảo dưỡng")

    vehicles = get_vehicles()
    st.metric("🚗 Tổng số xe", len(vehicles))
    st.write("")

    with st.expander("➕ Thêm xe tập lái mới", expanded=False):
        with st.form("add_vehicle_form"):
            v_plate = st.text_input("Biển số xe *", placeholder="51A-88888")
            v_brand = st.text_input("Hãng xe", placeholder="Toyota")
            v_model = st.text_input("Dòng xe", placeholder="Vios")
            v_class = st.text_input("Hạng xe đào tạo", value="B2")
            v_year = st.number_input("Năm sản xuất", min_value=2000, max_value=2030, value=2024)

            if st.form_submit_button("💾 Thêm xe mới", use_container_width=True, type="primary"):
                if v_plate.strip():
                    payload = {
                        "plate_number": v_plate.strip(),
                        "brand": v_brand.strip() or None,
                        "model": v_model.strip() or None,
                        "license_class": v_class.strip() or None,
                        "year": int(v_year),
                        "status": "active"
                    }
                    try:
                        res = requests.post(f"{BACKEND_URL}/vehicles", json=payload, timeout=10)
                        res.raise_for_status()
                        st.success("✅ Thêm xe thành công!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi: {e}")
                else:
                    st.warning("Vui lòng nhập biển số xe.")

    section_header("📋 Danh sách phương tiện")
    if not vehicles:
        st.info("Chưa có phương tiện nào trong hệ thống.")
    for v in vehicles:
        with st.container(border=True):
            st.markdown(
                f'''
                <div class="row-flex">
                    <div class="icon-tile">🚗</div>
                    <div class="row-main">
                        <div class="row-title">{esc(v.get("plate_number"))}</div>
                        <div class="row-sub">{esc(v.get("brand") or "")} {esc(v.get("model") or "")} · Hạng đào tạo: <b>{esc(v.get("license_class") or "—")}</b></div>
                    </div>
                    <div class="row-end">{status_badge(v.get("status"))}</div>
                </div>
                ''',
                unsafe_allow_html=True
            )

# =========================================================
# 5. LỊCH HỌC & BUỔI HỌC (XẾP LỊCH & XUẤT EXCEL)
# =========================================================

elif menu == "📚 Lịch học & Buổi học":
    page_header("📚 Quản Lý Lịch Học & Xếp Lịch Thông Minh", "Xếp lịch thực hành cho học viên, phân công giáo viên và xe tránh trùng giờ")

    students = get_students()
    teacher_list = get_teachers()
    vehicle_list = get_vehicles()
    lessons = get_lessons()

    if lessons:
        if st.button("📥 Xuất danh sách lịch học ra file Excel", type="primary"):
            df_lessons_export = pd.DataFrame([{
                "Mã Buổi Học": l.get("id"),
                "Ngày Học": l.get("lesson_date"),
                "Giờ Bắt Đầu": l.get("start_time"),
                "Giờ Kết Thúc": l.get("end_time"),
                "Thời Lượng (Giờ)": l.get("duration"),
                "Học Viên": l.get("student_name"),
                "Giáo Viên": l.get("teacher_name"),
                "Biển Số Xe": l.get("plate_number", "Không có"),
                "Loại Buổi Học": l.get("lesson_type"),
                "Nội Dung": l.get("content")
            } for l in lessons])

            output_l = io.BytesIO()
            with pd.ExcelWriter(output_l, engine='xlsxwriter') as writer_l:
                df_lessons_export.to_excel(writer_l, sheet_name='LichHoc', index=False)

            st.download_button(
                label="💾 Tải file Excel lịch học ngay (.xlsx)",
                data=output_l.getvalue(),
                file_name="Danh_Sach_Lich_Hoc_Driving_Center.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        st.write("")

    with st.expander("➕ Thêm buổi học mới (Xếp lịch)", expanded=True):
        with st.form("add_lesson_form"):
            c1, c2 = st.columns(2)
            with c1:
                st_id = st.selectbox("Chọn học viên *", students, format_func=lambda x: f"{x.get('student_code')} - {x.get('full_name')}")
                t_id = st.selectbox("Chọn giáo viên hướng dẫn *", teacher_list, format_func=lambda x: f"{x.get('teacher_code')} - {x.get('full_name')}")
                v_id = st.selectbox("Chọn xe tập lái", [None] + vehicle_list, format_func=lambda x: "Không chọn xe riêng" if x is None else f"{x.get('plate_number')} ({x.get('brand')})")
            with c2:
                l_date = st.date_input("Ngày học", value=date.today())
                s_time = st.text_input("Giờ bắt đầu", value="08:00")
                e_time = st.text_input("Giờ kết thúc", value="10:00")
                l_dur = st.number_input("Thời lượng (giờ)", min_value=0.5, value=2.0, step=0.5)
                l_type = st.text_input("Loại buổi học", value="Thực hành sa hình")

            l_content = st.text_area("Nội dung buổi học chi tiết")
            if st.form_submit_button("📅 Xác nhận xếp lịch học", use_container_width=True, type="primary"):
                payload = {
                    "student_id": int(st_id["id"]),
                    "teacher_id": int(t_id["id"]),
                    "vehicle_id": int(v_id["id"]) if v_id else None,
                    "lesson_date": str(l_date),
                    "start_time": s_time.strip(),
                    "end_time": e_time.strip(),
                    "duration": float(l_dur),
                    "lesson_type": l_type.strip(),
                    "content": l_content.strip() or None
                }
                try:
                    res = requests.post(f"{BACKEND_URL}/lessons", json=payload, timeout=10)
                    res.raise_for_status()
                    st.success("✅ Xếp lịch buổi học thành công!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Lỗi xếp lịch: {e}")

    section_header("📋 Lịch trình các buổi học gần đây")
    if not lessons:
        st.info("Chưa có buổi học nào được xếp lịch.")
    for l in lessons:
        with st.container(border=True):
            st.markdown(
                f'''
                <div class="row-flex">
                    {date_tile(l.get("lesson_date"))}
                    <div class="row-main">
                        <div class="row-title">{esc(l.get("student_name"))}
                            <span class="time-chip">⏰ {esc(l.get("start_time"))} - {esc(l.get("end_time"))}</span>
                        </div>
                        <div class="row-sub">👨‍🏫 {esc(l.get("teacher_name"))} · 🚗 {esc(l.get("plate_number", "Không có"))}</div>
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )

# =========================================================
# 6. ĐÁNH GIÁ & AI PHÂN TÍCH KỸ NĂNG
# =========================================================

elif menu == "⭐ Đánh giá & AI":
    page_header("⭐ Đánh Giá Kỹ Năng & Trợ Lý AI", "Theo dõi điểm số chi tiết từng kỹ năng lái xe và nhận xét đánh giá từ AI")

    evals = get_evaluations()
    st.metric("Tổng số đánh giá ghi nhận", len(evals))
    st.write("")

    for e in evals:
        eid = e.get("id")
        with st.container(border=True):
            st.markdown(
                f'''
                <div class="row-flex">
                    <div class="row-main">
                        <div class="row-title">{esc(e.get("student_name"))}</div>
                        <div class="row-sub">Mã học viên: <b>{esc(e.get("student_code"))}</b></div>
                    </div>
                    <div class="row-end">
                        <span class="cell-label" style="margin-right:6px;">Điểm tổng kết</span>{score_badge(e.get("score"))}
                    </div>
                </div>
                <div class="eval-comment">💬 Nhận xét giáo viên: {esc(e.get("comment") or "Không có")}</div>
                ''',
                unsafe_allow_html=True
            )

            if e.get("ai_comment"):
                st.success(f"🤖 **Đánh giá từ AI:**\n{e.get('ai_comment')}")

            if st.button(f"🤖 Kích hoạt AI phân tích đánh giá #{eid}", key=f"eval_ai_{eid}"):
                with st.spinner("AI đang xử lý nhận xét..."):
                    try:
                        res = requests.post(f"{BACKEND_URL}/evaluations/{eid}/ai", timeout=30)
                        res.raise_for_status()
                        st.success("✅ AI phân tích thành công!")
                        st.rerun()
                    except Exception as err:
                        st.error(f"Lỗi: {err}")

# =========================================================
# 7. QUẢN LÝ HỌC PHÍ & TÀI CHÍNH
# =========================================================

elif menu == "💰 Quản lý học phí":
    page_header("💰 Quản Lý Học Phí & Công Nợ", "Theo dõi tình hình đóng học phí, ghi nhận thanh toán và kiểm soát công nợ")

    fin_res = api_get("/dashboard/finance")
    if fin_res and "data" in fin_res:
        fin_data = fin_res["data"]
        overview = fin_data.get("overview", {})
        debt_list = fin_data.get("students_debt", [])

        f1, f2, f3, f4 = st.columns(4)
        f1.metric("Tổng học phí cam kết", f"{overview.get('total_tuition', 0):,.0f} đ")
        f2.metric("Đã thu thực tế", f"{overview.get('total_paid', 0):,.0f} đ")
        f3.metric("Tổng công nợ còn lại", f"{overview.get('total_remaining', 0):,.0f} đ")
        f4.metric("Tỷ lệ thu học phí", f"{overview.get('collection_rate', 0)}%")

        section_header("📋 Bảng công nợ chi tiết học viên")
        for s in debt_list:
            sid = s.get("id")
            remaining = s.get("remaining", 0) or 0
            fee = s.get("tuition_fee", 0) or 0
            paid = s.get("paid", 0) or 0
            percent = min(paid / fee * 100, 100) if fee > 0 else 0
            badge = '<span class="badge-danger">Còn nợ</span>' if remaining > 0 else '<span class="badge-success">Đã hoàn tất</span>'

            with st.container(border=True):
                col_d1, col_d2, col_d3, col_d4, col_d5 = st.columns([2.5, 1.5, 1.5, 1.8, 1.4])
                col_d1.markdown(
                    f'''
                    <div class="row-title">{esc(s.get("full_name"))}</div>
                    <div class="row-sub">Mã: <b>{esc(s.get("student_code"))}</b> · Đã đóng {percent:.0f}%</div>
                    <div class="progress-track"><div class="progress-fill" style="width:{percent:.0f}%;"></div></div>
                    ''',
                    unsafe_allow_html=True
                )
                col_d2.markdown(f'<div class="cell-label">Tổng học phí</div><div class="cell-value">{fee:,.0f}đ</div>', unsafe_allow_html=True)
                col_d3.markdown(f'<div class="cell-label">Đã đóng</div><div class="cell-value">{paid:,.0f}đ</div>', unsafe_allow_html=True)
                col_d4.markdown(f'<div class="cell-label">Còn nợ</div><div class="cell-value">{remaining:,.0f}đ</div>{badge}', unsafe_allow_html=True)

                with col_d5:
                    with st.popover("💵 Đóng tiền"):
                        with st.form(f"pay_form_{sid}"):
                            amount_pay = st.number_input("Số tiền đóng (VNĐ)", min_value=0.0, value=min(remaining, 5000000.0) if remaining > 0 else 1000000.0, step=500000.0, format="%.0f")
                            method_pay = st.selectbox("Phương thức", ["Tiền mặt", "Chuyển khoản", "Thẻ"], key=f"m_{sid}")
                            note_pay = st.text_input("Ghi chú", key=f"n_{sid}")

                            if st.form_submit_button("Xác nhận thu tiền", type="primary"):
                                p_payload = {
                                    "student_id": int(sid),
                                    "amount": float(amount_pay),
                                    "payment_method": method_pay,
                                    "note": note_pay or None
                                }
                                try:
                                    pres = requests.post(f"{BACKEND_URL}/payments", json=p_payload, timeout=10)
                                    pres.raise_for_status()
                                    st.success("✅ Ghi nhận thanh toán thành công!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Lỗi: {e}")

# =========================================================
# 8. TRỢ LÝ AI TRUNG TÂM
# =========================================================

elif menu == "🤖 Trợ lý AI Trung tâm":
    page_header("🤖 Trợ Lý AI Trung Tâm Pro", "Hỏi đáp tự do mọi thông tin vận hành, tra cứu học viên và nhận báo cáo thông minh từ AI")

    if "ai_center_chat" not in st.session_state:
        st.session_state.ai_center_chat = []

    user_q = st.chat_input("Nhập câu hỏi tự do cho trợ lý AI (Ví dụ: Trung tâm có bao nhiêu học viên còn nợ học phí?)...")

    if user_q:
        st.session_state.ai_center_chat.append({"role": "user", "content": user_q})
        with st.spinner("🤖 Trợ lý AI đang suy nghĩ và truy vấn dữ liệu..."):
            try:
                chat_payload = {"question": user_q}
                res = requests.post(f"{BACKEND_URL}/ai/chat", json=chat_payload, timeout=40)
                res.raise_for_status()
                ans_data = res.json().get("data", {})
                answer = ans_data.get("answer", "Không nhận được phản hồi từ AI.")
            except Exception as e:
                answer = f"⚠️ Không thể kết nối đến AI Backend (`/ai/chat`): {e}"

        st.session_state.ai_center_chat.append({"role": "assistant", "content": answer})

    if not st.session_state.ai_center_chat:
        st.info("💬 Hãy đặt câu hỏi ở ô nhập phía dưới để bắt đầu trò chuyện với trợ lý AI.")

    for msg in st.session_state.ai_center_chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# =========================================================
# 9. QUẢN LÝ TÀI KHOẢN & PHÂN QUYỀN (CÓ TÍNH NĂNG SỬA & XÓA)
# =========================================================

elif menu == "🔑 Quản lý tài khoản":
    page_header("🔑 Quản Lý Tài Khoản & Phân Quyền Hệ Thống", "Tạo mới, chỉnh sửa thông tin hoặc xóa tài khoản phân quyền trong trung tâm")

    with st.expander("➕ Tạo tài khoản phân quyền mới", expanded=False):
        with st.form("create_account_form"):
            new_user = st.text_input("Tên đăng nhập (Username) *", placeholder="VD: ketoan_02")
            new_pass = st.text_input("Mật khẩu *", type="password", placeholder="Nhập mật khẩu...")
            new_name = st.text_input("Họ và tên hiển thị *", placeholder="VD: Nguyễn Thị Lan")
            new_role = st.selectbox("Phân quyền hệ thống", ["Quản lý", "Giáo viên", "Kế toán"])

            if st.form_submit_button("💾 Tạo tài khoản mới", use_container_width=True, type="primary"):
                if new_user.strip() and new_pass.strip() and new_name.strip():
                    if new_user.strip() in st.session_state.users_db:
                        st.error("❌ Tên đăng nhập này đã tồn tại trong hệ thống!")
                    else:
                        st.session_state.users_db[new_user.strip()] = {
                            "password": new_pass.strip(),
                            "role": new_role,
                            "name": new_name.strip()
                        }
                        st.success(f"✅ Đã tạo thành công tài khoản **{new_user.strip()}**!")
                        st.rerun()
                else:
                    st.warning("⚠️ Vui lòng điền đầy đủ thông tin tài khoản.")

    section_header("📋 Danh sách tài khoản đang hoạt động")

    for idx, (u_id, u_info) in enumerate(list(st.session_state.users_db.items())):
        with st.container(border=True):
            col_u1, col_u3, col_u4 = st.columns([4.8, 1, 1])
            with col_u1:
                st.markdown(
                    f'''
                    <div class="row-flex">
                        {avatar_html(u_info["name"], idx)}
                        <div class="row-main">
                            <div class="row-title">{esc(u_info["name"])}</div>
                            <div class="row-sub">Username: <b>{esc(u_id)}</b> · 🛡️ <span class="badge-info">{esc(u_info["role"])}</span>
                            &nbsp;<span class="badge-success">Đang hoạt động</span></div>
                        </div>
                    </div>
                    ''',
                    unsafe_allow_html=True
                )
            with col_u3:
                if st.button("✏️ Sửa", key=f"edit_u_{u_id}", use_container_width=True):
                    st.session_state.editing_user = u_id
            with col_u4:
                if u_id == "admin":
                    st.caption("🔒 Cố định")
                else:
                    if st.button("🗑️ Xóa", key=f"del_u_{u_id}", use_container_width=True, type="secondary"):
                        del st.session_state.users_db[u_id]
                        st.success(f"Đã xóa tài khoản {u_id} thành công!")
                        st.rerun()

        if st.session_state.get("editing_user") == u_id:
            with st.form(f"edit_form_{u_id}"):
                st.markdown(f"##### ✏️ Chỉnh sửa tài khoản: `{u_id}`")
                edit_name = st.text_input("Họ và tên hiển thị", value=u_info["name"])
                edit_pass = st.text_input("Mật khẩu mới", value=u_info["password"], type="password")
                edit_role = st.selectbox("Phân quyền", ["Quản lý", "Giáo viên", "Kế toán"], index=["Quản lý", "Giáo viên", "Kế toán"].index(u_info["role"]))

                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    if st.form_submit_button("💾 Lưu thay đổi", type="primary", use_container_width=True):
                        st.session_state.users_db[u_id] = {
                            "password": edit_pass.strip(),
                            "role": edit_role,
                            "name": edit_name.strip()
                        }
                        st.session_state.editing_user = None
                        st.success("✅ Cập nhật tài khoản thành công!")
                        st.rerun()
                with col_e2:
                    if st.form_submit_button("❌ Hủy", use_container_width=True):
                        st.session_state.editing_user = None
                        st.rerun()
