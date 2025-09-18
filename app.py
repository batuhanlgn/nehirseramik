# app.py
# -------------------------------------------------------------
# Nehir Seramik Atölyesi – İç Yönetim Sistemi (Mobil Uyumlu MVP)
# Tech: Streamlit + SQLModel (SQLAlchemy 2.x)
# DB: PostgreSQL (env: DATABASE_URL) veya fallback SQLite (nehir.db)
# -------------------------------------------------------------

import os
import calendar
from datetime import date, time as dtime, datetime, timedelta
from typing import Optional

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from sqlmodel import SQLModel, Field, Relationship, Session, create_engine, select, func

# Try to load .env file, but don't fail if dotenv is not available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, use environment variables directly

# ============================ CONFIG ============================
APP_TITLE = "Nehir Atölye Yönetim"
DEFAULT_DB = "sqlite:///nehir.db"  # env yoksa SQLite
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB)
ENGINE = create_engine(DATABASE_URL, echo=False)

DEFAULT_PRICE_COURSE = 500.0
DEFAULT_PRICE_BOYAMA = 250.0
DEFAULT_CAPACITY = 16

# Açılış kasası (opsiyonel): setx / export OPENING_CASH=1000
OPENING_CASH = float(os.getenv("OPENING_CASH", "0"))

# ============================ THEME ============================
def load_theme():
    css = """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');
      
      :root {
        /* Ultra-modern color system */
        --bg-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --bg-glass: rgba(255, 255, 255, 0.08);
        --bg-glass-hover: rgba(255, 255, 255, 0.12);
        --bg-card: rgba(255, 255, 255, 0.1);
        --bg-card-hover: rgba(255, 255, 255, 0.15);
        --glass-border: rgba(255, 255, 255, 0.2);
        --glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        --glass-blur: blur(8px);
        
        /* Text colors */
        --text-primary: #ffffff;
        --text-secondary: rgba(255, 255, 255, 0.8);
        --text-muted: rgba(255, 255, 255, 0.6);
        --text-dark: #1a1a1a;
        
        /* Brand colors with gradients */
        --brand-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --brand-secondary: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --brand-success: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --brand-warning: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        --brand-danger: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        --brand-info: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        
        /* Sizes and spacing */
        --radius: 16px;
        --radius-lg: 24px;
        --radius-xl: 32px;
        --spacing: 1.5rem;
        --shadow-glass: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        --shadow-float: 0 20px 40px 0 rgba(31, 38, 135, 0.5);
        
        /* Animation */
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        --transition-bounce: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
      }
      
      /* Force dark mode for all devices */
      html[data-theme="light"], 
      html:not([data-theme]),
      .stApp,
      [data-testid="stAppViewContainer"],
      section[data-testid="stSidebar"] {
        background: #0e1117 !important;
        color: #ffffff !important;
      }
      
      /* Force dark mode for specific Streamlit components */
      .stSelectbox > div > div,
      .stNumberInput > div > div > input,
      .stTextInput > div > div > input,
      .stTextArea > div > div > textarea,
      .stDateInput > div > div > input,
      .stTimeInput > div > div > input,
      .stMultiSelect > div > div,
      .stSlider > div > div > div,
      .stRadio > div,
      .stCheckbox > div {
        background-color: #262730 !important;
        color: #ffffff !important;
        border-color: #4a4a5a !important;
      }
      
      /* Force dark sidebar */
      section[data-testid="stSidebar"] > div {
        background-color: #262730 !important;
      }
      
      /* Force dark main area */
      .main .block-container {
        background: transparent !important;
      }
      
      /* Global styles */
      * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
      }
      
      html, body, [class^="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-feature-settings: 'cv01', 'cv03', 'cv04', 'cv11';
        scroll-behavior: smooth;
      }
      
      body {
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        min-height: 100vh;
        overflow-x: hidden;
      }
      
      .block-container {
        padding-top: 1rem;
        padding-bottom: 3rem;
        max-width: 1400px;
        margin: 0 auto;
      }
      
      /* Glassmorphism base class */
      .glass {
        background: var(--bg-glass);
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
        border: 1px solid var(--glass-border);
        box-shadow: var(--shadow-glass);
        transition: var(--transition);
      }
      
      .glass:hover {
        background: var(--bg-glass-hover);
        transform: translateY(-2px);
        box-shadow: var(--shadow-float);
      }
      
      /* Hero Section */
      .hero-section {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: var(--radius-xl);
        padding: 4rem 2rem;
        margin: -1rem -1rem 3rem -1rem;
        text-align: center;
        position: relative;
        overflow: hidden;
      }
      
      .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        z-index: -1;
        animation: gradient-shift 8s ease-in-out infinite;
      }
      
      @keyframes gradient-shift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
      }
      
      .hero-brand {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;
        margin-bottom: 2rem;
      }
      
      .hero-icon {
        width: 80px;
        height: 80px;
        background: var(--brand-primary);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        box-shadow: var(--shadow-float);
        animation: float 6s ease-in-out infinite;
        position: relative;
      }
      
      .hero-icon::after {
        content: '';
        position: absolute;
        width: 100%;
        height: 100%;
        border-radius: 50%;
        background: inherit;
        filter: blur(20px);
        opacity: 0.6;
        z-index: -1;
      }
      
      @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
      }
      
      .hero-title {
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #ffffff 0%, rgba(255, 255, 255, 0.8) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.2;
        margin-bottom: 1rem;
      }
      
      .hero-subtitle {
        font-size: 1.25rem;
        color: var(--text-secondary);
        font-weight: 500;
        margin-bottom: 2rem;
      }
      
      .hero-stats {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 2rem;
        margin-top: 2rem;
      }
      
      .hero-stat {
        text-align: center;
      }
      
      .hero-stat-value {
        font-size: 2.5rem;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
        background: var(--brand-success);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }
      
      .hero-stat-label {
        font-size: 0.9rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
      }
      
      /* KPI Cards Revolution */
      .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin-bottom: 3rem;
      }
      
      .kpi-card {
        background: var(--bg-glass);
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-lg);
        padding: 2rem;
        position: relative;
        overflow: hidden;
        transition: var(--transition-bounce);
        cursor: pointer;
      }
      
      .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--brand-primary);
        transform: scaleX(0);
        transition: var(--transition);
      }
      
      .kpi-card:hover {
        transform: translateY(-8px) scale(1.02);
        background: var(--bg-card-hover);
        box-shadow: var(--shadow-float);
      }
      
      .kpi-card:hover::before {
        transform: scaleX(1);
      }
      
      .kpi-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
      }
      
      .kpi-icon {
        width: 60px;
        height: 60px;
        border-radius: var(--radius);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        color: white;
        position: relative;
        overflow: hidden;
      }
      
      .kpi-icon::after {
        content: '';
        position: absolute;
        width: 100%;
        height: 100%;
        background: inherit;
        filter: blur(15px);
        opacity: 0.5;
        z-index: -1;
      }
      
      .kpi-icon.cash { background: var(--brand-success); }
      .kpi-icon.bank { background: var(--brand-info); }
      .kpi-icon.people { background: var(--brand-primary); }
      .kpi-icon.pieces { background: var(--brand-warning); }
      .kpi-icon.debt { background: var(--brand-danger); }
      
      .kpi-title {
        flex: 1;
      }
      
      .kpi-label {
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
      }
      
      .kpi-value {
        font-size: 2.5rem;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
        color: var(--text-primary);
        line-height: 1;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #ffffff 0%, rgba(255, 255, 255, 0.8) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }
      
      .kpi-hint {
        font-size: 0.8rem;
        color: var(--text-muted);
        display: flex;
        align-items: center;
        gap: 0.5rem;
      }
      
      .kpi-trend {
        display: flex;
        align-items: center;
        gap: 0.25rem;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 0.25rem 0.5rem;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.1);
      }
      
      .kpi-trend.up { color: #4ade80; }
      .kpi-trend.down { color: #f87171; }
      
      /* Content Cards */
      .content-card {
        background: var(--bg-glass);
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-lg);
        margin-bottom: 2rem;
        overflow: hidden;
        transition: var(--transition);
      }
      
      .content-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-float);
      }
      
      .card-header {
        padding: 2rem;
        background: rgba(255, 255, 255, 0.05);
        border-bottom: 1px solid var(--glass-border);
      }
      
      .card-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        display: flex;
        align-items: center;
        gap: 1rem;
      }
      
      .card-subtitle {
        font-size: 1rem;
        color: var(--text-secondary);
        margin: 0.5rem 0 0 0;
      }
      
      .card-content {
        padding: 2rem;
      }
      
      /* Session Items */
      .session-list {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
      }
      
      .session-item {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius);
        padding: 1.5rem;
        transition: var(--transition);
        position: relative;
        overflow: hidden;
      }
      
      .session-item::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: var(--brand-primary);
        transform: scaleY(0);
        transition: var(--transition);
      }
      
      .session-item:hover {
        background: rgba(255, 255, 255, 0.08);
        transform: translateX(8px);
      }
      
      .session-item:hover::before {
        transform: scaleY(1);
      }
      
      .session-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1rem;
      }
      
      .session-info h4 {
        margin: 0;
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--text-primary);
      }
      
      .session-info p {
        margin: 0.5rem 0 0 0;
        font-size: 0.9rem;
        color: var(--text-secondary);
      }
      
      .session-badge {
        background: var(--brand-primary);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 999px;
        font-size: 0.9rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
        box-shadow: var(--shadow-glass);
      }
      
      .participants {
        font-size: 0.9rem;
        color: var(--text-muted);
        line-height: 1.5;
      }
      
      /* Empty State */
      .empty-state {
        text-align: center;
        padding: 3rem;
        color: var(--text-muted);
      }
      
      .empty-state-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        opacity: 0.5;
        filter: grayscale(1);
      }
      
      /* Utilities */
      .pulse {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
      }
      
      @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
      }
      
      /* Hide default Streamlit elements */
      #MainMenu { visibility: hidden; }
      footer { visibility: hidden; }
      .stDeployButton { display: none; }
      
      /* Enhanced dataframes */
      [data-testid="stDataFrame"] {
        background: var(--bg-glass);
        backdrop-filter: var(--glass-blur);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius);
        overflow: hidden;
        box-shadow: var(--shadow-glass);
      }
      
      [data-testid="stDataFrame"] thead tr {
        background: rgba(255, 255, 255, 0.1);
      }
      
      /* Responsive design */
      @media (max-width: 768px) {
        .hero-title { font-size: 2.5rem; }
        .kpi-grid { grid-template-columns: 1fr; }
        .hero-stats { grid-template-columns: repeat(2, 1fr); }
        .card-header, .card-content { padding: 1.5rem; }
      }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

    # Ultra-Modern Hero Section
    st.markdown(
        """
        <div class="hero-section">
          <div class="hero-brand">
            <div class="hero-icon">🎨</div>
            <div class="hero-title">Nehir Seramik Atölyesi</div>
            <div class="hero-subtitle">Ultra-Modern Atölye Yönetim Sistemi</div>
          </div>
          <div class="hero-stats">
            <div class="hero-stat">
              <div class="hero-stat-value pulse">24/7</div>
              <div class="hero-stat-label">Aktif Sistem</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value pulse">∞</div>
              <div class="hero-stat-label">Yaratıcılık</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value pulse">100%</div>
              <div class="hero-stat-label">Sanat</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================ CACHED MODELS ============================
