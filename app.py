import streamlit as st
import requests
import io
import pandas as pd
from datetime import date
import html as _html
import streamlit.components.v1 as components
# =========================================================
# CẤU HÌNH TRANG & GIAO DIỆN CAO CẤP (PRO UI/UX)
# =========================================================
BACKEND_URL = "http://127.0.0.1:8000"
st.set_page_config(
    page_title="Hệ Thống Đào Tạo Lái Xe AI Pro",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

/* ===== RESET & BASE ===== */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
    color: #0f172a;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}
body {
    background: #f1f5f9;
}
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 5rem;
    max-width: 1280px;
    margin: 0 auto;
}
/* Hide default streamlit chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
/* ===== FIX: giữ nút mở lại sidebar luôn hiển thị khi đã thu gọn ===== */
/* Khi header bị ẩn, nút ">_" mở lại sidebar cũng bị ẩn theo -> giữ nó hiển thị */
header [data-testid="collapsedControl"],
header [data-testid="stSidebarCollapsedControl"] {
    visibility: visible !important;
    opacity: 1 !important;
}
header [data-testid="collapsedControl"] button,
header [data-testid="stSidebarCollapsedControl"] button {
    background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%) !important;
    color: #ffffff !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 14px rgba(59,130,246,0.4) !important;
    border: none !important;
    transition: all 0.25s ease !important;
}
header [data-testid="collapsedControl"] button:hover,
header [data-testid="stSidebarCollapsedControl"] button:hover {
    transform: translateY(-1px) scale(1.05) !important;
    box-shadow: 0 6px 18px rgba(59,130,246,0.55) !important;
}

/* ===== FIX v2: header trong suốt + nhiều selector dự phòng mọi phiên bản Streamlit ===== */
header {
    visibility: visible !important;
    background: transparent !important;
    box-shadow: none !important;
    border-bottom: none !important;
    pointer-events: none !important;
}
/* Hiển thị mạnh mọi dạng nút mở lại sidebar (toàn cục, không giới hạn trong header) */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] *,
[data-testid="stSidebarCollapsedControl"] * {
    visibility: visible !important;
    opacity: 1 !important;
    display: flex !important;
    pointer-events: auto !important;
}
/* Ẩn các phần rác của header (menu hamburger, nút deploy, status widget) */
header [data-testid="stToolbar"],
header [data-testid="stMainMenu"],
header [data-testid="stDeployButton"],
header [data-testid="stStatusWidget"],
header [data-testid="stToolbarActions"],
header [data-testid="stHeaderActionElements"] {
    visibility: hidden !important;
    display: none !important;
}
/* Style nút mở lại sidebar cho dễ thấy ở mọi phiên bản */
[data-testid="collapsedControl"] button,
[data-testid="stSidebarCollapsedControl"] button,
header button[kind="header"] {
    background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%) !important;
    color: #ffffff !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 14px rgba(59,130,246,0.45) !important;
    border: none !important;
    visibility: visible !important;
    pointer-events: auto !important;
}
/* ===== SCROLLBAR ===== */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

