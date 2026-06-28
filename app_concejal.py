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

# 🔒 SEGURIDAD: URLs ocultas usando Streamlit Secrets
GAS_WEBAPP_URL = st.secrets.get("GAS_WEBAPP_URL", "")
SHEETS_CSV_URL = st.secrets.get("SHEETS_CSV_URL", "")
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
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center'>🏛️ ConcejalIA</h1>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align:center;color:gray'>Gestión Legislativa Inteligente — {DISTRITO}</h4>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        with st.form("login_form"):
            usuario = st.text_input("Usuario:", placeholder="concejal")
            clave = st.text_input("Contraseña:", type="password", placeholder="••••••••")
            st.caption("ℹ️ Demo: usuario `concejal` / contraseña `sanpedro2026`")
            if st.form_submit_button("Ingresar al Sistema", type="primary"):
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

def colorear_estado(val):
    val_lower = str(val).lower()
    if val_lower == 'pendiente':
        return 'color: #ff4b4b; font-weight: bold;'
    elif val_lower == 'solucionado':
        return 'color: #09ab3b; font-weight: bold;'
    elif val_lower == 'en gestión':
        return 'color: #f59e0b; font-weight: bold;'
    return ''

# ==========================================
# HEADER Y LOGOUT
# ==========================================
col_titulo, col_logout = st.columns([5, 1])
with col_titulo:
    st.title(f"🏛️ Sistema de Gestión Territorial y Asistencia Legislativa")
    st.markdown(f"### *Herramienta de Inteligencia Local para Concejales — {DISTRITO}*")
with col_logout:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Cerrar sesión"):
        st.session_state.autenticado = False
        st.rerun()

st.markdown("---")

# Carga de datos
df_reclamos, es_demo = cargar_datos()

if es_demo:
    st.info("📋 **Modo Demo activo** — Mostrando datos de ejemplo. Conectá tu Google Sheets para ver datos reales.")

# ==========================================
# PESTAÑAS
# ==========================================
tab1, tab2, tab3 = st.tabs(["📊 Tablero de Control", "📝 Registro de Reclamos", "🤖 Asistente de Ordenanzas IA"])

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

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("🚨 Total Reclamos", total_reclamos)
    kpi2.metric("⏳ Pendientes", pendientes, delta=f"{pendientes} urgentes", delta_color="inverse")
    kpi3.metric("🔄 En Gestión", en_gestion)
    kpi4.metric("✅ Solucionados", solucionados)

    st.markdown("---")

    g1, g2 = st.columns(2)

    with g1:
        st.subheader("📍 Reclamos por Barrio / Localidad")
        if "Barrio" in df_reclamos.columns:
            barrio_counts = df_reclamos["Barrio"].value_counts().reset_index()
            barrio_counts.columns = ["Barrio", "Cantidad"]
            fig_bar = px.bar(barrio_counts, x="Barrio", y="Cantidad",
                             color="Cantidad", color_continuous_scale="Blues", text_auto=True)
            fig_bar.update_layout(margin=dict(l=0, r=0, t=30, b=0), xaxis_title="", yaxis_title="Cant. de Reclamos")
            st.plotly_chart(fig_bar, use_container_width=True)

    with g2:
        st.subheader("💡 Problemáticas más Frecuentes")
        if "Tipo" in df_reclamos.columns:
            tipo_counts = df_reclamos["Tipo"].value_counts().reset_index()
            tipo_counts.columns = ["Tipo", "Cantidad"]
            fig_pie = px.pie(tipo_counts, names="Tipo", values="Cantidad", hole=0.4)
            fig_pie.update_layout(margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_pie, use_container_width=True)

    # Gráfico de evolución temporal
    if "Fecha" in df_reclamos.columns:
        st.subheader("📈 Evolución de Reclamos en el Tiempo")
        try:
            df_reclamos["Fecha"] = pd.to_datetime(df_reclamos["Fecha"])
            evolucion = df_reclamos.groupby("Fecha").size().reset_index(name="Cantidad")
            fig_line = px.line(evolucion, x="Fecha", y="Cantidad", markers=True)
            fig_line.update_layout(margin=dict(l=0, r=0, t=30, b=0))
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

    opciones_reclamos = [f"{row['ID']} - {row['Barrio']} ({row['Tipo']})" for _, row in df_reclamos.iterrows()]
    reclamo_seleccionado = st.selectbox("Selecciona el reclamo del vecino para procesar:", opciones_reclamos)

    sel_id = reclamo_seleccionado.split(" - ")[0]
    datos_fila = df_reclamos[df_reclamos["ID"].astype(str) == str(sel_id)].iloc[0]

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