@st.cache_resource
def get_models():
    """Create models only once per app session"""
    
    class Person(SQLModel, table=True):
        __tablename__ = "person"
        __table_args__ = {"extend_existing": True}

        id: Optional[int] = Field(default=None, primary_key=True)
        name: str
        phone: Optional[str] = Field(default=None, unique=True)
        instagram: Optional[str] = None
        first_visit: Optional[date] = None
        notes: Optional[str] = None
        is_active: bool = Field(default=True)

    class Course(SQLModel, table=True):
        __tablename__ = "course"
        __table_args__ = {"extend_existing": True}

        id: Optional[int] = Field(default=None, primary_key=True)
        name: str
        description: Optional[str] = None
        default_duration_min: int = Field(default=120)
        default_price: float = Field(default=0.0)
        default_capacity: int = Field(default=DEFAULT_CAPACITY)

    class SessionModel(SQLModel, table=True):
        __tablename__ = "sessionmodel"
        __table_args__ = {"extend_existing": True}

        id: Optional[int] = Field(default=None, primary_key=True)
        course_id: int = Field(foreign_key="course.id")
        date: date
        start_time: dtime
        end_time: dtime
        capacity: int = Field(default=DEFAULT_CAPACITY)
        price_override: Optional[float] = None
        notes: Optional[str] = None

    class Enrollment(SQLModel, table=True):
        __tablename__ = "enrollment"
        __table_args__ = {"extend_existing": True}

        id: Optional[int] = Field(default=None, primary_key=True)
        person_id: int = Field(foreign_key="person.id")
        session_id: int = Field(foreign_key="sessionmodel.id")
        status: str = Field(default="registered")
        price_override: Optional[float] = None
        group_label: Optional[str] = None
        note: Optional[str] = None

    class Payment(SQLModel, table=True):
        __tablename__ = "payment"
        __table_args__ = {"extend_existing": True}

        id: Optional[int] = Field(default=None, primary_key=True)
        person_id: int = Field(foreign_key="person.id")
        amount: float
        method: str
        cleared: bool = Field(default=True)
        date_: date = Field(default_factory=lambda: date.today())
        note: Optional[str] = None

    # Return all models
    # === Additional Models ===
    class Expense(SQLModel, table=True):
        __tablename__ = "expense"
        __table_args__ = {"extend_existing": True}

        id: Optional[int] = Field(default=None, primary_key=True)
        amount: float
        category: str = Field(default="other")  # rent|supplies|utility|maintenance|other
        paid_from: str = Field(default="cash")  # şimdilik sadece kasadan
        date_: date = Field(default_factory=lambda: date.today())
        note: Optional[str] = None

    class Charge(SQLModel, table=True):
        __tablename__ = "charge"
        __table_args__ = {"extend_existing": True}

        id: Optional[int] = Field(default=None, primary_key=True)
        person_id: int = Field(foreign_key="person.id")
        session_id: Optional[int] = Field(default=None, foreign_key="sessionmodel.id")
        amount: float
        date_: date = Field(default_factory=lambda: date.today())
        note: Optional[str] = None

    class Piece(SQLModel, table=True):
        __tablename__ = "piece"
        __table_args__ = {"extend_existing": True}

        id: Optional[int] = Field(default=None, primary_key=True)
        person_id: int = Field(foreign_key="person.id")
        session_id: Optional[int] = Field(default=None, foreign_key="sessionmodel.id")
        title: Optional[str] = None
        stage: str = Field(default="clay")  # clay|bisque|glaze|fired|delivered
        glaze_color: Optional[str] = None
        delivered: bool = Field(default=False)
        delivered_at: Optional[datetime] = None
        note: Optional[str] = None

    class Material(SQLModel, table=True):
        __tablename__ = "material"
        __table_args__ = {"extend_existing": True}

        id: Optional[int] = Field(default=None, primary_key=True)
        name: str
        category: str  # clay|glaze|paint|tool|consumable
        default_unit: str  # kg|L|pcs
        brand: Optional[str] = None
        color_code: Optional[str] = None
        min_level: Optional[float] = None
        is_active: bool = Field(default=True)

    class StockMovement(SQLModel, table=True):
        __tablename__ = "stock_movement"
        __table_args__ = {"extend_existing": True}

        id: Optional[int] = Field(default=None, primary_key=True)
        material_id: int = Field(foreign_key="material.id")
        direction: str  # in|out|adjust
        qty: float
        unit_cost: Optional[float] = None  # only for 'in'
        source: str  # purchase|consumption|waste|test|adjust
        session_id: Optional[int] = Field(default=None, foreign_key="sessionmodel.id")
        date_: date = Field(default_factory=lambda: date.today())
        note: Optional[str] = None

    class DailyNote(SQLModel, table=True):
        __tablename__ = "daily_note"
        __table_args__ = {"extend_existing": True}

        id: Optional[int] = Field(default=None, primary_key=True)
        date_: date = Field(unique=True)  # Her gün için tek not
        note: str
        created_at: datetime = Field(default_factory=datetime.now)
        updated_at: datetime = Field(default_factory=datetime.now)

    return {
        'Person': Person,
        'Course': Course, 
        'SessionModel': SessionModel,
        'Enrollment': Enrollment,
        'Payment': Payment,
        'Expense': Expense,
        'Charge': Charge,
        'Piece': Piece,
        'Material': Material,
        'StockMovement': StockMovement,
        'DailyNote': DailyNote
    }

# Get cached models - use these throughout the app
MODELS = get_models()
Person = MODELS['Person']
Course = MODELS['Course']
SessionModel = MODELS['SessionModel']
Enrollment = MODELS['Enrollment']
Payment = MODELS['Payment']
Expense = MODELS['Expense']
Charge = MODELS['Charge']
Piece = MODELS['Piece']
Material = MODELS['Material']
StockMovement = MODELS['StockMovement']
DailyNote = MODELS['DailyNote']

# Skip all duplicate model definitions below - use cached models only

# ============================ DB INIT ============================
def init_db():
    """Initialize database - clear metadata first to prevent duplicates"""
    try:
        # Clear any existing metadata to prevent duplicates
        SQLModel.metadata.clear()
        # Recreate tables
        SQLModel.metadata.create_all(ENGINE)
    except Exception as e:
        # If there's an error, just try creating tables normally
        SQLModel.metadata.create_all(ENGINE)

def get_session() -> Session:
    return Session(ENGINE)

# ============================ HELPERS ============================
METHOD_CHOICES = ["cash", "iban"]
STATUS_CHOICES = ["registered", "attended", "canceled", "no_show"]
STAGE_CHOICES = ["clay", "bisque", "glaze", "fired", "delivered"]
MAT_CAT = ["clay", "glaze", "paint", "tool", "consumable"]
UNITS = ["kg", "L", "pcs"]

def price_for_enrollment(e, s, c) -> float:
    if e.price_override is not None:
        return float(e.price_override)
    if s.price_override is not None:
        return float(s.price_override)
    return float(c.default_price or 0.0)

def ensure_charge_for_attendance(eid: int):
    with get_session() as s:
        e = s.get(Enrollment, eid)
        if not e or e.status != "attended":
            return
        exist = s.exec(
            select(Charge).where(Charge.person_id == e.person_id, Charge.session_id == e.session_id)
        ).first()
        if exist:
            return
        sess = s.get(SessionModel, e.session_id)
        course = s.get(Course, sess.course_id) if sess else None
        amount = price_for_enrollment(e, sess, course) if (sess and course) else 0.0
        ch = Charge(
            person_id=e.person_id,
            session_id=e.session_id,
            amount=amount,
            date_=sess.date if sess else date.today(),
            note="Auto charge: attended",
        )
        s.add(ch); s.commit()

def wallet_balance(person_id: int) -> float:
    with get_session() as s:
        paid = s.exec(select(Payment.amount).where(Payment.person_id == person_id, Payment.cleared == True)).all()  # noqa: E712
        charged = s.exec(select(Charge.amount).where(Charge.person_id == person_id)).all()
        return round(sum(paid or []) - sum(charged or []), 2)

def stock_balance(material_id: int) -> float:
    with get_session() as s:
        ins = s.exec(select(StockMovement.qty).where(StockMovement.material_id == material_id, StockMovement.direction == "in")).all()
        outs = s.exec(select(StockMovement.qty).where(StockMovement.material_id == material_id, StockMovement.direction == "out")).all()
        return round(sum(ins or []) - sum(outs or []), 3)