/* ===== FIX v3: NGĂN THU GỌN SIDEBAR (tránh mất menu) + hiển thị mạnh nút mở lại ===== */
/* Ẩn nút × thu gọn sidebar -> người dùng không thể thu gọn => menu luôn hiện */
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"],
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] button,
section[data-testid="stSidebar"] button[kind="header"],
section[data-testid="stSidebar"] button[aria-label*="sidebar" i] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    width: 0 !important;
    height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    overflow: hidden !important;
}
/* Hiển thị mạnh nút mở lại sidebar (nếu đang bị thu gọn) bằng mọi selector có thể */
header button[aria-label*="sidebar" i],
header button[title*="sidebar" i],
header [data-testid="collapsedControl"] button,
header [data-testid="stSidebarCollapsedControl"] button,
header button[kind="header"] {
    visibility: visible !important;
    opacity: 1 !important;
    display: inline-flex !important;
    pointer-events: auto !important;
    background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%) !important;
    color: #ffffff !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 16px rgba(59,130,246,0.5) !important;
    border: none !important;
    padding: 8px 16px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
}
/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1220 0%, #131c2e 50%, #0f172a 100%) !important;
    border-right: none !important;
    box-shadow: 4px 0 24px rgba(0,0,0,0.15);
}
section[data-testid="stSidebar"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #3b82f6, #06b6d4, #8b5cf6);
    z-index: 1000;
}
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stRadio label {
    color: #e2e8f0 !important;
}
.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 18px 14px;
    background: linear-gradient(135deg, rgba(59,130,246,0.12) 0%, rgba(6,182,212,0.08) 100%);
    border-radius: 16px;
    margin-bottom: 20px;
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(10px);
}
.sidebar-brand-icon {
    width: 46px; height: 46px;
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px;
    box-shadow: 0 4px 14px rgba(59,130,246,0.4);
    flex-shrink: 0;
}
.sidebar-title {
    font-size: 15px;
    font-weight: 800;
    background: linear-gradient(135deg, #60a5fa 0%, #22d3ee 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    line-height: 1.3;
    letter-spacing: 0.3px;
}
.sidebar-subtitle {
    color: #94a3b8 !important;
    font-size: 11px;
    margin: 2px 0 0 0 !important;
    font-weight: 500;
}
.sidebar-menu-label {
    font-size: 10px;
    color: #64748b !important;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin: 8px 4px 10px 4px !important;
    padding-left: 4px;
}

/* ===== NAV RADIO ITEMS ===== */
div[data-testid="stRadio"] > div {
    gap: 2px;
}
div[data-testid="stRadio"] label {
    padding: 11px 14px !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    margin-bottom: 2px !important;
    cursor: pointer;
    border: 1px solid transparent;
    position: relative;
}
div[data-testid="stRadio"] label:hover {
    background: rgba(59,130,246,0.12) !important;
    border-color: rgba(59,130,246,0.2);
    transform: translateX(3px);
}
div[data-testid="stRadio"] label[data-checked="true"] {
    background: linear-gradient(135deg, rgba(59,130,246,0.25) 0%, rgba(6,182,212,0.15) 100%) !important;
    border-color: rgba(59,130,246,0.4) !important;
    box-shadow: 0 2px 12px rgba(59,130,246,0.2);
}
div[data-testid="stRadio"] label[data-checked="true"]::before {
    content: '';
    position: absolute;
    left: -10px; top: 50%;
    transform: translateY(-50%);
    width: 3px; height: 22px;
    background: linear-gradient(180deg, #3b82f6, #06b6d4);
    border-radius: 3px;
}

/* ===== PAGE TITLES ===== */
.page-title {
    font-size: 28px;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.6px;
    margin-bottom: 6px;
    line-height: 1.2;
}
.page-subtitle {
    color: #64748b;
    font-size: 14px;
    margin-bottom: 28px;
    font-weight: 500;
    line-height: 1.5;
}
.page-header-accent {
    display: inline-block;
    width: 40px; height: 4px;
    background: linear-gradient(90deg, #3b82f6, #06b6d4);
    border-radius: 4px;
    margin-bottom: 18px;
}

/* ===== CARDS / CONTAINERS ===== */
div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 18px 22px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    margin-bottom: 12px;
    animation: fadeSlideIn 0.4s ease-out;
}
div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"]:hover {
    box-shadow: 0 8px 24px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.04);
    border-color: #cbd5e1;
    transform: translateY(-1px);
}
@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ===== METRIC CARDS ===== */
div[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 16px 18px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
    animation: fadeSlideIn 0.4s ease-out;
}
div[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    background: linear-gradient(180deg, #3b82f6, #06b6d4);
}
div[data-testid="stMetric"]:hover {
    box-shadow: 0 6px 20px rgba(0,0,0,0.08);
    transform: translateY(-2px);
    border-color: #cbd5e1;
}
div[data-testid="stMetric"] label[data-testid="stMetricLabel"] {
    font-size: 12px !important;
    font-weight: 600 !important;
    color: #64748b !important;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    font-size: 26px !important;
    font-weight: 800 !important;
    color: #0f172a !important;
    margin-top: 4px;
}

/* ===== BADGES ===== */
.badge-danger {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 5px 12px;
    background: linear-gradient(135deg, #fef2f2, #fee2e2);
    color: #dc2626;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    border: 1px solid #fecaca;
    letter-spacing: 0.2px;
}
.badge-danger::before {
    content: '';
    width: 6px; height: 6px;
    background: #ef4444;
    border-radius: 50%;
    box-shadow: 0 0 0 3px rgba(239,68,68,0.2);
}
.badge-success {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 5px 12px;
    background: linear-gradient(135deg, #f0fdf4, #dcfce7);
    color: #16a34a;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    border: 1px solid #bbf7d0;
    letter-spacing: 0.2px;
}
.badge-success::before {
    content: '';
    width: 6px; height: 6px;
    background: #22c55e;
    border-radius: 50%;
    box-shadow: 0 0 0 3px rgba(34,197,94,0.2);
}
.badge-info {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 5px 12px;
    background: linear-gradient(135deg, #eff6ff, #dbeafe);
    color: #2563eb;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    border: 1px solid #bfdbfe;
    letter-spacing: 0.2px;
}
.student-code {
    display: inline-block;
    padding: 3px 10px;
    background: linear-gradient(135deg, #eff6ff, #e0e7ff);
    color: #4f46e5;
    font-size: 11px;
    font-weight: 700;
    border-radius: 8px;
    margin-bottom: 6px;
    letter-spacing: 0.5px;
    border: 1px solid #c7d2fe;
}

/* ===== BUTTONS ===== */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    border: none !important;
    letter-spacing: 0.2px;
}
.stButton > button:hover {
    transform: translateY(-1.5px);
    box-shadow: 0 6px 16px rgba(59,130,246,0.35) !important;
}
.stButton > button:active {
    transform: translateY(0);
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    box-shadow: 0 2px 8px rgba(59,130,246,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    box-shadow: 0 8px 20px rgba(59,130,246,0.45) !important;
}
.stButton > button[kind="secondary"] {
    background: #f1f5f9 !important;
    color: #334155 !important;
    border: 1px solid #e2e8f0 !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #e2e8f0 !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
}

/* Sidebar logout button */
section[data-testid="stSidebar"] button[kind="secondary"] {
    background: linear-gradient(135deg, rgba(239,68,68,0.15), rgba(239,68,68,0.08)) !important;
    color: #f87171 !important;
    border: 1px solid rgba(239,68,68,0.3) !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    transition: all 0.25s ease !important;
}
section[data-testid="stSidebar"] button[kind="secondary"]:hover {
    background: linear-gradient(135deg, #ef4444, #dc2626) !important;
    color: #ffffff !important;
    border-color: #ef4444 !important;
    box-shadow: 0 4px 16px rgba(239,68,68,0.4) !important;
    transform: translateY(-1px);
}

/* ===== FORM INPUTS ===== */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div,
.stDateInput > div > div > input {
    border-radius: 10px !important;
    border: 1.5px solid #e2e8f0 !important;
    background: #f8fafc !important;
    transition: all 0.2s ease !important;
    font-size: 14px !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stSelectbox > div > div > div:focus-within,
.stDateInput > div > div > input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
    background: #ffffff !important;
}
.stTextInput label, .stNumberInput label, .stTextArea label,
.stSelectbox label, .stDateInput label, .stCheckbox label {
    font-weight: 600 !important;
    font-size: 13px !important;
    color: #334155 !important;
    margin-bottom: 4px !important;
}

/* ===== EXPANDER ===== */
.streamlit-expanderHeader {
    background: linear-gradient(135deg, #f8fafc, #f1f5f9) !important;
    border-radius: 12px !important;
    border: 1px solid #e2e8f0 !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    color: #1e293b !important;
    padding: 14px 18px !important;
    transition: all 0.2s ease !important;
}
.streamlit-expanderHeader:hover {
    border-color: #3b82f6 !important;
    box-shadow: 0 2px 8px rgba(59,130,246,0.15) !important;
}
.streamlit-expanderContent {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-top: none;
    border-radius: 0 0 12px 12px;
    padding: 16px 18px !important;
    margin-top: -4px;
}

/* ===== INFO / SUCCESS / ERROR / WARNING BOXES ===== */
.stAlert {
    border-radius: 12px !important;
    border: none !important;
    padding: 14px 18px !important;
    font-size: 14px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
}
.stAlert[data-testid="stAlertInfo"] {
    background: linear-gradient(135deg, #eff6ff, #dbeafe) !important;
    color: #1e40af !important;
    border-left: 4px solid #3b82f6 !important;
}
.stAlert[data-testid="stAlertSuccess"] {
    background: linear-gradient(135deg, #f0fdf4, #dcfce7) !important;
    color: #166534 !important;
    border-left: 4px solid #22c55e !important;
}
.stAlert[data-testid="stAlertError"] {
    background: linear-gradient(135deg, #fef2f2, #fee2e2) !important;
    color: #991b1b !important;
    border-left: 4px solid #ef4444 !important;
}
.stAlert[data-testid="stAlertWarning"] {
    background: linear-gradient(135deg, #fffbeb, #fef3c7) !important;
    color: #92400e !important;
    border-left: 4px solid #f59e0b !important;
}

/* ===== CHAT ===== */
.stChatMessage {
    border-radius: 16px !important;
    padding: 12px 16px !important;
    margin-bottom: 10px !important;
}
.stChatMessage[data-testid="stChatMessage-user"] {
    background: linear-gradient(135deg, #eff6ff, #dbeafe) !important;
    border: 1px solid #bfdbfe;
}
.stChatMessage[data-testid="stChatMessage-assistant"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

/* ===== POPOVER ===== */
[data-testid="stPopover"] button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    background: linear-gradient(135deg, #f0fdf4, #dcfce7) !important;
    color: #16a34a !important;
    border: 1px solid #bbf7d0 !important;
    transition: all 0.2s ease !important;
}
[data-testid="stPopover"] button:hover {
    background: linear-gradient(135deg, #dcfce7, #bbf7d0) !important;
    box-shadow: 0 4px 12px rgba(34,197,94,0.25) !important;
    transform: translateY(-1px);
}

/* ===== TABS (if any) ===== */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: #f1f5f9;
    padding: 6px;
    border-radius: 12px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}
.stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #2563eb !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}

/* ===== DATAFRAME / TABLE ===== */
.stDataFrame {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid #e2e8f0 !important;
}

/* ===== DIVIDER ===== */
hr[data-testid="stDivider"] {
    border-color: #e2e8f0 !important;
    margin: 20px 0 !important;
}

/* ===== CAPTION ===== */
.stCaption {
    font-size: 11px !important;
    color: #94a3b8 !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 2px !important;
}

/* ===== LOGIN PAGE BACKGROUND ===== */
.login-bg {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 40%, #0f172a 100%);
    z-index: -1;
    overflow: hidden;
}
.login-bg::before {
    content: '';
    position: absolute;
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(59,130,246,0.3) 0%, transparent 70%);
    top: -100px; right: -100px;
    border-radius: 50%;
    animation: float 8s ease-in-out infinite;
}
.login-bg::after {
    content: '';
    position: absolute;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(6,182,212,0.25) 0%, transparent 70%);
    bottom: -80px; left: -80px;
    border-radius: 50%;
    animation: float 10s ease-in-out infinite reverse;
}
@keyframes float {
    0%, 100% { transform: translate(0, 0); }
    50% { transform: translate(30px, -30px); }
}
.login-card {
    background: rgba(255,255,255,0.98);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    padding: 40px 36px;
    box-shadow: 0 25px 60px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.1);
    animation: fadeSlideIn 0.6s ease-out;
    border: 1px solid rgba(255,255,255,0.2);
}
.login-logo {
    width: 64px; height: 64px;
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    border-radius: 18px;
    display: flex; align-items: center; justify-content: center;
    font-size: 32px;
    margin: 0 auto 16px;
    box-shadow: 0 8px 24px rgba(59,130,246,0.4);
}

/* ===== PROFILE HEADER CARD ===== */
.profile-header-card {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
    border-radius: 16px;
    padding: 24px 28px;
    color: white;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 24px rgba(15,23,42,0.3);
}
.profile-header-card::before {
    content: '';
    position: absolute;
    top: -50%; right: -10%;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(59,130,246,0.3) 0%, transparent 70%);
    border-radius: 50%;
}
.profile-header-card::after {
    content: '';
    position: absolute;
    bottom: -30%; left: 20%;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(6,182,212,0.2) 0%, transparent 70%);
    border-radius: 50%;
}

/* ===== SECTION HEADER ===== */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 24px 0 16px 0;
}
.section-header-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, #e2e8f0, transparent);
}
.section-header-title {
    font-size: 16px;
    font-weight: 700;
    color: #1e293b;
    white-space: nowrap;
}

/* ===== AVATAR ===== */
.avatar-circle {
    width: 42px; height: 42px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 15px;
    color: white;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

/* ===== PROGRESS BAR ===== */
.progress-track {
    width: 100%;
    height: 6px;
    background: #e2e8f0;
    border-radius: 10px;
    overflow: hidden;
    margin-top: 4px;
}
.progress-fill {
    height: 100%;
    border-radius: 10px;
    background: linear-gradient(90deg, #3b82f6, #06b6d4);
    transition: width 0.6s ease;
}

/* ===== CHART CONTAINER ===== */
[data-testid="stArrowVegaLiteChart"] {
    background: #ffffff;
    border-radius: 14px;
    padding: 12px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

/* ===== CHECKBOX ===== */
.stCheckbox [data-baseweb="checkbox"] {
    border-radius: 6px !important;
}

/* ===== SPINNER ===== */
.stSpinner > div {
    border-color: #3b82f6 !important;
    border-right-color: transparent !important;
}
</style>
""", unsafe_allow_html=True)

# ===== FIX: Nút ☰ nổi thông minh (chỉ hiện khi sidebar đang thu gọn) để chắc chắn mở lại menu =====
st.markdown("""
<div id="ai-sidebar-toggle-fallback" style="display:none;position:fixed;top:14px;left:14px;z-index:999999;background:linear-gradient(135deg,#3b82f6,#06b6d4);color:#ffffff;border:none;border-radius:10px;padding:9px 16px;font-size:13px;font-weight:700;cursor:pointer;box-shadow:0 4px 16px rgba(59,130,246,0.5);font-family:'Plus Jakarta Sans','Inter',sans-serif;letter-spacing:0.3px;">☰ Mở Menu</div>
<script>
(function(){
  var btn = document.getElementById('ai-sidebar-toggle-fallback');
  if(!btn) return;
  function isSidebarCollapsed(){
    var sb = document.querySelector('section[data-testid="stSidebar"]');
    if(!sb) return true;
    if(sb.getAttribute('aria-expanded') === 'false') return true;
    if(sb.offsetWidth < 60) return true;
    return false;
  }
  function syncBtn(){
    btn.style.display = isSidebarCollapsed() ? 'block' : 'none';
  }
  btn.addEventListener('click', function(){
    // Thử mọi selector có thể của nút mở sidebar ở mọi phiên bản Streamlit
    var t = document.querySelector(
      '[data-testid="collapsedControl"] button, ' +
      '[data-testid="stSidebarCollapsedControl"] button, ' +
      'header button[kind="header"], ' +
      '[data-testid="collapsedControl"], ' +
      '[data-testid="stSidebarCollapsedControl"]'
    );
    if(t){ t.click(); }
    else {
      // Dự phòng cuối: cố gắng click vào vùng sidebar collapsed
      var sb = document.querySelector('section[data-testid="stSidebar"]');
      if(sb) sb.click();
    }
  });
  syncBtn();
  setInterval(syncBtn, 600);
})();
</script>
""", unsafe_allow_html=True)

# =========================================================
# FIX v4: JS thật (components.html) - tự động hiển thị nút mở lại sidebar
# Chạy trong iframe same-origin, truy cập được window.parent.document
# =========================================================
components.html("""
<script>
(function(){
  var doc = window.parent.document;
  function findExpandBtn(){
    var sels = [
      '[data-testid="collapsedControl"] button',
      '[data-testid="stSidebarCollapsedControl"] button',
      'header button[kind="header"]',
      'header button[aria-label*="sidebar" i]',
      'header button[title*="sidebar" i]',
      '[data-testid="collapsedControl"]',
      '[data-testid="stSidebarCollapsedControl"]'
    ];
    for(var i=0;i<sels.length;i++){
      var el = doc.querySelector(sels[i]);
      if(el){
        if(el.tagName === 'BUTTON') return el;
        var b = el.querySelector('button');
        return b || el;
      }
    }
    var hdr = doc.querySelector('header');
    if(hdr){
      var btns = hdr.querySelectorAll('button');
      if(btns.length) return btns[0];
    }
    return null;
  }
  function isCollapsed(){
    var sb = doc.querySelector('section[data-testid="stSidebar"]');
    if(!sb) return true;
    if(sb.getAttribute('aria-expanded') === 'false') return true;
    if(sb.offsetWidth < 60) return true;
    return false;
  }
  function ensure(){
    // 1. Bỏ ẩn header (nguyên nhân làm mất nút mở)
    var hdr = doc.querySelector('header');
    if(hdr){
      hdr.style.visibility = 'visible';
      hdr.style.background = 'transparent';
      hdr.style.boxShadow = 'none';
      hdr.style.borderBottom = 'none';
      hdr.style.pointerEvents = 'none';
    }
    // 2. Hiện & style nút mở lại sidebar (nếu có)
    var btn = findExpandBtn();
    if(btn){
      btn.style.visibility = 'visible';
      btn.style.opacity = '1';
      btn.style.display = 'inline-flex';
      btn.style.pointerEvents = 'auto';
      btn.style.background = 'linear-gradient(135deg,#3b82f6,#06b6d4)';
      btn.style.color = '#ffffff';
      btn.style.borderRadius = '10px';
      btn.style.padding = '8px 16px';
      btn.style.boxShadow = '0 4px 16px rgba(59,130,246,0.5)';
      btn.style.border = 'none';
      btn.style.fontWeight = '700';
      btn.style.fontSize = '13px';
      btn.style.zIndex = '99999';
      var txt = (btn.textContent || '').trim();
      if(txt.length < 2){ btn.textContent = '☰ Menu'; }
    }
    // 3. Đảm bảo nút thu gọn (×) luôn hiện (để user có thể thu gọn)
    var sbSec = doc.querySelector('section[data-testid="stSidebar"]');
    if(sbSec){
      var sbBtns = sbSec.querySelectorAll('button');
      for(var j=0;j<sbBtns.length;j++){
        sbBtns[j].style.display = 'inline-flex';
        sbBtns[j].style.visibility = 'visible';
        sbBtns[j].style.opacity = '1';
        sbBtns[j].style.width = 'auto';
        sbBtns[j].style.height = 'auto';
      }
    }
    // 4. Tạo nút nổi đảm bảo (chỉ hiện khi sidebar đang thu gọn)
    var fb = doc.getElementById('ai-float-menu-btn');
    if(!fb){
      fb = doc.createElement('div');
      fb.id = 'ai-float-menu-btn';
      fb.textContent = '☰ Mở Menu';
      fb.style.cssText = 'position:fixed;top:14px;left:14px;z-index:2147483647;background:linear-gradient(135deg,#3b82f6,#06b6d4);color:#ffffff;border-radius:10px;padding:9px 16px;font-size:13px;font-weight:700;cursor:pointer;box-shadow:0 4px 16px rgba(59,130,246,0.5);font-family:sans-serif;display:none;';
      fb.addEventListener('click', function(){
        var b = findExpandBtn();
        if(b){ b.click(); }
      });
      doc.body.appendChild(fb);
    }
    fb.style.display = isCollapsed() ? 'block' : 'none';
  }
  ensure();
  setInterval(ensure, 700);
})();
</script>
""", height=0)

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
# Màn hình Đăng nhập Pro
if not st.session_state.logged_in:
    st.markdown('<div class="login-bg"></div>', unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
    with col_l2:
        st.markdown('''
        <div class="login-card">
            <div class="login-logo">🚗</div>
            <h2 style="text-align: center; color: #0f172a; font-weight: 800; font-size: 24px; margin: 0 0 6px 0; letter-spacing: -0.5px;">Đào Tạo Lái Xe AI Pro</h2>
            <p style="text-align: center; color: #64748b; font-size: 13px; margin-bottom: 28px; font-weight: 500;">Hệ thống quản lý trung tâm thông minh</p>
        </div>
        ''', unsafe_allow_html=True)
        with st.container():
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
                        st.success(f"Đăng nhập thành công với quyền **{user_info['role']}**!")
                        st.rerun()
                    else:
                        st.error("❌ Tên đăng nhập hoặc mật khẩu không chính xác!")
            
            st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 11px; margin-top: 18px;'>💡 Tài khoản mẫu: <b>admin</b> / 123 (Quản lý) | <b>teacher</b> / 123 (Giáo viên) | <b>accountant</b> / 123 (Kế toán)</p>", unsafe_allow_html=True)
    st.stop()
# =========================================================
# CÁC HÀM GỌI BACKEND API
# =========================================================
BACKEND_URL = "http://127.0.0.1:8000"
def api_get(endpoint, params=None):
    try:
        response = requests.get(f"{BACKEND_URL}{endpoint}", params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Không thể kết nối đến Backend (`http://127.0.0.1:8000`). Hãy đảm bảo server FastAPI đã khởi động!")
        return None
    except Exception:
        return None
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
                <p class="sidebar-subtitle"><b>{st.session_state.user_name}</b> · {st.session_state.user_role}</p>
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
    
    # Nút Đăng xuất được đặt màu trắng nổi bật rõ trên nền tối của sidebar
    if st.button("🚪 Đăng xuất tài khoản", use_container_width=True, type="secondary"):
        st.session_state.logged_in = False
        st.rerun()
students = get_students()
# =========================================================
# 1. TỔNG QUAN
# =========================================================
if menu == "📊 Tổng quan":
    st.markdown('<div class="page-title">📊 Tổng Quan Hệ Thống Trung Tâm</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-header-accent"></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Thống kê hoạt động, tài chính và tiến độ đào tạo theo thời gian thực</div>', unsafe_allow_html=True)
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
    st.write("")
    st.markdown('<div class="section-header"><span class="section-header-title">📈 Biểu đồ phân tích trực quan</span><span class="section-header-line"></span></div>', unsafe_allow_html=True)
    
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
    st.markdown('<div class="page-title">👨‍🎓 Quản Lý Học Viên & Báo Cáo</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-header-accent"></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Thêm mới, tìm kiếm, tra cứu hồ sơ chi tiết và xuất danh sách học viên ra Excel</div>', unsafe_allow_html=True)
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
        } for s in students])
        
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
                    try:
                        res = requests.post(f"{BACKEND_URL}/students", json=payload, timeout=10)
                        res.raise_for_status()
                        st.success("✅ Thêm học viên thành công!")
                        st.rerun()
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
    if debt_only: params["debt_only"] = "true"
    if min_score > 0: params["min_score"] = min_score
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
            score_text = f"{score:.2f}" if score is not None else "Chưa có"
            remaining = student.get("tuition", {}).get("remaining", 0)
            badge_tuition = '<span class="badge-danger">Còn nợ</span>' if remaining > 0 else '<span class="badge-success">Đã hoàn tất</span>'
            with st.container():
                c1, c2, c3, c4, c5, c6 = st.columns([2.2, 2, 1, 1, 1.2, 1.4])
                with c1:
                    st.markdown(f'<span class="student-code">{code}</span>', unsafe_allow_html=True)
                    st.markdown(f'<div style="font-weight: 700; font-size: 15px; color: #0f172a;">{name}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="color: #64748b; font-size: 11px; margin-top: 2px;">📞 {phone or "Chưa có"}</div>', unsafe_allow_html=True)
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
                    st.write(f"**{score_text}**")
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
                                <div style="font-size: 20px; font-weight: 800; letter-spacing: -0.3px;">👤 Hồ sơ chi tiết: {p_student.get('full_name')}</div>
                                <div style="color: #94a3b8; font-size: 12px; margin-top: 6px; display: flex; gap: 16px; flex-wrap: wrap;">
                                    <span>📋 Mã HV: <b style="color: #60a5fa;">{p_student.get('student_code')}</b></span>
                                    <span>🎯 Hạng bằng: <b style="color: #60a5fa;">{p_student.get('license_class')}</b></span>
                                    <span>📌 Trạng thái: <b style="color: #34d399;">{p_student.get('status')}</b></span>
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
    st.markdown('<div class="page-title">👨‍🏫 Quản Lý Giáo Viên Trung Tâm</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-header-accent"></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Thêm mới, cập nhật thông tin và trạng thái giảng dạy của giáo viên</div>', unsafe_allow_html=True)
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
    st.markdown('<div class="section-header"><span class="section-header-title">📋 Danh sách giáo viên</span><span class="section-header-line"></span></div>', unsafe_allow_html=True)
    for t in teachers:
        with st.container():
            st.write(f"👨‍🏫 **{t.get('full_name')}** (Mã: `{t.get('teacher_code')}`) — SĐT: {t.get('phone', 'Chưa có')} — Trạng thái: **{t.get('status')}**")
# =========================================================
# 4. QUẢN LÝ XE TẬP LÁI
# =========================================================
elif menu == "🚗 Quản lý xe":
    st.markdown('<div class="page-title">🚗 Quản Lý Phương Tiện & Xe Tập Lái</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-header-accent"></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Quản lý biển số xe, hãng sản xuất, dòng xe và trạng thái bảo dưỡng</div>', unsafe_allow_html=True)
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
    st.markdown('<div class="section-header"><span class="section-header-title">📋 Danh sách phương tiện</span><span class="section-header-line"></span></div>', unsafe_allow_html=True)
    for v in vehicles:
        with st.container():
            st.write(f"🚗 Biển số: **{v.get('plate_number')}** — {v.get('brand')} {v.get('model')} (Hạng: {v.get('license_class')}) — Trạng thái: **{v.get('status')}**")
# =========================================================
# 5. LỊCH HỌC & BUỔI HỌC (CHỐNG TRÙNG LỊCH & XUẤT EXCEL)
# =========================================================
elif menu == "📚 Lịch học & Buổi học":
    st.markdown('<div class="page-title">📚 Quản Lý Lịch Học & Xếp Lịch Thông Minh</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-header-accent"></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Xếp lịch thực hành cho học viên, phân công giáo viên và xe tránh trùng giờ</div>', unsafe_allow_html=True)
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
    st.markdown('<div class="section-header"><span class="section-header-title">📋 Lịch trình các buổi học gần đây</span><span class="section-header-line"></span></div>', unsafe_allow_html=True)
    for l in lessons:
        with st.container():
            st.info(f"📅 Ngày: **{l.get('lesson_date')}** | ⏰ Giờ: **{l.get('start_time')} - {l.get('end_time')}** | HV: **{l.get('student_name')}** | GV: **{l.get('teacher_name')}** | Xe: **{l.get('plate_number', 'Không có')}**")
# =========================================================
# 6. ĐÁNH GIÁ & AI PHÂN TÍCH KỸ NĂNG
# =========================================================
elif menu == "⭐ Đánh giá & AI":
    st.markdown('<div class="page-title">⭐ Đánh Giá Kỹ Năng & Trợ Lý AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-header-accent"></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Theo dõi điểm số chi tiết từng kỹ năng lái xe và nhận xét đánh giá từ AI</div>', unsafe_allow_html=True)
    evals = get_evaluations()
    st.metric("Tổng số đánh giá ghi nhận", len(evals))
    st.write("")
    for e in evals:
        eid = e.get("id")
        with st.container():
            st.markdown(f"**Học viên:** {e.get('student_name')} (Mã: {e.get('student_code')}) — Điểm tổng kết: **{e.get('score')} / 10**")
            st.caption(f"Nhận xét giáo viên: {e.get('comment', 'Không có')}")
            
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
    st.markdown('<div class="page-title">💰 Quản Lý Học Phí & Công Nợ</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-header-accent"></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Theo dõi tình hình đóng học phí, ghi nhận thanh toán và kiểm soát công nợ</div>', unsafe_allow_html=True)
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
        st.write("")
        st.markdown('<div class="section-header"><span class="section-header-title">📋 Bảng công nợ chi tiết học viên</span><span class="section-header-line"></span></div>', unsafe_allow_html=True)
        for s in debt_list:
            sid = s.get("id")
            remaining = s.get("remaining", 0)
            badge = '<span class="badge-danger">Còn nợ</span>' if remaining > 0 else '<span class="badge-success">Đã hoàn tất</span>'
            
            with st.container():
                col_d1, col_d2, col_d3, col_d4, col_d5 = st.columns([2.5, 1.5, 1.5, 1.5, 1.5])
                col_d1.write(f"**{s.get('full_name')}** (`{s.get('student_code')}`)")
                col_d2.write(f"Tổng: {s.get('tuition_fee', 0):,.0f}đ")
                col_d3.write(f"Đã đóng: {s.get('paid', 0):,.0f}đ")
                col_d4.markdown(f"Nợ: **{remaining:,.0f}đ** {badge}", unsafe_allow_html=True)
                
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
    st.markdown('<div class="page-title">🤖 Trợ Lý AI Trung Tâm Pro</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-header-accent"></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Hỏi đáp tự do mọi thông tin vận hành, tra cứu học viên và nhận báo cáo thông minh từ AI</div>', unsafe_allow_html=True)
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
    for msg in st.session_state.ai_center_chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
# =========================================================
# 9. QUẢN LÝ TÀI KHOẢN & PHÂN QUYỀN (CÓ TÍNH NĂNG SỬA & XÓA)
# =========================================================
elif menu == "🔑 Quản lý tài khoản":
    st.markdown('<div class="page-title">🔑 Quản Lý Tài Khoản & Phân Quyền Hệ Thống</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-header-accent"></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Tạo mới, chỉnh sửa thông tin hoặc xóa tài khoản phân quyền trong trung tâm</div>', unsafe_allow_html=True)
    # Form Thêm tài khoản mới
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
    st.markdown('<div class="section-header"><span class="section-header-title">📋 Danh sách tài khoản đang hoạt động</span><span class="section-header-line"></span></div>', unsafe_allow_html=True)
    
    for u_id, u_info in list(st.session_state.users_db.items()):
        with st.container():
            col_u1, col_u2, col_u3, col_u4, col_u5 = st.columns([2, 1.5, 1.2, 1, 1])
            with col_u1:
                st.write(f"👤 **{u_info['name']}**")
                st.caption(f"Username: `{u_id}`")
            with col_u2:
                st.write(f"🛡️ Quyền: **{u_info['role']}**")
            with col_u3:
                st.markdown('<span class="badge-success">Đang hoạt động</span>', unsafe_allow_html=True)
            with col_u4:
                # Nút Sửa tài khoản
                if st.button("✏️ Sửa", key=f"edit_u_{u_id}", use_container_width=True):
                    st.session_state.editing_user = u_id
            with col_u5:
                # Nút Xóa tài khoản (Không cho phép xóa tài khoản admin mặc định cuối cùng nếu muốn)
                if u_id == "admin":
                    st.caption("🔒 Cố định")
                else:
                    if st.button("🗑️ Xóa", key=f"del_u_{u_id}", use_container_width=True, type="secondary"):
                        del st.session_state.users_db[u_id]
                        st.success(f"Đã xóa tài khoản {u_id} thành công!")
                        st.rerun()
        # Hiển thị form chỉnh sửa nếu người dùng bấm nút Sửa
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
            st.divider()
