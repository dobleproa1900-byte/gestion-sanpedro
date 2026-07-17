import streamlit as st
import pandas as pd
import requests
import datetime
import uuid
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="ConcejalIA — Gestión Legislativa",
    page_icon="🏛️",
    layout="wide"
)

# ==========================================
# ESTILOS PERSONALIZADOS
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');

:root {
    --primary: #6366f1;
    --primary-light: #818cf8;
    --violet: #8b5cf6;
    --accent: #22d3ee;
    --success: #34d399;
    --warning: #fbbf24;
    --danger: #f87171;
    --bg-deep: #070714;
    --glass-bg: rgba(23, 23, 54, 0.55);
    --glass-bg-soft: rgba(30, 30, 68, 0.40);
    --glass-border: rgba(139, 92, 246, 0.22);
    --glass-highlight: rgba(255, 255, 255, 0.06);
    --text-main: #e2e8f0;
    --text-muted: #94a3b8;
}

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ---- Fondo global: aurora institucional azul/violeta ---- */
.stApp {
    background:
        radial-gradient(ellipse 80% 50% at 15% -10%, rgba(99, 102, 241, 0.30), transparent 60%),
        radial-gradient(ellipse 60% 45% at 85% 5%, rgba(139, 92, 246, 0.24), transparent 60%),
        radial-gradient(ellipse 70% 60% at 50% 110%, rgba(34, 211, 238, 0.10), transparent 55%),
        linear-gradient(180deg, #0b0b22 0%, var(--bg-deep) 100%);
    background-attachment: fixed;
    color: var(--text-main);
}

/* Chrome de Streamlit fuera de vista */
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }

/* ---- Animaciones ---- */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes shimmer {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.block-container { animation: fadeUp 0.5s ease both; }

/* ---- Tipografía ---- */
h1, h2, h3 { font-family: 'Sora', 'Inter', sans-serif; color: #f1f5f9 !important; letter-spacing: -0.02em; font-weight: 700; }
[data-testid="stMarkdownContainer"] p, .stApp p, .stApp li { color: var(--text-main); }
[data-testid="stWidgetLabel"] p { color: #c7d2fe !important; font-weight: 600; font-size: 0.85rem; }
[data-testid="stCaptionContainer"] p, small { color: var(--text-muted) !important; }
hr { border-color: rgba(139, 92, 246, 0.18) !important; }

/* ---- Header principal: panel de vidrio con brillo animado ---- */
.app-header {
    position: relative;
    background: linear-gradient(135deg, rgba(49,46,129,0.75) 0%, rgba(76,29,149,0.55) 55%, rgba(30,27,75,0.72) 100%);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1px solid var(--glass-border);
    padding: 1.9rem 2.2rem;
    border-radius: 20px;
    margin-bottom: 0.75rem;
    box-shadow: 0 18px 50px -18px rgba(99, 102, 241, 0.45), inset 0 1px 0 var(--glass-highlight);
    overflow: hidden;
    animation: fadeUp 0.6s ease both;
}
.app-header::before {
    content: "";
    position: absolute; inset: 0;
    background: linear-gradient(120deg, transparent 30%, rgba(255,255,255,0.07) 50%, transparent 70%);
    background-size: 220% 220%;
    animation: shimmer 7s ease-in-out infinite;
    pointer-events: none;
}
.app-header h1 {
    font-size: 1.85rem; margin: 0; font-weight: 800;
    background: linear-gradient(90deg, #ffffff 0%, #c7d2fe 55%, #a5b4fc 100%);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
}
.app-header p { color: #a5b4fc !important; font-size: 1rem; margin: 0.35rem 0 0 0; }

/* ---- Tarjetas KPI: glassmorphism con acento superior ---- */
.kpi-card {
    position: relative;
    background: var(--glass-bg);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-radius: 16px;
    padding: 1.15rem 1.35rem;
    border: 1px solid var(--glass-border);
    box-shadow: 0 10px 30px -14px rgba(0,0,0,0.6), inset 0 1px 0 var(--glass-highlight);
    overflow: hidden;
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    animation: fadeUp 0.55s ease both;
}
.kpi-card::before {
    content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, var(--kpi-color, var(--primary)), transparent 85%);
}
.kpi-card:hover {
    transform: translateY(-4px);
    border-color: rgba(139,92,246,0.45);
    box-shadow: 0 18px 40px -14px rgba(99,102,241,0.35), inset 0 1px 0 var(--glass-highlight);
}
.kpi-card .kpi-label { color: var(--text-muted); font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; }
.kpi-card .kpi-value { color: #f8fafc; font-size: 2.1rem; font-weight: 800; line-height: 1.25; font-family: 'Sora', sans-serif; }

/* ---- Pestañas ---- */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: var(--glass-bg-soft);
    backdrop-filter: blur(12px);
    padding: 6px;
    border-radius: 14px;
    border: 1px solid var(--glass-border);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px; padding: 10px 20px; font-weight: 600;
    color: var(--text-muted); background: transparent;
    transition: color 0.2s ease, background 0.2s ease;
}
.stTabs [data-baseweb="tab"]:hover { color: #e0e7ff; background: rgba(99,102,241,0.12); }
.stTabs [aria-selected="true"] {
    background: linear-gradient(120deg, var(--primary), var(--violet)) !important;
    color: #ffffff !important;
    box-shadow: 0 6px 18px -6px rgba(99,102,241,0.6);
}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { background: transparent; }

/* ---- Botones ---- */
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
    border-radius: 12px;
    font-weight: 600;
    background: var(--glass-bg);
    color: var(--text-main);
    border: 1px solid var(--glass-border);
    backdrop-filter: blur(10px);
    transition: all 0.2s ease;
}
.stButton > button[kind^="primary"], .stFormSubmitButton > button[kind^="primary"], .stDownloadButton > button[kind^="primary"] {
    background: linear-gradient(120deg, var(--primary) 0%, var(--violet) 100%) !important;
    border: none !important;
    color: #ffffff !important;
    box-shadow: 0 8px 24px -8px rgba(99,102,241,0.65);
}
.stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover {
    transform: translateY(-2px);
    border-color: rgba(139,92,246,0.5);
    box-shadow: 0 12px 28px -10px rgba(139,92,246,0.55);
    color: #ffffff;
}

/* ---- Formularios: panel de vidrio ---- */
[data-testid="stForm"] {
    background: var(--glass-bg);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    padding: 1.9rem 2.1rem;
    border-radius: 22px;
    border: 1px solid var(--glass-border);
    box-shadow: 0 24px 60px -24px rgba(0,0,0,0.65), inset 0 1px 0 var(--glass-highlight);
}

/* ---- Campos de entrada ---- */
.stTextInput input, .stTextArea textarea, .stNumberInput input, .stDateInput input {
    background: rgba(10, 10, 30, 0.6) !important;
    color: var(--text-main) !important;
    border: 1px solid rgba(139,92,246,0.25) !important;
    border-radius: 10px !important;
    caret-color: var(--primary-light);
}
.stTextInput input:focus, .stTextArea textarea:focus, .stDateInput input:focus {
    border-color: var(--primary-light) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.25) !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder { color: #64748b !important; }
[data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="base-input"] {
    background: transparent !important;
    border-color: transparent !important;
}

/* ---- Selects y menús desplegables ---- */
.stSelectbox [data-baseweb="select"] > div, .stMultiSelect [data-baseweb="select"] > div {
    background: rgba(10, 10, 30, 0.6) !important;
    border: 1px solid rgba(139,92,246,0.25) !important;
    border-radius: 10px !important;
    color: var(--text-main) !important;
}
.stSelectbox [data-baseweb="select"] svg { fill: #a5b4fc; }
[data-baseweb="popover"] [data-baseweb="menu"], ul[data-testid="stSelectboxVirtualDropdown"] {
    background: #14142e !important;
    border: 1px solid var(--glass-border) !important;
}
[data-baseweb="menu"] li, [role="option"] { background: transparent !important; color: var(--text-main) !important; }
[data-baseweb="menu"] li:hover, [role="option"]:hover { background: rgba(99,102,241,0.2) !important; }
[data-baseweb="calendar"] { background: #14142e !important; color: var(--text-main) !important; }

/* ---- Alertas y avisos ---- */
[data-testid="stAlert"] {
    background: var(--glass-bg-soft);
    backdrop-filter: blur(10px);
    border: 1px solid var(--glass-border);
    border-radius: 14px;
}
[data-testid="stAlert"] p { color: var(--text-main) !important; }

/* ---- Tablas y bloques de código ---- */
[data-testid="stDataFrame"], [data-testid="stCodeBlock"] {
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid var(--glass-border);
    box-shadow: 0 14px 34px -18px rgba(0,0,0,0.6);
}
[data-testid="stCodeBlock"] pre { background: rgba(10,10,30,0.75) !important; }
[data-testid="stCodeBlock"] code { color: #c7d2fe !important; }

/* ---- Expander / status ---- */
details {
    background: var(--glass-bg-soft) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 14px !important;
}
details summary { color: var(--text-main) !important; }

/* ---- Scrollbar ---- */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.35); border-radius: 8px; }
::-webkit-scrollbar-thumb:hover { background: rgba(139,92,246,0.55); }

/* ---- Pantalla de login ---- */
.login-hero { text-align: center; margin-bottom: 1.5rem; animation: fadeUp 0.6s ease both; }
.login-hero .login-icon { font-size: 3.2rem; line-height: 1; filter: drop-shadow(0 6px 18px rgba(139,92,246,0.6)); }
.login-hero h1 {
    font-weight: 800; margin: 0.3rem 0 0 0;
    background: linear-gradient(90deg, #e0e7ff 0%, #a5b4fc 50%, #a78bfa 100%);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
}
.login-hero p { color: var(--text-muted); font-size: 1rem; margin-top: 0.35rem; }
</style>
""", unsafe_allow_html=True)

# 🔒 SEGURIDAD: URLs ocultas usando Streamlit Secrets
GAS_WEBAPP_URL = st.secrets.get("GAS_WEBAPP_URL", "")
SHEETS_CSV_URL = st.secrets.get("SHEETS_CSV_URL", "")
# CSV público con coordenadas GPS (latitud/longitud) para el mapa territorial
MAPA_CSV_URL = st.secrets.get(
    "MAPA_CSV_URL",
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vQOwmQnvQKFOWA5_FbTUxzVH-XNNPIf5pyum_1dD1JdeH_JoVVBKAPokWyCHuKU9fvxhNPSas2A20zu"
    "/pub?output=csv",
)
DISTRITO = st.secrets.get("DISTRITO", "San Pedro")
DEMO_USER = st.secrets.get("DEMO_USER", "concejal")
DEMO_PASS = st.secrets.get("DEMO_PASS", "sanpedro2026")

# ==========================================
# LOGIN
# ==========================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class='login-hero'>
                <div class='login-icon'>🏛️</div>
                <h1>ConcejalIA</h1>
                <p>Gestión Legislativa Inteligente — {DISTRITO}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        with st.form("login_form"):
            usuario = st.text_input("Usuario:", placeholder="concejal")
            clave = st.text_input("Contraseña:", type="password", placeholder="••••••••")
            st.caption("ℹ️ Demo: usuario `concejal` / contraseña `sanpedro2026`")
            if st.form_submit_button("Ingresar al Sistema", type="primary", use_container_width=True):
                if usuario == DEMO_USER and clave == DEMO_PASS:
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")
    st.stop()

# ==========================================
# DATOS DE DEMO (cuando Sheets está vacío)
# ==========================================
DATOS_DEMO = [
    {"ID": "demo0001", "Fecha": "2026-03-10", "Nombre": "María González", "Barrio": "Centro", "Tipo": "Alumbrado", "Descripcion": "Farolas apagadas en Av. Belgrano desde hace 3 semanas.", "Estado": "Pendiente"},
    {"ID": "demo0002", "Fecha": "2026-03-12", "Nombre": "Carlos Pérez", "Barrio": "Bajo Tala", "Tipo": "Bacheo/Calles", "Descripcion": "Bache peligroso en cruce de Rivadavia y San Martín.", "Estado": "Pendiente"},
    {"ID": "demo0003", "Fecha": "2026-03-14", "Nombre": "Ana Rodríguez", "Barrio": "Santa Lucía", "Tipo": "Agua/Cloacas", "Descripcion": "Pérdida de agua en la esquina de Mitre y Urquiza.", "Estado": "Solucionado"},
    {"ID": "demo0004", "Fecha": "2026-03-15", "Nombre": "Juan Martínez", "Barrio": "Las Casuarinas", "Tipo": "Basura/Limpieza", "Descripcion": "Microbasural en descampado lindero al parque.", "Estado": "En gestión"},
    {"ID": "demo0005", "Fecha": "2026-03-18", "Nombre": "Laura Díaz", "Barrio": "Centro", "Tipo": "Seguridad", "Descripcion": "Solicitan mayor presencia policial en el sector comercial.", "Estado": "Pendiente"},
    {"ID": "demo0006", "Fecha": "2026-03-20", "Nombre": "Roberto Sánchez", "Barrio": "Bajo Tala", "Tipo": "Alumbrado", "Descripcion": "Calle oscura en el pasaje Los Aromos, riesgo de accidentes.", "Estado": "Pendiente"},
    {"ID": "demo0007", "Fecha": "2026-03-22", "Nombre": "Marta López", "Barrio": "Villa del Parque", "Tipo": "Bacheo/Calles", "Descripcion": "Calle de tierra sin mantenimiento, imposible transitar con lluvia.", "Estado": "Pendiente"},
    {"ID": "demo0008", "Fecha": "2026-03-25", "Nombre": "Diego Fernández", "Barrio": "Santa Lucía", "Tipo": "Basura/Limpieza", "Descripcion": "Recolección de residuos irregular, varios días sin pasar.", "Estado": "Solucionado"},
    {"ID": "demo0009", "Fecha": "2026-03-28", "Nombre": "Susana Torres", "Barrio": "Centro", "Tipo": "Agua/Cloacas", "Descripcion": "Desborde de cloaca en Lavalle al 300.", "Estado": "En gestión"},
    {"ID": "demo0010", "Fecha": "2026-04-01", "Nombre": "Pablo Acosta", "Barrio": "Las Casuarinas", "Tipo": "Seguridad", "Descripcion": "Falta de señalización en cruce escolar peligroso.", "Estado": "Pendiente"},
    {"ID": "demo0011", "Fecha": "2026-04-03", "Nombre": "Valeria Romero", "Barrio": "Villa del Parque", "Tipo": "Alumbrado", "Descripcion": "Transformador quemado deja sin luz a 3 cuadras.", "Estado": "En gestión"},
    {"ID": "demo0012", "Fecha": "2026-04-05", "Nombre": "Héctor Benítez", "Barrio": "Bajo Tala", "Tipo": "Bacheo/Calles", "Descripcion": "Cuneta tapada provoca inundación en días de lluvia.", "Estado": "Solucionado"},
]

# ==========================================
# CARGA DE DATOS CON FALLBACK A DEMO
# ==========================================
@st.cache_data(ttl=60)
def cargar_datos():
    try:
        if not SHEETS_CSV_URL:
            raise ValueError("Sin URL")
        df = pd.read_csv(SHEETS_CSV_URL)
        df = df.dropna(how='all')
        if df.empty:
            raise ValueError("Vacío")
        return df, False
    except Exception:
        return pd.DataFrame(DATOS_DEMO), True


def _resolver_columna(columnas, candidatos):
    """Devuelve el nombre real de columna coincidiendo sin importar mayúsculas/espacios."""
    normalizado = {str(c).strip().lower(): c for c in columnas}
    for cand in candidatos:
        if cand.lower() in normalizado:
            return normalizado[cand.lower()]
    return None


def _parse_coord(valor):
    """Convierte coordenadas del Sheets (-33.675.761 o 'No disponible') a float."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return None
    s = str(valor).strip().replace(",", ".")
    if s.lower() in ("", "nan", "none", "no disponible", "n/a"):
        return None
    # Sheets a veces formatea -33.675761 como -33.675.761
    if s.count(".") > 1:
        partes = s.split(".")
        s = partes[0] + "." + "".join(partes[1:])
    try:
        return float(s)
    except ValueError:
        return None


@st.cache_data(ttl=60)
def cargar_datos_mapa(csv_url):
    """Lee reclamos con coordenadas desde Google Sheets. Fallback a demo si no hay lat/lon válidos."""
    coords_demo = pd.DataFrame([
        {"Nombre": "María González", "Barrio": "Centro", "Tipo": "Alumbrado", "Estado": "Pendiente", "lat": -33.6789, "lon": -59.6721},
        {"Nombre": "Carlos Pérez", "Barrio": "Bajo Tala", "Tipo": "Bacheo/Calles", "Estado": "Pendiente", "lat": -33.6823, "lon": -59.6698},
        {"Nombre": "Ana Rodríguez", "Barrio": "Santa Lucía", "Tipo": "Agua/Cloacas", "Estado": "Solucionado", "lat": -33.6756, "lon": -59.6745},
        {"Nombre": "Juan Martínez", "Barrio": "Las Casuarinas", "Tipo": "Basura/Limpieza", "Estado": "En gestión", "lat": -33.6801, "lon": -59.6712},
        {"Nombre": "Laura Díaz", "Barrio": "Centro", "Tipo": "Seguridad", "Estado": "Pendiente", "lat": -33.6778, "lon": -59.6734},
        {"Nombre": "Roberto Sánchez", "Barrio": "Bajo Tala", "Tipo": "Alumbrado", "Estado": "Pendiente", "lat": -33.6834, "lon": -59.6689},
        {"Nombre": "Marta López", "Barrio": "Villa del Parque", "Tipo": "Bacheo/Calles", "Estado": "Pendiente", "lat": -33.6745, "lon": -59.6756},
        {"Nombre": "Diego Fernández", "Barrio": "Santa Lucía", "Tipo": "Basura/Limpieza", "Estado": "Solucionado", "lat": -33.6767, "lon": -59.6723},
        {"Nombre": "Susana Torres", "Barrio": "Centro", "Tipo": "Agua/Cloacas", "Estado": "En gestión", "lat": -33.6792, "lon": -59.6709},
        {"Nombre": "Pablo Acosta", "Barrio": "Las Casuarinas", "Tipo": "Seguridad", "Estado": "Pendiente", "lat": -33.6812, "lon": -59.6741},
        {"Nombre": "Valeria Romero", "Barrio": "Villa del Parque", "Tipo": "Alumbrado", "Estado": "En gestión", "lat": -33.6734, "lon": -59.6768},
        {"Nombre": "Héctor Benítez", "Barrio": "Bajo Tala", "Tipo": "Bacheo/Calles", "Estado": "Solucionado", "lat": -33.6845, "lon": -59.6701},
    ])
    try:
        if not csv_url:
            raise ValueError("Sin URL")
        df = pd.read_csv(csv_url)
        df = df.dropna(how="all")
        if df.empty:
            raise ValueError("Vacío")

        df.columns = [str(c).strip() for c in df.columns]
        col_lat = _resolver_columna(df.columns, ["latitud", "lat", "latitude", "y"])
        col_lon = _resolver_columna(df.columns, ["longitud", "lon", "lng", "longitude", "x"])
        if not col_lat or not col_lon:
            raise ValueError("Sin columnas de coordenadas")

        df["lat"] = df[col_lat].map(_parse_coord)
        df["lon"] = df[col_lon].map(_parse_coord)
        df = df.dropna(subset=["lat", "lon"])
        if df.empty:
            raise ValueError("Coordenadas vacías")

        col_nombre = _resolver_columna(df.columns, ["Nombre", "nombre", "ID", "id"])
        col_barrio = _resolver_columna(df.columns, ["Barrio", "barrio", "direccion", "Direccion"])
        col_tipo = _resolver_columna(df.columns, ["Tipo", "tipo", "categoria", "Categoria"])
        col_estado = _resolver_columna(df.columns, ["Estado", "estado"])

        out = pd.DataFrame({
            "Nombre": df[col_nombre] if col_nombre else (df[col_barrio] if col_barrio else "Sin nombre"),
            "Barrio": df[col_barrio] if col_barrio else "Sin barrio",
            "Tipo": df[col_tipo] if col_tipo else "Otros",
            "Estado": df[col_estado] if col_estado else "Pendiente",
            "lat": df["lat"],
            "lon": df["lon"],
        })
        return out, False
    except Exception:
        return coords_demo, True


def colorear_estado(val):
    val_lower = str(val).lower()
    if val_lower == 'pendiente':
        return 'color: #f87171; font-weight: bold;'
    elif val_lower == 'solucionado':
        return 'color: #34d399; font-weight: bold;'
    elif val_lower == 'en gestión':
        return 'color: #fbbf24; font-weight: bold;'
    return ''

# ==========================================
# HEADER Y LOGOUT
# ==========================================
col_titulo, col_logout = st.columns([5, 1])
with col_titulo:
    st.markdown(
        f"""
        <div class="app-header">
            <h1>🏛️ Sistema de Gestión Territorial y Asistencia Legislativa</h1>
            <p>Herramienta de Inteligencia Local para Concejales — {DISTRITO}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
with col_logout:
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🚪 Cerrar sesión", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

# Carga de datos
df_reclamos, es_demo = cargar_datos()

if es_demo:
    st.info("📋 **Modo Demo activo** — Mostrando datos de ejemplo. Conectá tu Google Sheets para ver datos reales.")

# ==========================================
# PESTAÑAS
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Tablero de Control",
    "📝 Registro de Reclamos", 
    "🤖 Asistente de Ordenanzas IA",
    "📍 Mapa Territorial"
])

# ==========================================
# PESTAÑA 1: TABLERO DE CONTROL
# ==========================================
with tab1:
    st.header("Análisis de Situación Territorial")

    df_reclamos.columns = [c.strip() for c in df_reclamos.columns]
    total_reclamos = len(df_reclamos)

    estado_col = "Estado" if "Estado" in df_reclamos.columns else df_reclamos.columns[-1]
    pendientes = len(df_reclamos[df_reclamos[estado_col].str.lower() == "pendiente"])
    en_gestion = len(df_reclamos[df_reclamos[estado_col].str.lower() == "en gestión"])
    solucionados = len(df_reclamos[df_reclamos[estado_col].str.lower() == "solucionado"])

    def kpi_card(col, label, value, color):
        col.markdown(
            f"""
            <div class="kpi-card" style="--kpi-color:{color};">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi_card(kpi1, "🚨 Total Reclamos", total_reclamos, "#818cf8")
    kpi_card(kpi2, "⏳ Pendientes", pendientes, "#f87171")
    kpi_card(kpi3, "🔄 En Gestión", en_gestion, "#fbbf24")
    kpi_card(kpi4, "✅ Solucionados", solucionados, "#34d399")

    st.markdown("---")

    g1, g2 = st.columns(2)

    PALETA_CATEGORICA = ["#818cf8", "#22d3ee", "#fbbf24", "#f87171", "#34d399", "#a78bfa"]

    def estilizar_layout(fig):
        fig.update_layout(
            margin=dict(l=0, r=0, t=30, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#e2e8f0"),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e2e8f0")),
            hoverlabel=dict(bgcolor="#14142e", font=dict(color="#e2e8f0"), bordercolor="rgba(139,92,246,0.4)")
        )
        fig.update_xaxes(gridcolor="rgba(148,163,184,0.12)", zerolinecolor="rgba(148,163,184,0.25)",
                         linecolor="rgba(148,163,184,0.25)", tickfont=dict(color="#94a3b8"))
        fig.update_yaxes(gridcolor="rgba(148,163,184,0.12)", zerolinecolor="rgba(148,163,184,0.25)",
                         linecolor="rgba(148,163,184,0.25)", tickfont=dict(color="#94a3b8"))
        return fig

    with g1:
        st.subheader("📍 Reclamos por Barrio / Localidad")
        if "Barrio" in df_reclamos.columns:
            barrio_counts = df_reclamos["Barrio"].value_counts().reset_index()
            barrio_counts.columns = ["Barrio", "Cantidad"]
            fig_bar = px.bar(barrio_counts, x="Barrio", y="Cantidad",
                             color="Cantidad",
                             color_continuous_scale=["#312e81", "#818cf8"], text_auto=True)
            estilizar_layout(fig_bar).update_layout(
                xaxis_title="", yaxis_title="Cant. de Reclamos",
                coloraxis_colorbar=dict(tickfont=dict(color="#94a3b8"), title_font=dict(color="#94a3b8"))
            )
            fig_bar.update_traces(textfont_color="#e2e8f0")
            st.plotly_chart(fig_bar, use_container_width=True)

    with g2:
        st.subheader("💡 Problemáticas más Frecuentes")
        if "Tipo" in df_reclamos.columns:
            tipo_counts = df_reclamos["Tipo"].value_counts().reset_index()
            tipo_counts.columns = ["Tipo", "Cantidad"]
            fig_pie = px.pie(tipo_counts, names="Tipo", values="Cantidad", hole=0.4,
                             color_discrete_sequence=PALETA_CATEGORICA)
            estilizar_layout(fig_pie)
            st.plotly_chart(fig_pie, use_container_width=True)

    # Gráfico de evolución temporal
    if "Fecha" in df_reclamos.columns:
        st.subheader("📈 Evolución de Reclamos en el Tiempo")
        try:
            df_reclamos["Fecha"] = pd.to_datetime(df_reclamos["Fecha"])
            evolucion = df_reclamos.groupby("Fecha").size().reset_index(name="Cantidad")
            fig_line = px.line(evolucion, x="Fecha", y="Cantidad", markers=True)
            fig_line.update_traces(line_color="#818cf8", marker=dict(color="#22d3ee", size=8))
            estilizar_layout(fig_line)
            st.plotly_chart(fig_line, use_container_width=True)
        except Exception:
            pass

    st.markdown("---")
    st.subheader("📋 Detalle de las Demandas Ciudadanas")

    # Filtros
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        if "Barrio" in df_reclamos.columns:
            barrios_filtro = ["Todos"] + sorted(df_reclamos["Barrio"].dropna().unique().tolist())
            barrio_sel = st.selectbox("Filtrar por Barrio:", barrios_filtro)
    with col_f2:
        if "Estado" in df_reclamos.columns:
            estados_filtro = ["Todos"] + sorted(df_reclamos["Estado"].dropna().unique().tolist())
            estado_sel = st.selectbox("Filtrar por Estado:", estados_filtro)

    df_filtrado = df_reclamos.copy()
    if barrio_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Barrio"] == barrio_sel]
    if estado_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Estado"] == estado_sel]

    columnas_estado = [estado_col] if estado_col in df_filtrado.columns else []
    df_estilizado = df_filtrado.style.map(colorear_estado, subset=columnas_estado)
    st.dataframe(df_estilizado, use_container_width=True, hide_index=True)

    csv_export = df_filtrado.to_csv(index=False).encode('utf-8')
    col_descarga, _ = st.columns([1, 3])
    with col_descarga:
        st.download_button(
            label="📥 Exportar Reporte a CSV",
            data=csv_export,
            file_name=f"Reporte_{DISTRITO}_{datetime.date.today()}.csv",
            mime="text/csv",
            use_container_width=True
        )

# ==========================================
# PESTAÑA 2: REGISTRO DE RECLAMOS
# ==========================================
with tab2:
    st.header("Ingreso de Demandas de Vecinos")
    st.caption("Los datos ingresados aquí impactan directo en la nube y actualizan el Tablero de Control al instante.")

    with st.form("form_avanzado", clear_on_submit=True):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            nombre = st.text_input("Nombre y Apellido del Vecino")
            barrio = st.text_input("Barrio / Paraje (ej: Centro, Bajo Tala, Santa Lucía)")
            tipo = st.selectbox(
                "Categoría del Problema",
                ["Alumbrado", "Bacheo/Calles", "Agua/Cloacas", "Basura/Limpieza", "Seguridad", "Otros"]
            )
        with col_f2:
            descripcion = st.text_area("Detalles del Reclamo / Notas de campo")
            fecha = st.date_input("Fecha de recepción", datetime.date.today())
            estado_nuevo = st.selectbox("Estado inicial:", ["Pendiente", "En gestión", "Solucionado"])

        btn_guardar = st.form_submit_button("⚡ Registrar e Impactar en la Nube")

        if btn_guardar:
            if nombre and barrio and descripcion:
                if es_demo:
                    st.warning("⚠️ Modo demo activo. Conectá tu Google Sheets para guardar reclamos reales.")
                else:
                    id_unico = str(uuid.uuid4())[:8]
                    datos = {
                        "id": id_unico,
                        "fecha": str(fecha),
                        "nombre": nombre,
                        "barrio": barrio,
                        "tipo": tipo,
                        "descripcion": descripcion,
                        "estado": estado_nuevo
                    }
                    try:
                        with st.status("📡 Conectando con la base de datos...", expanded=True) as status:
                            st.write("Enviando paquete de datos...")
                            res = requests.post(GAS_WEBAPP_URL, json=datos, timeout=10)
                            if res.json().get("success"):
                                status.update(label="Reclamo registrado con éxito", state="complete", expanded=False)
                                st.toast(f"✅ ¡Guardado! ID: {id_unico}", icon="🎉")
                                st.balloons()
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                status.update(label="Error en el guardado", state="error", expanded=False)
                                st.error("Error al procesar en la hoja de cálculo.")
                    except Exception as e:
                        st.error(f"Error de conexión: {e}")
            else:
                st.warning("Por favor, completa los campos obligatorios.")

# ==========================================
# PESTAÑA 3: ASISTENTE DE ORDENANZAS IA
# ==========================================
with tab3:
    st.header("🤖 Redactor de Proyectos de Ordenanza Inteligente")
    st.caption("Convierta de forma automática las demandas vecinales en proyectos legislativos listos para su presentación.")

    df_reclamos["_idx"] = range(len(df_reclamos))
    opciones_reclamos = [f"{i} | {row['Barrio']} ({row['Tipo']})" for i, row in df_reclamos.iterrows()]
    reclamo_seleccionado = st.selectbox("Selecciona el reclamo del vecino para procesar:", opciones_reclamos)

    sel_idx = int(reclamo_seleccionado.split(" | ")[0])
    datos_fila = df_reclamos.loc[sel_idx]

    tipo_proyecto = st.radio("Tipo de documento técnico a generar:", ["Proyecto de Ordenanza", "Minuta de Comunicación / Pedido de Informes"])

    if st.button("✨ Generar Borrador Legislativo"):
        with st.spinner("Generando estructura del proyecto normativo..."):

            borrador = f"""HONORABLE CONCEJO DELIBERANTE DE {DISTRITO.upper()}

VISTO:
El reclamo registrado bajo el expediente N° {datos_fila['ID']}, iniciado por el/la vecino/a {datos_fila['Nombre']} referente a una problemática de {datos_fila['Tipo']} en el barrio {datos_fila['Barrio']}, y;

CONSIDERANDO:
Que el vecino manifiesta lo siguiente: "{datos_fila['Descripcion']}".
Que es deber fundamental de este Cuerpo Deliberativo velar por el bienestar, la infraestructura urbana y la seguridad de todos los habitantes del partido de {DISTRITO}.
Que las deficiencias en materia de {datos_fila['Tipo']} impactan negativamente en la calidad de vida diaria del barrio {datos_fila['Barrio']}.

POR ELLO:
EL HONORABLE CONCEJO DELIBERANTE DE {DISTRITO.upper()}
SANCIONA CON FUERZA DE {tipo_proyecto.upper()}

ARTÍCULO 1°: Encomiéndase al Departamento Ejecutivo Municipal, a través del área que corresponda, a realizar las obras de reparación, mantenimiento y/o solución definitiva en relación a "{datos_fila['Tipo']}" en la zona delimitada del barrio {datos_fila['Barrio']}.

ARTÍCULO 2°: Establécese un plazo de ejecución perentorio no mayor a quince (15) días corridos desde la promulgación de la presente para dar inicio a las tareas de relevamiento en el sector.

ARTÍCULO 3°: De forma."""

            st.subheader("📄 Borrador Generado")
            st.code(borrador, language="text")
            st.success("📋 ¡Proyecto listo!")

            # Descarga del borrador como .txt
            st.download_button(
                label="📥 Descargar Borrador (.txt)",
                data=borrador.encode("utf-8"),
                file_name=f"Ordenanza_{datos_fila['ID']}_{DISTRITO}.txt",
                mime="text/plain"
            )

# ==========================================
# PESTAÑA 4: MAPA TERRITORIAL
# ==========================================
with tab4:
    st.header("📍 Mapa Territorial de Reclamos")
    st.caption("Visualización geográfica de los reclamos vecinales por barrio y categoría.")

    df_mapa, mapa_es_demo = cargar_datos_mapa(MAPA_CSV_URL)
    if mapa_es_demo:
        st.info("📍 Sin coordenadas reales en la planilla — mostrando ubicaciones de ejemplo.")
    else:
        st.success(f"📍 Mostrando {len(df_mapa)} reclamos con GPS real desde Google Sheets.")

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        tipo_mapa = st.multiselect("Filtrar por categoría:", df_mapa["Tipo"].unique().tolist(), default=df_mapa["Tipo"].unique().tolist())
    with col_m2:
        estado_mapa = st.multiselect("Filtrar por estado:", df_mapa["Estado"].unique().tolist(), default=df_mapa["Estado"].unique().tolist())

    df_mapa_filtrado = df_mapa[df_mapa["Tipo"].isin(tipo_mapa) & df_mapa["Estado"].isin(estado_mapa)]

    if len(df_mapa_filtrado) > 0:
        centro_lat = float(df_mapa_filtrado["lat"].mean())
        centro_lon = float(df_mapa_filtrado["lon"].mean())
    else:
        centro_lat, centro_lon = -33.679, -59.672

    fig_mapa = px.scatter_mapbox(
        df_mapa_filtrado,
        lat="lat",
        lon="lon",
        color="Tipo",
        hover_name="Nombre",
        hover_data={"Barrio": True, "Tipo": True, "Estado": True, "lat": False, "lon": False},
        size_max=15,
        zoom=13,
        center={"lat": centro_lat, "lon": centro_lon},
        mapbox_style="open-street-map",
        title="Mapa de Reclamos — San Pedro",
        height=500,
        color_discrete_map={
            "Alumbrado": "#f59e0b",
            "Bacheo/Calles": "#ef4444",
            "Agua/Cloacas": "#3b82f6",
            "Basura/Limpieza": "#10b981",
            "Seguridad": "#8b5cf6"
        }
    )
    fig_mapa.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_mapa, use_container_width=True)

    st.markdown("---")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.subheader("🏘️ Reclamos por barrio")
        barrio_counts = df_mapa_filtrado["Barrio"].value_counts().reset_index()
        barrio_counts.columns = ["Barrio", "Cantidad"]
        fig_barrio = px.bar(barrio_counts, x="Barrio", y="Cantidad",
                           color="Cantidad", color_continuous_scale="Reds", text_auto=True)
        fig_barrio.update_layout(margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_barrio, use_container_width=True)
    with col_r2:
        st.subheader("📋 Detalle de reclamos")
        st.dataframe(df_mapa_filtrado[["Nombre", "Barrio", "Tipo", "Estado"]],
                    use_container_width=True, hide_index=True)