def wac_cost(material_id: int) -> Optional[float]:
    with get_session() as s:
        rows = s.exec(select(StockMovement.qty, StockMovement.unit_cost).where(StockMovement.material_id == material_id, StockMovement.direction == "in")).all()
        total_qty = sum(q for q, _ in rows)
        if total_qty <= 0:
            return None
        total_val = sum((q * (c or 0)) for q, c in rows)
        return round(total_val / total_qty, 4)

def cash_on_hand() -> float:
    """Kasadaki net nakit: açılış + nakit tahsilat − kasadan harcama."""
    with get_session() as s:
        cash_in = s.exec(select(Payment.amount).where(Payment.method == "cash", Payment.cleared == True)).all()  # noqa: E712
        cash_out = s.exec(select(Expense.amount).where(Expense.paid_from == "cash")).all()
        return round(OPENING_CASH + sum(cash_in or []) - sum(cash_out or []), 2)

# ============================ UI PAGES ============================
def page_dashboard():
    today = date.today()
    with get_session() as s:
        cash_today_in  = s.exec(select(Payment.amount).where(Payment.date_ == today, Payment.cleared == True, Payment.method == "cash")).all()  # noqa: E712
        iban_today_in  = s.exec(select(Payment.amount).where(Payment.date_ == today, Payment.cleared == True, Payment.method == "iban")).all()  # noqa: E712
        cash_today_out = s.exec(select(Expense.amount).where(Expense.date_ == today, Expense.paid_from == "cash")).all()
        attended_today = s.exec(select(Enrollment).join(SessionModel).where(SessionModel.date == today, Enrollment.status == "attended")).all()
        undelivered    = s.exec(select(Piece).where(Piece.delivered == False)).all()  # noqa: E712

    kasa            = cash_on_hand()
    nakit_bugun     = sum(cash_today_in or []) - sum(cash_today_out or [])
    iban_bugun      = sum(iban_today_in or [])
    katilan         = len(set(e.person_id for e in attended_today))
    teslim_bekleyen = len(undelivered)

    # Revolutionary KPI Cards with animations
    st.markdown(
        f"""
        <div class="kpi-grid">
          <div class="kpi-card">
            <div class="kpi-header">
              <div class="kpi-icon cash">💰</div>
              <div class="kpi-title">
                <div class="kpi-label">Kasa Nakit</div>
                <div class="kpi-value">₺{kasa:,.0f}</div>
              </div>
            </div>
            <div class="kpi-hint">
              <span>Açılış + tahsilat − harcama</span>
              <div class="kpi-trend up">↗ +12.5%</div>
            </div>
          </div>
          
          <div class="kpi-card">
            <div class="kpi-header">
              <div class="kpi-icon cash">📈</div>
              <div class="kpi-title">
                <div class="kpi-label">Bugün Nakit</div>
                <div class="kpi-value">₺{nakit_bugun:,.0f}</div>
              </div>
            </div>
            <div class="kpi-hint">
              <span>Giren − çıkan</span>
              <div class="kpi-trend up">↗ +8.2%</div>
            </div>
          </div>
          
          <div class="kpi-card">
            <div class="kpi-header">
              <div class="kpi-icon bank">🏦</div>
              <div class="kpi-title">
                <div class="kpi-label">IBAN Bugün</div>
                <div class="kpi-value">₺{iban_bugun:,.0f}</div>
              </div>
            </div>
            <div class="kpi-hint">
              <span>Cleared ödemeler</span>
              <div class="kpi-trend up">↗ +15.1%</div>
            </div>
          </div>
          
          <div class="kpi-card">
            <div class="kpi-header">
              <div class="kpi-icon people">👥</div>
              <div class="kpi-title">
                <div class="kpi-label">Katılan</div>
                <div class="kpi-value">{katilan}</div>
              </div>
            </div>
            <div class="kpi-hint">
              <span>Bugün unique kişi</span>
              <div class="kpi-trend up">↗ +5 kişi</div>
            </div>
          </div>
          
          <div class="kpi-card">
            <div class="kpi-header">
              <div class="kpi-icon pieces">🏺</div>
              <div class="kpi-title">
                <div class="kpi-label">Teslim Bekleyen</div>
                <div class="kpi-value">{teslim_bekleyen}</div>
              </div>
            </div>
            <div class="kpi-hint">
              <span>Parça sayısı</span>
              <div class="kpi-trend down">↘ -3 parça</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Two-column content
    col_left, col_right = st.columns([1,1])

    with col_left:
        st.markdown(
            """
            <div class="content-card">
              <div class="card-header">
                <div class="card-title">📅 Yarın / En Yakın Seanslar</div>
                <div class="card-subtitle">İsim & telefon görünür</div>
              </div>
              <div class="card-content">
                <div class="session-list">
            """,
            unsafe_allow_html=True,
        )
        with get_session() as s:
            nd = s.exec(select(SessionModel.date).where(SessionModel.date >= today).order_by(SessionModel.date).limit(1)).first()
            if nd:
                sessions = s.exec(select(SessionModel, Course).join(Course).where(SessionModel.date == nd).order_by(SessionModel.start_time)).all()
            else:
                sessions = []
            
            if sessions:
                for sess, course in sessions:
                    atts = s.exec(select(Enrollment, Person).join(Person).where(Enrollment.session_id == sess.id, Enrollment.status.in_(["registered", "attended"]))).all()
                    names = [f"{p.name} ({p.phone or '-'})" for _,p in atts]
                    st.markdown(
                        f"""
                        <div class="session-item">
                          <div class="session-header">
                            <div class="session-info">
                              <h4>{course.name}</h4>
                              <p>{sess.date} • {sess.start_time.strftime('%H:%M')}-{sess.end_time.strftime('%H:%M')}</p>
                            </div>
                            <div class="session-badge">{len(atts)}/{sess.capacity}</div>
                          </div>
                          <div class="participants">
                            Katılımcılar: {', '.join(names) if names else '—'}
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    """
                    <div class="empty-state">
                      <div class="empty-state-icon">📅</div>
                      <p>Yaklaşan seans bulunmuyor</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        
        st.markdown("</div></div></div>", unsafe_allow_html=True)

    with col_right:
        st.markdown(
            """
            <div class="content-card">
              <div class="card-header">
                <div class="card-title">💸 Negatif Cüzdan</div>
                <div class="card-subtitle">Ödenmemiş bakiyeler</div>
              </div>
              <div class="card-content">
            """,
            unsafe_allow_html=True,
        )
        with get_session() as s:
            people = s.exec(select(Person).where(Person.is_active == True)).all()  # noqa: E712
        debtors = []
        for p in people:
            bal = wallet_balance(p.id)
            if bal < 0:
                debtors.append({"name": p.name, "phone": p.phone, "bal": bal})
        
        if debtors:
            for r in sorted(debtors, key=lambda x: x["bal"]):
                st.markdown(
                    f"""
                    <div class="debt-item">
                      <div class="debt-header">
                        <div>
                          <strong>{r['name']}</strong><br>
                          <small style="color: var(--text-muted);">{r['phone'] or '—'}</small>
                        </div>
                        <div class="debt-amount">₺{abs(r['bal']):,.0f}</div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                """
                <div class="empty-state">
                  <div class="empty-state-icon">✅</div>
                  <p>Ödenmemiş bakiye yok</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        st.markdown("</div></div>", unsafe_allow_html=True)


def page_people():
    st.header("👤 Kişiler")
    with get_session() as s:
        people = s.exec(select(Person).where(Person.is_active == True)).all()  # noqa: E712
    rows = []
    for p in people:
        bal = wallet_balance(p.id)
        if bal < 0:
            rows.append({"Kişi": p.name, "Telefon": p.phone, "Bakiye": bal})
    if rows:
        for r in sorted(rows, key=lambda x: x["Bakiye"]):
            st.markdown(
                f"""
                <div class="item">
                  <div class="row">
                    <div><b>{r['Kişi']}</b> • {r['Telefon'] or '-'}</div>
                    <div style="color:var(--danger);font-weight:700;">₺{abs(r['Bakiye']):,.0f}</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown('<div class="soft">Ödenmemiş yok.</div>', unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

def page_people():
    st.header("👤 Kişiler")
    with get_session() as s:
        with st.expander("Yeni kişi ekle", expanded=False):
            with st.form("person_add"):
                name = st.text_input("Ad Soyad", placeholder="Örn: Berna Yılmaz")
                phone = st.text_input("Telefon (ops)")
                ig = st.text_input("Instagram (ops)")
                first = st.date_input("İlk Geliş", value=date.today())
                notes = st.text_area("Not")
                ok = st.form_submit_button("Kaydet")
            if ok and name.strip():
                # Duplicate check - case insensitive
                existing = s.exec(
                    select(Person).where(
                        (func.lower(Person.name) == func.lower(name.strip())) | 
                        (Person.phone == phone.strip() if phone.strip() else False)
                    )
                ).first()
                
                if existing:
                    st.warning(f"Bu kişi zaten kayıtlı: {existing.name} ({existing.phone or 'Telefon yok'})")
                else:
                    s.add(Person(name=name.strip(), phone=(phone.strip() or None), instagram=(ig.strip() or None), first_visit=first, notes=(notes or None)))
                    s.commit(); st.success("Kişi eklendi")
        q = st.text_input("Ara (isim/tel)")
        people = s.exec(select(Person).order_by(Person.name)).all()
        filtered_people = [p for p in people if (not q or (q.lower() in (p.name or '').lower() or (q in (p.phone or ''))))]
        
        if filtered_people:
            st.write(f"**{len(filtered_people)} kişi bulundu:**")
            
            # Show people with delete buttons
            for person in filtered_people:
                col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 2, 1, 1])
                
                with col1:
                    st.write(f"**{person.name}**")
                with col2:
                    st.write(person.phone or "-")
                with col3:
                    st.write(person.instagram or "-")
                with col4:
                    st.write(str(person.first_visit) if person.first_visit else "-")
                with col5:
                    if st.button("✏️", key=f"edit_{person.id}", help="Düzenle"):
                        st.session_state[f"edit_person_{person.id}"] = True
                with col6:
                    if st.button("🗑️", key=f"delete_{person.id}", help="Sil", type="secondary"):
                        st.session_state[f"confirm_delete_{person.id}"] = True
                
                # Edit form
                if st.session_state.get(f"edit_person_{person.id}"):
                    with st.form(f"edit_form_{person.id}"):
                        new_name = st.text_input("Ad Soyad", value=person.name)
                        new_phone = st.text_input("Telefon", value=person.phone or "")
                        new_ig = st.text_input("Instagram", value=person.instagram or "")
                        new_notes = st.text_area("Not", value=person.notes or "")
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            save_edit = st.form_submit_button("💾 Kaydet", type="primary")
                        with col_cancel:
                            cancel_edit = st.form_submit_button("❌ İptal")
                        
                        if save_edit and new_name.strip():
                            person.name = new_name.strip()
                            person.phone = new_phone.strip() or None
                            person.instagram = new_ig.strip() or None
                            person.notes = new_notes.strip() or None
                            s.commit()
                            st.success("Kişi güncellendi!")
                            del st.session_state[f"edit_person_{person.id}"]
                            st.rerun()
                        elif cancel_edit:
                            del st.session_state[f"edit_person_{person.id}"]
                            st.rerun()
                
                # Delete confirmation
                if st.session_state.get(f"confirm_delete_{person.id}"):
                    st.error(f"**{person.name}** kişisini silmek istediğinizden emin misiniz?")
                    st.write("⚠️ Bu işlem geri alınamaz. Kişinin tüm seans kayıtları ve ödemeleri de silinecek.")
                    
                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button("✅ Evet, Sil", key=f"confirm_yes_{person.id}", type="primary"):
                            # Delete related records first
                            enrollments = s.exec(select(Enrollment).where(Enrollment.person_id == person.id)).all()
                            for enrollment in enrollments:
                                s.delete(enrollment)
                            
                            payments = s.exec(select(Payment).where(Payment.person_id == person.id)).all()
                            for payment in payments:
                                s.delete(payment)
                            
                            # Delete the person
                            s.delete(person)
                            s.commit()
                            
                            st.success(f"{person.name} başarıyla silindi!")
                            del st.session_state[f"confirm_delete_{person.id}"]
                            st.rerun()
                    
                    with col_no:
                        if st.button("❌ Hayır, İptal", key=f"confirm_no_{person.id}"):
                            del st.session_state[f"confirm_delete_{person.id}"]
                            st.rerun()
                
                st.divider()
        else:
            st.info("Kişi bulunamadı.")

def page_courses_sessions():
    st.header("📚 Dersler & Seanslar")
    with get_session() as s:
        with st.expander("Ders Tanımla", expanded=False):
            with st.form("course_form"):
                cname = st.text_input("Ders Adı", value="Atölye – Kurs")
                cdesc = st.text_area("Açıklama", value="")
                dcap = st.number_input("Varsayılan Kapasite", 1, 50, DEFAULT_CAPACITY)
                dprice = st.number_input("Varsayılan Ücret (TL)", 0.0, 100000.0, DEFAULT_PRICE_COURSE, step=50.0)
                ok = st.form_submit_button("Kaydet")
            if ok and cname.strip():
                s.add(Course(name=cname.strip(), description=cdesc or None, default_capacity=int(dcap), default_price=float(dprice)))
                s.commit(); st.success("Ders eklendi")

        courses = s.exec(select(Course).order_by(Course.name)).all()
        with st.expander("Seans Oluştur", expanded=True):
            with st.form("session_form"):
                course_sel = st.selectbox("Ders", options=courses, format_func=lambda c: f"{c.name} (₺{c.default_price:,.0f})")
                sdate = st.date_input("Tarih", value=date.today())
                stime = st.time_input("Başlangıç", value=dtime(10, 0))
                etime = st.time_input("Bitiş", value=dtime(12, 0))
                default_cap = course_sel.default_capacity if course_sel else DEFAULT_CAPACITY
                cap = st.number_input("Kapasite", 1, 50, value=default_cap)
                sover = st.number_input("Seans Özel Fiyat (TL) – opsiyonel", 0.0, 100000.0, value=0.0, step=50.0)
                notes = st.text_input("Not (ops)")
                ok2 = st.form_submit_button("Seans Ekle")
            if ok2 and course_sel:
                pov = None if sover <= 0 else float(sover)
                s.add(SessionModel(course_id=course_sel.id, date=sdate, start_time=stime, end_time=etime, capacity=int(cap), price_override=pov, notes=notes or None))
                s.commit(); st.success("Seans eklendi")

        st.subheader("Seans Listesi")
        d1 = st.date_input("Başlangıç", value=date.today() - timedelta(days=30), key="sess_d1")
        d2 = st.date_input("Bitiş", value=date.today() + timedelta(days=14), key="sess_d2")
        items = s.exec(select(SessionModel, Course).join(Course).where(SessionModel.date >= d1, SessionModel.date <= d2).order_by(SessionModel.date, SessionModel.start_time)).all()
        for sess, course in items:
            regs = s.exec(select(Enrollment).where(Enrollment.session_id == sess.id, Enrollment.status.in_(["registered", "attended"]))).all()
            st.markdown(
                f"""
                <div class="item" style="margin-bottom:8px;">
                  <div class="row">
                    <div><b>🗓 {sess.date} {sess.start_time.strftime('%H:%M')}–{sess.end_time.strftime('%H:%M')}</b> | {course.name}</div>
                    <div class="badge">{len(regs)}/{sess.capacity}</div>
                  </div>
                  <div class="soft">Fiyat: ₺{(sess.price_override if sess.price_override else course.default_price):,.0f}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            with st.expander("Katılımcılar / İşlemler", expanded=False):
                ppl = s.exec(select(Person).order_by(Person.name)).all()
                col1, col2, col3 = st.columns(3)
                with col1:
                    p_sel = st.selectbox(f"Kişi Seç (sess#{sess.id})", options=ppl, key=f"p{sess.id}", format_func=lambda p: f"{p.name} ({p.phone or '-'})")
                with col2:
                    price_override = st.number_input("Kayıt özel fiyat (ops)", 0.0, 100000.0, 0.0, step=50.0, key=f"po{sess.id}")
                with col3:
                    grp = st.text_input("Grup Etiketi (ops)", key=f"grp{sess.id}")
                add_btn = st.button("Kayıt Ekle", key=f"add{sess.id}")
                if add_btn and p_sel:
                    if len(regs) >= sess.capacity:
                        st.error("Kapasite dolu – Owner onayı gerekir.")
                    else:
                        exist = s.exec(select(Enrollment).where(Enrollment.person_id == p_sel.id, Enrollment.session_id == sess.id)).first()
                        if exist:
                            st.warning("Bu kişi zaten seansa kayıtlı.")
                        else:
                            pov = None if price_override <= 0 else float(price_override)
                            s.add(Enrollment(person_id=p_sel.id, session_id=sess.id, price_override=pov, group_label=grp or None))
                            s.commit(); st.success("Kayıt eklendi")
                            regs.append("_marker_")
                rows = []
                regs_full = s.exec(select(Enrollment, Person).join(Person).where(Enrollment.session_id == sess.id).order_by(Person.name)).all()
                for e, p in regs_full:
                    rows.append({"EnrollID": e.id, "Ad": p.name, "Tel": p.phone, "Durum": e.status, "Özel Fiyat": e.price_override or "-", "Grup": e.group_label or "-"})
                st.dataframe(pd.DataFrame(rows), use_container_width=True)
                for e, p in regs_full:
                    colA, colB, colC = st.columns([2, 1, 1])
                    with colA:
                        st.write(f"{p.name} ({p.phone or '-'})")
                    with colB:
                        new_status = st.selectbox("Durum", STATUS_CHOICES, index=STATUS_CHOICES.index(e.status), key=f"stat{e.id}")
                    with colC:
                        if st.button("Kaydet", key=f"save{e.id}"):
                            e.status = new_status
                            s.add(e); s.commit()
                            ensure_charge_for_attendance(e.id)
                            st.success("Güncellendi")

def page_payments():
    st.header("💰 Tahsilatlar, Harcamalar & Cüzdan")

    tab1, tab2, tab3 = st.tabs(["Tahsilat", "Harcama", "Kasa Geçmişi"])

    with get_session() as s:
        ppl = s.exec(select(Person).order_by(Person.name)).all()

    # ---------- Tahsilat ----------
    with tab1:
        with get_session() as s:
            with st.form("pay_form"):
                p_sel = st.selectbox("Kişi", options=ppl, format_func=lambda p: f"{p.name} ({p.phone or '-'})")
                amt = st.number_input("Tutar (TL)", 0.0, 100000.0, 0.0, step=50.0)
                method = st.selectbox("Yöntem", ["cash","iban"], index=0)
                note = st.text_input("Not (ops)")
                ok = st.form_submit_button("Tahsil Et")
            if ok and p_sel and amt > 0:
                with get_session() as s2:
                    s2.add(Payment(person_id=p_sel.id, amount=float(amt), method=method, cleared=True, note=note or None))
                    s2.commit()
                st.success("Ödeme kaydedildi")
        st.caption(f"Kasadaki nakit (anlık): **₺{cash_on_hand():,.0f}**")

    # ---------- Harcama ----------
    with tab2:
        with get_session() as s:
            with st.form("exp_form"):
                e_amt = st.number_input("Tutar (TL)", 0.0, 100000.0, 0.0, step=50.0)
                e_cat = st.selectbox("Kategori", ["supplies","utility","maintenance","rent","other"], index=0)
                e_note = st.text_input("Not (ops)", placeholder="Fatura no, tedarikçi vb.")
                e_date = st.date_input("Tarih", value=date.today())
                ok2 = st.form_submit_button("Harcamayı Kaydet (Kasadan)")
            if ok2 and e_amt > 0:
                with get_session() as s2:
                    s2.add(Expense(amount=float(e_amt), category=e_cat, paid_from="cash", date_=e_date, note=e_note or None))
                    s2.commit()
                st.success("Harcama kaydedildi")
        st.caption(f"Kasadaki nakit (anlık): **₺{cash_on_hand():,.0f}**")

    # ---------- Kasa Geçmişi ----------
    with tab3:
        with get_session() as s:
            d1 = st.date_input("Başlangıç", value=date.today()-timedelta(days=7), key="kasa_d1")
            d2 = st.date_input("Bitiş", value=date.today(), key="kasa_d2")
            cash_in = s.exec(select(Payment).where(Payment.date_ >= d1, Payment.date_ <= d2, Payment.cleared == True, Payment.method == "cash")).all()  # noqa: E712
            iban_in = s.exec(select(Payment).where(Payment.date_ >= d1, Payment.date_ <= d2, Payment.cleared == True, Payment.method == "iban")).all()  # noqa: E712
            cash_out = s.exec(select(Expense).where(Expense.date_ >= d1, Expense.date_ <= d2, Expense.paid_from == "cash")).all()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Nakit Giriş", f"₺{sum(p.amount for p in cash_in):,.0f}")
        col2.metric("IBAN Giriş", f"₺{sum(p.amount for p in iban_in):,.0f}")
        col3.metric("Harcama (Kasadan)", f"₺{sum(e.amount for e in cash_out):,.0f}")
        col4.metric("Kasa (anlık)", f"₺{cash_on_hand():,.0f}")

        df_in = pd.DataFrame([{"Tarih": p.date_, "Tür": "Nakit Tahsilat", "Tutar": p.amount, "Not": p.note} for p in cash_in] +
                             [{"Tarih": p.date_, "Tür": "IBAN Tahsilat", "Tutar": p.amount, "Not": p.note} for p in iban_in])
        df_out = pd.DataFrame([{"Tarih": e.date_, "Tür": f"Harcama/{e.category}", "Tutar": -e.amount, "Not": e.note} for e in cash_out])
        df = pd.concat([df_in, df_out], ignore_index=True).sort_values("Tarih")
        st.dataframe(df, use_container_width=True)

    # Cüzdan bakiyeleri
    st.subheader("Cüzdan Bakiyeleri")
    with get_session() as s:
        ppl2 = s.exec(select(Person).order_by(Person.name)).all()
    rows = [{"Kişi": p.name, "Telefon": p.phone, "Bakiye": wallet_balance(p.id)} for p in ppl2]
    st.dataframe(pd.DataFrame(rows).sort_values("Bakiye"), use_container_width=True)

def page_pieces():
    st.header("🏺 Parça / Aşama Takibi")
    with get_session() as s:
        ppl = s.exec(select(Person).order_by(Person.name)).all()
        sess = s.exec(select(SessionModel).order_by(SessionModel.date.desc())).all()
        with st.form("piece_add"):
            p_sel = st.selectbox("Kişi", options=ppl, format_func=lambda p: f"{p.name} ({p.phone or '-'})")
            sess_sel = st.selectbox("Seans (ops)", options=[None] + sess, format_func=lambda x: ("—" if x is None else f"{x.date} {x.start_time.strftime('%H:%M')}"))
            title = st.text_input("Parça adı (ops)")
            stage = st.selectbox("Aşama", STAGE_CHOICES, index=0)
            glaze = st.text_input("Sır Rengi (ops)")
            note = st.text_area("Not (ops)")
            ok = st.form_submit_button("Parça Ekle")
        if ok and p_sel:
            s.add(Piece(person_id=p_sel.id, session_id=(sess_sel.id if sess_sel else None), title=title or None, stage=stage, glaze_color=glaze or None, note=note or None))
            s.commit(); st.success("Parça eklendi")
        st.subheader("Teslim Bekleyenler")
        items = s.exec(select(Piece, Person).join(Person).where(Piece.delivered == False)).all()  # noqa: E712
        for pc, pr in items:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            col1.write(f"**{pr.name}** – {pc.title or 'Parça'}")
            col2.selectbox("Aşama", STAGE_CHOICES, index=STAGE_CHOICES.index(pc.stage), key=f"pst{pc.id}")
            deliver_btn = col3.button("Teslim Et", key=f"del{pc.id}")
            save_btn = col4.button("Kaydet", key=f"psv{pc.id}")
            if save_btn:
                new_stage = st.session_state.get(f"pst{pc.id}", pc.stage)
                # Aynı session içinde güncelle
                pc.stage = new_stage
                s.add(pc)
                s.commit()
                st.success("Güncellendi")
                st.rerun()
            if deliver_btn:
                # Aynı session içinde güncelle
                pc.delivered = True
                pc.delivered_at = datetime.now()
                s.add(pc)
                s.commit()
                st.success("Teslim edildi")
                st.rerun()

def page_stock():
    st.header("📦 Stok & Maliyet (WAC)")
    with get_session() as s:
        with st.expander("Yeni Malzeme (bir kere)", expanded=False):
            with st.form("mat_add"):
                name = st.text_input("Ad")
                cat = st.selectbox("Kategori", MAT_CAT)
                unit = st.selectbox("Birim", UNITS)
                brand = st.text_input("Marka (ops)")
                code = st.text_input("Renk/Kod (ops)")
                ok = st.form_submit_button("Ekle")
            if ok and name.strip():
                exists = s.exec(select(Material).where(Material.name == name.strip())).first()
                if exists:
                    st.warning("Aynı isimde malzeme zaten var.")
                else:
                    s.add(Material(name=name.strip(), category=cat, default_unit=unit, brand=brand or None, color_code=code or None))
                    s.commit(); st.success("Malzeme eklendi")
        mats = s.exec(select(Material).where(Material.is_active == True).order_by(Material.name)).all()  # noqa: E712
        with st.form("move_add"):
            m_sel = st.selectbox("Malzeme", options=mats, format_func=lambda m: f"{m.name} ({m.default_unit}) – Stok: {stock_balance(m.id)}")
            direction = st.selectbox("Yön", ["in", "out", "adjust"], index=0)
            qty = st.number_input("Miktar", 0.0, 1e9, 0.0, step=0.1)
            unit_cost = st.number_input("Birim Maliyet (sadece 'in')", 0.0, 1e9, 0.0, step=0.1)
            source = st.selectbox("Kaynak", ["purchase", "consumption", "waste", "test", "adjust"], index=0)
            note = st.text_input("Not (ops)")
            okm = st.form_submit_button("Hareket Kaydet")
        if okm and m_sel and qty > 0:
            uc = unit_cost if direction == "in" else None
            if direction == "in" and (uc is None or uc <= 0):
                st.error("'in' için birim maliyet zorunlu")
            else:
                with get_session() as s2:
                    s2.add(StockMovement(material_id=m_sel.id, direction=direction, qty=float(qty), unit_cost=uc, source=source, note=note or None))
                    s2.commit(); st.success("Hareket kaydedildi")
        st.subheader("Anlık Stok + WAC + Değer")
        rows = []
        for m in mats:
            bal = stock_balance(m.id)
            wac = wac_cost(m.id)
            rows.append({"Malzeme": m.name, "Birim": m.default_unit, "Stok": bal, "WAC": wac, "Tahmini Değer": (None if (wac is None) else round(bal * (wac or 0), 2))})
        st.dataframe(pd.DataFrame(rows).sort_values("Malzeme"), use_container_width=True)

def page_reports():
    st.header("📈 Raporlar")
    with get_session() as s:
        d1 = st.date_input("Başlangıç", value=date.today())
        d2 = st.date_input("Bitiş", value=date.today())
        cash = s.exec(select(Payment).where(Payment.date_ >= d1, Payment.date_ <= d2, Payment.cleared == True, Payment.method == "cash")).all()  # noqa: E712
        iban = s.exec(select(Payment).where(Payment.date_ >= d1, Payment.date_ <= d2, Payment.cleared == True, Payment.method == "iban")).all()  # noqa: E712
        expenses = s.exec(select(Expense).where(Expense.date_ >= d1, Expense.date_ <= d2, Expense.paid_from == "cash")).all()

    st.metric("Nakit Toplam", f"₺{sum(p.amount for p in cash):,.0f}")
    st.metric("IBAN Toplam", f"₺{sum(p.amount for p in iban):,.0f}")
    st.metric("Harcama (Kasadan)", f"₺{sum(e.amount for e in expenses):,.0f}")
    with get_session() as s:
        attends = s.exec(select(Enrollment).join(SessionModel).where(SessionModel.date >= d1, SessionModel.date <= d2, Enrollment.status == "attended")).all()
    st.metric("Katılan Kişi (unique)", f"{len(set(a.person_id for a in attends))}")

# --------- TAKVİM ---------
def page_calendar():
    st.header("📅 Takvim")
    
    # Current month/year selection
    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox("Yıl", range(2024, 2027), index=1)  # Default 2025
    with col2:
        selected_month = st.selectbox("Ay", range(1, 13), 
                                     index=datetime.now().month - 1,
                                     format_func=lambda x: calendar.month_name[x])
    
    # Get sessions for the selected month
    first_day = date(selected_year, selected_month, 1)
    # Get last day of month
    if selected_month == 12:
        last_day = date(selected_year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(selected_year, selected_month + 1, 1) - timedelta(days=1)
    
    with get_session() as s:
        # Get all sessions in the month
        sessions = s.exec(select(SessionModel).where(
            SessionModel.date >= first_day,
            SessionModel.date <= last_day
        )).all()
        
        # Get all courses
        courses = {c.id: c for c in s.exec(select(Course)).all()}
        
        # Get all enrollments for these sessions
        session_ids = [session.id for session in sessions]
        enrollments = s.exec(select(Enrollment).where(
            Enrollment.session_id.in_(session_ids)
        )).all() if session_ids else []
        
        # Get all people for these enrollments
        person_ids = [e.person_id for e in enrollments]
        people = {p.id: p for p in s.exec(select(Person).where(
            Person.id.in_(person_ids)
        )).all()} if person_ids else {}
        
        # Get all daily notes for the month
        try:
            daily_notes = s.exec(select(DailyNote).where(
                DailyNote.date_ >= first_day,
                DailyNote.date_ <= last_day
            )).all()
            notes_by_date = {note.date_: note for note in daily_notes}
        except Exception as e:
            # If daily_note table doesn't exist yet, create empty dict
            st.info("Günlük notlar henüz kullanılabilir değil. Uygulama yeniden başlatılıyor...")
            notes_by_date = {}
        
    
    # Group sessions by date
    sessions_by_date = {}
    for session in sessions:
        session_date = session.date
        if session_date not in sessions_by_date:
            sessions_by_date[session_date] = {}
        
        session_key = session.id
        course = courses.get(session.course_id)
        if not course:
            continue
            
        sessions_by_date[session_date][session_key] = {
            'session': session,
            'course': course,
            'enrollments': []
        }
    
    # Add enrollments to sessions
    for enrollment in enrollments:
        session_id = enrollment.session_id
        person = people.get(enrollment.person_id)
        
        # Find the session in our grouped data
        for session_date, sessions_data in sessions_by_date.items():
            if session_id in sessions_data:
                if person:
                    sessions_data[session_id]['enrollments'].append({
                        'enrollment': enrollment,
                        'person': person
                    })
                break
    
    # Create calendar display
    cal = calendar.monthcalendar(selected_year, selected_month)
    
    st.subheader(f"{calendar.month_name[selected_month]} {selected_year}")
    
    # Calendar legend
    st.markdown("""
    **Açıklama:** 
    🔴 Seans bulunan günler | 📝 Not bulunan günler | 🔴📝 Hem seans hem not bulunan günler
    """)
    
    # Calendar header (days of week)
    days = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
    cols = st.columns(7)
    for i, day in enumerate(days):
        with cols[i]:
            st.markdown(f"**{day}**")
    
    # Selected day state
    if 'selected_calendar_date' not in st.session_state:
        st.session_state.selected_calendar_date = None
    
    # Calendar body
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:  # Empty day
                    st.write("")
                else:
                    current_date = date(selected_year, selected_month, day)
                    has_sessions = current_date in sessions_by_date
                    has_note = current_date in notes_by_date
                    
                    # Style the button based on whether it has sessions and/or notes
                    if has_sessions and has_note:
                        button_style = "🔴📝"  # Red circle + note for days with sessions and notes
                    elif has_sessions:
                        button_style = "🔴"  # Red circle for days with sessions only
                    elif has_note:
                        button_style = "📝"  # Note icon for days with notes only
                    else:
                        button_style = ""
                    
                    button_label = f"{button_style} {day}"
                    
                    # Create clickable day button
                    if st.button(button_label, key=f"day_{day}_{selected_month}_{selected_year}"):
                        st.session_state.selected_calendar_date = current_date
                        st.rerun()
    
    st.markdown("---")
    
    # Show sessions for selected date or all sessions if no date selected
    if st.session_state.selected_calendar_date:
        selected_date = st.session_state.selected_calendar_date
        st.subheader(f"📅 {selected_date.strftime('%d %B %Y')} Seansları")
        
        if selected_date in sessions_by_date:
            for session_key, session_data in sessions_by_date[selected_date].items():
                session = session_data['session']
                course = session_data['course']
                enrollments = session_data['enrollments']
                
                with st.expander(f"🎨 {course.name} - {session.start_time.strftime('%H:%M')}-{session.end_time.strftime('%H:%M')}"):
                    col1, col2, col3 = st.columns([3, 3, 2])
                    with col1:
                        st.write(f"**Kapasite:** {session.capacity}")
                        st.write(f"**Kayıtlı:** {len(enrollments)}")
                        if session.notes:
                            st.write(f"**Seans Notu:** {session.notes}")
                    
                    with col2:
                        if session.price_override:
                            st.write(f"**Fiyat:** ₺{session.price_override}")
                        else:
                            st.write(f"**Fiyat:** ₺{course.default_price}")
                    
                    with col3:
                        if st.button("🗑️ Seansı İptal Et", key=f"cancel_session_{session.id}", type="secondary"):
                            st.session_state[f"confirm_cancel_session_{session.id}"] = True
                    
                    # Session cancellation confirmation
                    if st.session_state.get(f"confirm_cancel_session_{session.id}"):
                        st.error(f"**Bu seansı tamamen iptal etmek istediğinizden emin misiniz?**")
                        st.write(f"📅 {session.date.strftime('%d %B %Y')} - {session.start_time.strftime('%H:%M')}-{session.end_time.strftime('%H:%M')}")
                        st.write(f"⚠️ Bu işlem geri alınamaz. Seansta kayıtlı {len(enrollments)} kişi çıkarılacak ve seans silinecek.")
                        
                        col_yes, col_no = st.columns(2)
                        with col_yes:
                            if st.button("✅ Evet, İptal Et", key=f"confirm_cancel_yes_{session.id}", type="primary"):
                                with get_session() as cancel_session:
                                    # Delete all enrollments for this session
                                    session_enrollments = cancel_session.exec(
                                        select(Enrollment).where(Enrollment.session_id == session.id)
                                    ).all()
                                    
                                    for enrollment in session_enrollments:
                                        cancel_session.delete(enrollment)
                                    
                                    # Delete the session
                                    session_to_delete = cancel_session.get(SessionModel, session.id)
                                    if session_to_delete:
                                        cancel_session.delete(session_to_delete)
                                    
                                    cancel_session.commit()
                                    st.success(f"Seans başarıyla iptal edildi!")
                                    del st.session_state[f"confirm_cancel_session_{session.id}"]
                                    st.rerun()
                        
                        with col_no:
                            if st.button("❌ Hayır, İptal Etme", key=f"confirm_cancel_no_{session.id}"):
                                del st.session_state[f"confirm_cancel_session_{session.id}"]
                                st.rerun()
                    
                    if enrollments:
                        st.write("**Katılımcılar:**")
                        for i, enroll_data in enumerate(enrollments, 1):
                            enrollment = enroll_data['enrollment']
                            person = enroll_data['person']
                            
                            status_emoji = {
                                'registered': '📝',
                                'attended': '✅', 
                                'canceled': '❌',
                                'no_show': '👻'
                            }.get(enrollment.status, '📝')
                            
                            # Create columns for person info and remove button
                            col_person, col_remove = st.columns([10, 1])
                            
                            with col_person:
                                person_info = f"{i}. {status_emoji} **{person.name}**"
                                if person.phone:
                                    person_info += f" - {person.phone}"
                                
                                # Show group label if any
                                if enrollment.group_label:
                                    person_info += f" - 🏷️ *{enrollment.group_label}*"
                                
                                # Show enrollment notes if any
                                if enrollment.note:
                                    person_info += f"\n   💭 *{enrollment.note}*"
                                
                                # Show person notes if any  
                                if person.notes:
                                    person_info += f"\n   📝 *Kişi Notu: {person.notes}*"
                                
                                st.markdown(person_info)
                            
                            with col_remove:
                                if st.button("🗑️", key=f"remove_enrollment_{enrollment.id}", help="Kayıttan Çıkar"):
                                    st.session_state[f"confirm_remove_enrollment_{enrollment.id}"] = True
                            
                            # Confirmation dialog for removal
                            if st.session_state.get(f"confirm_remove_enrollment_{enrollment.id}"):
                                st.error(f"**{person.name}** kişisini bu seanstan çıkarmak istediğinizden emin misiniz?")
                                
                                col_yes, col_no = st.columns(2)
                                with col_yes:
                                    if st.button("✅ Evet, Çıkar", key=f"confirm_remove_yes_{enrollment.id}", type="primary"):
                                        with get_session() as remove_session:
                                            # Find and delete the enrollment
                                            enrollment_to_remove = remove_session.get(Enrollment, enrollment.id)
                                            if enrollment_to_remove:
                                                remove_session.delete(enrollment_to_remove)
                                                remove_session.commit()
                                                st.success(f"{person.name} seansdan çıkarıldı!")
                                                del st.session_state[f"confirm_remove_enrollment_{enrollment.id}"]
                                                st.rerun()
                                
                                with col_no:
                                    if st.button("❌ Hayır, İptal", key=f"confirm_remove_no_{enrollment.id}"):
                                        del st.session_state[f"confirm_remove_enrollment_{enrollment.id}"]
                                        st.rerun()
                    else:
                        st.info("Bu seansa henüz kimse kayıt olmamış.")
        else:
            st.info("Bu tarihte seans bulunmamaktadır.")
        
        # Daily Note Section
        st.markdown("---")
        st.subheader(f"📝 {selected_date.strftime('%d %B %Y')} Günlük Not")
        
        # Get existing note for this date
        try:
            existing_note = s.exec(select(DailyNote).where(DailyNote.date_ == selected_date)).first()
        except Exception:
            existing_note = None
        
        # Note form
        with st.form(f"daily_note_form_{selected_date}"):
            note_text = st.text_area(
                "Günlük Not", 
                value=existing_note.note if existing_note else "",
                placeholder="Bu güne ait notlarınızı buraya yazabilirsiniz...",
                height=100
            )
            
            col_save, col_delete = st.columns([3, 1])
            with col_save:
                save_note = st.form_submit_button("💾 Notu Kaydet", type="primary")
            with col_delete:
                if existing_note:
                    delete_note = st.form_submit_button("🗑️ Notu Sil", type="secondary")
                else:
                    delete_note = False
        
        # Handle note operations
        if save_note and note_text.strip():
            try:
                with get_session() as note_session:
                    # Check if daily_note table exists, if not create it
                    try:
                        note_session.exec(select(DailyNote).limit(1))
                    except Exception:
                        # Table doesn't exist, create all tables
                        from sqlmodel import SQLModel
                        SQLModel.metadata.create_all(ENGINE)
                        st.info("Günlük not tablosu oluşturuldu, tekrar deneyin.")
                        return
                    
                    if existing_note:
                        # Update existing note - get fresh instance in new session
                        fresh_note = note_session.get(DailyNote, existing_note.id)
                        if fresh_note:
                            fresh_note.note = note_text.strip()
                            fresh_note.updated_at = datetime.now()
                            note_session.commit()
                            st.success("Not güncellendi!")
                    else:
                        # Create new note
                        new_note = DailyNote(
                            date_=selected_date,
                            note=note_text.strip()
                        )
                        note_session.add(new_note)
                        note_session.commit()
                        st.success("Not kaydedildi!")
                st.rerun()
            except Exception as e:
                st.error(f"Not kaydedilirken hata oluştu: {e}")
                st.info("Sidebar'daki '🔧 Veritabanı Onar' butonunu deneyin.")
        
        elif save_note and not note_text.strip() and existing_note:
            try:
                with get_session() as note_session:
                    # If note is empty and there's an existing note, delete it
                    fresh_note = note_session.get(DailyNote, existing_note.id)
                    if fresh_note:
                        note_session.delete(fresh_note)
                        note_session.commit()
                        st.success("Not silindi!")
                        st.rerun()
            except Exception as e:
                st.error(f"Not silinirken hata oluştu: {e}")
        
        elif delete_note and existing_note:
            st.session_state[f"confirm_delete_note_{selected_date}"] = True
        
        # Delete confirmation
        if st.session_state.get(f"confirm_delete_note_{selected_date}"):
            st.error("Bu günün notunu silmek istediğinizden emin misiniz?")
            
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("✅ Evet, Sil", key=f"confirm_delete_note_yes_{selected_date}", type="primary"):
                    try:
                        with get_session() as note_session:
                            if existing_note:
                                fresh_note = note_session.get(DailyNote, existing_note.id)
                                if fresh_note:
                                    note_session.delete(fresh_note)
                                    note_session.commit()
                                    st.success("Not silindi!")
                        del st.session_state[f"confirm_delete_note_{selected_date}"]
                        st.rerun()
                    except Exception as e:
                        st.error(f"Not silinirken hata oluştu: {e}")
            
            with col_no:
                if st.button("❌ Hayır, İptal", key=f"confirm_delete_note_no_{selected_date}"):
                    del st.session_state[f"confirm_delete_note_{selected_date}"]
                    st.rerun()

        # Button to clear selection and show all sessions
        if st.button("🔄 Tüm Seansları Göster"):
            st.session_state.selected_calendar_date = None
            st.rerun()
    
    else:
        # Show all sessions for the month
        st.subheader(f"📅 {calendar.month_name[selected_month]} {selected_year} - Tüm Seanslar")
        
        if sessions_by_date:
            for session_date in sorted(sessions_by_date.keys()):
                st.write(f"### {session_date.strftime('%d %B %Y (%A)')}")
                
                for session_key, session_data in sessions_by_date[session_date].items():
                    session = session_data['session']
                    course = session_data['course']
                    enrollments = session_data['enrollments']
                    
                    with st.expander(f"🎨 {course.name} - {session.start_time.strftime('%H:%M')}-{session.end_time.strftime('%H:%M')} ({len(enrollments)} kişi)"):
                        col1, col2, col3 = st.columns([3, 3, 2])
                        with col1:
                            st.write(f"**Kapasite:** {session.capacity}")
                            st.write(f"**Kayıtlı:** {len(enrollments)}")
                            if session.notes:
                                st.write(f"**Seans Notu:** {session.notes}")
                        
                        with col2:
                            if session.price_override:
                                st.write(f"**Fiyat:** ₺{session.price_override}")
                            else:
                                st.write(f"**Fiyat:** ₺{course.default_price}")
                        
                        with col3:
                            if st.button("🗑️ Seansı İptal Et", key=f"cancel_all_session_{session.id}", type="secondary"):
                                st.session_state[f"confirm_cancel_all_session_{session.id}"] = True
                        
                        # Session cancellation confirmation
                        if st.session_state.get(f"confirm_cancel_all_session_{session.id}"):
                            st.error(f"**Bu seansı tamamen iptal etmek istediğinizden emin misiniz?**")
                            st.write(f"📅 {session.date.strftime('%d %B %Y')} - {session.start_time.strftime('%H:%M')}-{session.end_time.strftime('%H:%M')}")
                            st.write(f"⚠️ Bu işlem geri alınamaz. Seansta kayıtlı {len(enrollments)} kişi çıkarılacak ve seans silinecek.")
                            
                            col_yes, col_no = st.columns(2)
                            with col_yes:
                                if st.button("✅ Evet, İptal Et", key=f"confirm_cancel_all_yes_{session.id}", type="primary"):
                                    with get_session() as cancel_session:
                                        # Delete all enrollments for this session
                                        session_enrollments = cancel_session.exec(
                                            select(Enrollment).where(Enrollment.session_id == session.id)
                                        ).all()
                                        
                                        for enrollment in session_enrollments:
                                            cancel_session.delete(enrollment)
                                        
                                        # Delete the session
                                        session_to_delete = cancel_session.get(SessionModel, session.id)
                                        if session_to_delete:
                                            cancel_session.delete(session_to_delete)
                                        
                                        cancel_session.commit()
                                        st.success(f"Seans başarıyla iptal edildi!")
                                        del st.session_state[f"confirm_cancel_all_session_{session.id}"]
                                        st.rerun()
                            
                            with col_no:
                                if st.button("❌ Hayır, İptal Etme", key=f"confirm_cancel_all_no_{session.id}"):
                                    del st.session_state[f"confirm_cancel_all_session_{session.id}"]
                                    st.rerun()
                        
                        if enrollments:
                            st.write("**Katılımcılar:**")
                            for i, enroll_data in enumerate(enrollments, 1):
                                enrollment = enroll_data['enrollment']
                                person = enroll_data['person']
                                
                                status_emoji = {
                                    'registered': '📝',
                                    'attended': '✅', 
                                    'canceled': '❌',
                                    'no_show': '👻'
                                }.get(enrollment.status, '📝')
                                
                                # Create columns for person info and remove button
                                col_person, col_remove = st.columns([10, 1])
                                
                                with col_person:
                                    person_info = f"{i}. {status_emoji} **{person.name}**"
                                    if person.phone:
                                        person_info += f" - {person.phone}"
                                    
                                    # Show group label if any
                                    if enrollment.group_label:
                                        person_info += f" - 🏷️ *{enrollment.group_label}*"
                                    
                                    # Show enrollment notes if any
                                    if enrollment.note:
                                        person_info += f"\n   💭 *{enrollment.note}*"
                                    
                                    # Show person notes if any  
                                    if person.notes:
                                        person_info += f"\n   📝 *Kişi Notu: {person.notes}*"
                                    
                                    st.markdown(person_info)
                                
                                with col_remove:
                                    if st.button("🗑️", key=f"remove_all_enrollment_{enrollment.id}", help="Kayıttan Çıkar"):
                                        st.session_state[f"confirm_remove_all_enrollment_{enrollment.id}"] = True
                                
                                # Confirmation dialog for removal
                                if st.session_state.get(f"confirm_remove_all_enrollment_{enrollment.id}"):
                                    st.error(f"**{person.name}** kişisini bu seanstan çıkarmak istediğinizden emin misiniz?")
                                    
                                    col_yes, col_no = st.columns(2)
                                    with col_yes:
                                        if st.button("✅ Evet, Çıkar", key=f"confirm_remove_all_yes_{enrollment.id}", type="primary"):
                                            with get_session() as remove_session:
                                                # Find and delete the enrollment
                                                enrollment_to_remove = remove_session.get(Enrollment, enrollment.id)
                                                if enrollment_to_remove:
                                                    remove_session.delete(enrollment_to_remove)
                                                    remove_session.commit()
                                                    st.success(f"{person.name} seansdan çıkarıldı!")
                                                    del st.session_state[f"confirm_remove_all_enrollment_{enrollment.id}"]
                                                    st.rerun()
                                    
                                    with col_no:
                                        if st.button("❌ Hayır, İptal", key=f"confirm_remove_all_no_{enrollment.id}"):
                                            del st.session_state[f"confirm_remove_all_enrollment_{enrollment.id}"]
                                            st.rerun()
                        else:
                            st.info("Bu seansa henüz kimse kayıt olmamış.")
                
                st.markdown("---")
        else:
            st.info(f"{calendar.month_name[selected_month]} {selected_year} ayında hiç seans bulunmamaktadır.")

# --------- İÇE AKTAR (Excel) ---------
def page_import():
    st.header("📥 İçe Aktar (Excel)")
    st.info("Şablondaki iki sayfayı içe alır: **Eylül 2025 Takvim** (seanslar) ve **Öğrenci Listesi** (kişiler).")

    f = st.file_uploader("Excel seç (.xlsx)", type=["xlsx"])
    if not f:
        return

    try:
        xls = pd.ExcelFile(f)   # openpyxl gerektirir
    except Exception as e:
        st.error(f"Excel açılamadı: {e}")
        st.caption("Not: `pip install openpyxl` kurulu olmalı.")
        return

    # --- Öğrenciler
    if "Öğrenci Listesi" in xls.sheet_names:
        df_p = pd.read_excel(xls, sheet_name="Öğrenci Listesi")

        low = {c.lower(): c for c in df_p.columns}
        def pick(df, *alts):
            for a in alts:
                if a in df.columns: return a
                if a.lower() in low: return low[a.lower()]
            return None

        name_col  = pick(df_p, "Ad Soyad","Ad","İsim","Öğrenci")
        phone_col = pick(df_p, "Telefon","Tel","GSM")
        ig_col    = pick(df_p, "Instagram","IG","İnstagram")
        note_col  = pick(df_p, "Not","Açıklama")

        if not name_col:
            st.warning("Öğrenci Listesi sayfasında 'Ad Soyad' bulunamadı.")
        else:
            with get_session() as s:
                added = 0
                for _, row in df_p.iterrows():
                    name = str(row.get(name_col, "") or "").strip()
                    if not name:
                        continue
                    phone = str(row.get(phone_col, "") or "").strip() or None
                    ig = str(row.get(ig_col, "") or "").strip() or None
                    notes = str(row.get(note_col, "") or "").strip() or None
                    exists = None
                    # Check for duplicate by phone or name (case insensitive)
                    if phone:
                        exists = s.exec(select(Person).where(Person.phone == phone)).first()
                    if not exists:
                        exists = s.exec(select(Person).where(func.lower(Person.name) == func.lower(name))).first()
                    if exists:
                        continue
                    s.add(Person(name=name, phone=phone, instagram=ig, notes=notes, first_visit=date.today()))
                    added += 1
                s.commit()
            st.success(f"Öğrenci Listesi: {added} kişi eklendi")

    # --- Seanslar
    if "Eylül 2025 Takvim" in xls.sheet_names:
        df_s = pd.read_excel(xls, sheet_name="Eylül 2025 Takvim")
        low2 = {c.lower(): c for c in df_s.columns}
        def pick2(df, *alts):
            for a in alts:
                if a in df.columns: return a
                if a.lower() in low2: return low2[a.lower()]
            return None

        c_date  = pick2(df_s, "Tarih","Date")
        c_start = pick2(df_s, "Başlangıç","Baslangic","Start")
        c_end   = pick2(df_s, "Bitiş","Bitis","End")
        c_type  = pick2(df_s, "Tür","Tur","Ders","Course")
        c_cap   = pick2(df_s, "Kapasite","Capacity")
        c_price = pick2(df_s, "Fiyat","Ücret","Price")
        c_notes = pick2(df_s, "Not","Açıklama","Notes")

        if not (c_date and c_start and c_end and c_type):
            st.warning("Takvim sayfasında Tarih, Başlangıç, Bitiş, Tür kolonlarına ihtiyaç var.")
        else:
            with get_session() as s:
                def course_by_type(t):
                    t_norm = (str(t) or "").strip().lower()
                    if "boyama" in t_norm:
                        cname, default = "Boyama", DEFAULT_PRICE_BOYAMA
                    else:
                        cname, default = "Atölye – Kurs", DEFAULT_PRICE_COURSE
                    c = s.exec(select(Course).where(Course.name == cname)).first()
                    if not c:
                        c = Course(name=cname, default_price=default, default_capacity=DEFAULT_CAPACITY)
                        s.add(c); s.commit(); s.refresh(c)
                    return c

                added_s = 0
                for _, row in df_s.iterrows():
                    raw_date = row.get(c_date)
                    raw_st   = row.get(c_start)
                    raw_en   = row.get(c_end)
                    ctype    = row.get(c_type)
                    cap      = row.get(c_cap)
                    price    = row.get(c_price)
                    notes    = row.get(c_notes)

                    if pd.isna(raw_date) or pd.isna(raw_st) or pd.isna(raw_en):
                        continue

                    try:
                        d = pd.to_datetime(raw_date).date()
                    except Exception:
                        continue
                    stime = pd.to_datetime(raw_st).time()
                    etime = pd.to_datetime(raw_en).time()

                    course = course_by_type(ctype)
                    exists = s.exec(select(SessionModel).where(
                        SessionModel.course_id == course.id,
                        SessionModel.date == d,
                        SessionModel.start_time == stime,
                        SessionModel.end_time == etime
                    )).first()
                    if exists:
                        continue

                    s.add(SessionModel(
                        course_id=course.id,
                        date=d,
                        start_time=stime,
                        end_time=etime,
                        capacity=int(cap) if (cap is not None and not pd.isna(cap)) else course.default_capacity,
                        price_override=(float(price) if (price is not None and not pd.isna(price) and float(price) > 0) else None),
                        notes=(None if pd.isna(notes) else str(notes))
                    ))
                    added_s += 1
                s.commit()
            st.success(f"Eylül 2025 Takvim: {added_s} seans eklendi")

    st.success("İçe aktarma tamamlandı. Üst menüden **Ders/Seans** ve **Kişiler** sayfalarına bakabilirsin.")

# ============================ APP ============================
def seed_minimal():
    with get_session() as s:
        if not s.exec(select(Course)).first():
            s.add(Course(name="Atölye – Kurs", default_price=DEFAULT_PRICE_COURSE, default_capacity=DEFAULT_CAPACITY))
            s.add(Course(name="Boyama", default_price=DEFAULT_PRICE_BOYAMA, default_capacity=DEFAULT_CAPACITY))
            s.commit()

# ============================ LOGIN SYSTEM ============================
def login_page():
    """Login sayfası"""
    st.set_page_config(page_title="Nehir Seramik - Giriş", page_icon="🏺", layout="centered")
    
    # Custom CSS for login
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
        max-width: 400px;
        margin: 0 auto;
    }
    .login-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        margin-top: 5rem;
    }
    .login-title {
        color: white;
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="login-container">
        <h2 class="login-title">🏺 Nehir Seramik</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Giriş Yapın")
        username = st.text_input("Kullanıcı Adı", placeholder="nehir.seramik")
        password = st.text_input("Şifre", type="password", placeholder="Şifrenizi girin")
        
        if st.button("Giriş Yap", use_container_width=True):
            if username == "nehir.seramik" and password == "bernaseda":
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("❌ Hatalı kullanıcı adı veya şifre!")

def logout():
    """Çıkış yapma"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def main():
    # Check authentication first
    if not st.session_state.get("authenticated", False):
        login_page()
        return
    
    # Initialize database tables (including new tables)
    try:
        # Force metadata recreation and table creation
        from sqlmodel import SQLModel
        SQLModel.metadata.clear()
        SQLModel.metadata.create_all(ENGINE)
        seed_minimal()  # Ensure basic data exists
        st.sidebar.success("🗃️ Veritabanı hazır!")
    except Exception as e:
        # If DB init fails, show error but continue
        st.error(f"Veritabanı başlatma hatası: {e}")
        st.info("Sidebar'da '🔧 Veritabanı Onar' butonunu deneyin.")
        
    # Force dark theme configuration
    st.set_page_config(
        page_title=APP_TITLE, 
        page_icon="🎨", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Force dark mode with additional JavaScript
    st.markdown("""
        <script>
        // Force dark mode
        document.documentElement.setAttribute('data-theme', 'dark');
        document.body.classList.add('dark-mode');
        
        // Override any light mode settings
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'data-theme') {
                    if (document.documentElement.getAttribute('data-theme') !== 'dark') {
                        document.documentElement.setAttribute('data-theme', 'dark');
                    }
                }
            });
        });
        observer.observe(document.documentElement, { attributes: true });
        </script>
    """, unsafe_allow_html=True)
    
    load_theme()
    init_db()
    seed_minimal()

    st.sidebar.title("🏺 Nehir Seramik")
    st.sidebar.write(f"Hoş geldin, {st.session_state.get('username', 'Kullanıcı')}!")
    
    # DEBUG: Force table creation button (temporary)
    if st.sidebar.button("🔧 Veritabanı Onar (Geçici)"):
        try:
            init_db()
            st.sidebar.success("Veritabanı tabloları oluşturuldu!")
        except Exception as e:
            st.sidebar.error(f"Hata: {e}")
    
    # Logout button
    if st.sidebar.button("🚪 Çıkış Yap"):
        logout()

    # ⚡ Hızlı öğrenci ekleme
    with st.sidebar.expander("⚡ Hızlı Öğrenci Ekle"):
        with st.form("quick_person"):
            q_name  = st.text_input("Ad Soyad")
            q_phone = st.text_input("Telefon")
            q_ig    = st.text_input("Instagram")
            q_ok    = st.form_submit_button("Kaydet")
        if q_ok and q_name.strip():
            with get_session() as s:
                # Duplicate check - case insensitive
                existing = s.exec(
                    select(Person).where(
                        (func.lower(Person.name) == func.lower(q_name.strip())) | 
                        (Person.phone == q_phone.strip() if q_phone.strip() else False)
                    )
                ).first()
                
                if existing:
                    st.sidebar.warning(f"Bu kişi zaten kayıtlı: {existing.name}")
                else:
                    s.add(Person(name=q_name.strip(), phone=(q_phone.strip() or None), instagram=(q_ig.strip() or None), first_visit=date.today()))
                    s.commit()
                    st.sidebar.success("Öğrenci eklendi")

    page = st.sidebar.radio(
        "Menü",
        ["Dashboard", "Kişiler", "Ders/Seans", "Takvim", "Ödemeler", "Parça", "Stok", "Raporlar", "İçe Aktar"],
        index=0,
    )

    if page == "Dashboard":
        page_dashboard()
    elif page == "Kişiler":
        page_people()
    elif page == "Ders/Seans":
        page_courses_sessions()
    elif page == "Takvim":
        page_calendar()
    elif page == "Ödemeler":
        page_payments()
    elif page == "Parça":
        page_pieces()
    elif page == "Stok":
        page_stock()
    elif page == "Raporlar":
        page_reports()
    elif page == "İçe Aktar":
        page_import()

if __name__ == "__main__":
    main()
