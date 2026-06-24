import streamlit as st
import pandas as pd
import requests
import datetime
import uuid
import plotly.express as px  # <-- Nueva librería para gráficos interactivos

# Configuración de la página
st.set_page_config(
    page_title="Gestión Inteligente San Pedro",
    page_icon="🏛️",
    layout="wide"
)

# 🔒 SEGURIDAD: URLs ocultas usando Streamlit Secrets
GAS_WEBAPP_URL = st.secrets["GAS_WEBAPP_URL"]
SHEETS_CSV_URL = st.secrets["SHEETS_CSV_URL"]

# ⚡ MEJORA TÉCNICA: Caché de datos por 60 segundos
@st.cache_data(ttl=60)
def cargar_datos():
    try:
        df = pd.read_csv(SHEETS_CSV_URL)
        df = df.dropna(how='all')
        return df
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        return pd.DataFrame(columns=["ID", "Fecha", "Nombre", "Barrio", "Tipo", "Descripcion", "Estado"])

# Función para colorear estados en la tabla
def colorear_estado(val):
    if str(val).lower() == 'pendiente':
        return 'color: #ff4b4b; font-weight: bold;'
    elif str(val).lower() == 'solucionado':
        return 'color: #09ab3b; font-weight: bold;'
    return ''

# Título Principal con estilo profesional
st.title("🏛️ Sistema de Gestión Territorial y Asistencia Legislativa")
st.markdown("### *Herramienta de Inteligencia Local para Concejales - San Pedro*")
st.markdown("---")

# Carga de datos inicial
df_reclamos = cargar_datos()

# Crear las pestañas avanzadas
tab1, tab2, tab3 = st.tabs(["📊 Tablero de Control", "📝 Registro de Reclamos", "🤖 Asistente de Ordenanzas IA"])

# ==========================================
# PESTAÑA 1: TABLERO DE CONTROL (KPIs y Gráficos)
# ==========================================
with tab1:
    st.header("Análisis de Situación Territorial")
    
    if df_reclamos.empty:
        st.info("Agradecemos tu paciencia. Aún no hay reclamos registrados en la planilla para mostrar estadísticas.")
    else:
        df_reclamos.columns = [c.strip() for c in df_reclamos.columns] 
        total_reclamos = len(df_reclamos)
        
        estado_col = "Estado" if "Estado" in df_reclamos.columns else df_reclamos.columns[-1]
        pendientes = len(df_reclamos[df_reclamos[estado_col].str.lower() == "pendiente"]) if estado_col in df_reclamos.columns else 0
        solucionados = total_reclamos - pendientes
        
        # Fila de KPIs
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("🚨 Total Reclamos Activos", total_reclamos)
        kpi2.metric("⏳ Gestión Pendiente", pendientes, delta=f"{pendientes} urgentes", delta_color="inverse")
        kpi3.metric("✅ Soluciones Brindadas", solucionados)
        
        st.markdown("---")
        
        # Sección de Gráficos de Distribución con Plotly
        g1, g2 = st.columns(2)
        
        with g1:
            st.subheader("📍 Reclamos por Barrio / Localidad")
            if "Barrio" in df_reclamos.columns:
                barrio_counts = df_reclamos["Barrio"].value_counts().reset_index()
                barrio_counts.columns = ["Barrio", "Cantidad"]
                
                # Gráfico interactivo Plotly
                fig_bar = px.bar(barrio_counts, x="Barrio", y="Cantidad", 
                                 color="Cantidad", color_continuous_scale="Blues",
                                 text_auto=True) # text_auto pone el número sobre la barra
                fig_bar.update_layout(margin=dict(l=0, r=0, t=30, b=0), xaxis_title="", yaxis_title="Cant. de Reclamos")
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.caption("No se encontró la columna 'Barrio'")
                
        with g2:
            st.subheader("💡 Problemáticas más Frecuentes")
            if "Tipo" in df_reclamos.columns:
                tipo_counts = df_reclamos["Tipo"].value_counts().reset_index()
                tipo_counts.columns = ["Tipo", "Cantidad"]
                
                # Gráfico de dona interactivo Plotly
                fig_pie = px.pie(tipo_counts, names="Tipo", values="Cantidad", hole=0.4)
                fig_pie.update_layout(margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.caption("No se encontró la columna 'Tipo'")

        st.markdown("---")
        st.subheader("📋 Detalle de las Demandas Ciudadanas")
        
        # Tabla estilizada según el estado
        columnas_estado = [estado_col] if estado_col in df_reclamos.columns else []
        df_estilizado = df_reclamos.style.map(colorear_estado, subset=columnas_estado)
        st.dataframe(df_estilizado, use_container_width=True, hide_index=True)
        
        # Nuevo Botón de Descarga
        csv_export = df_reclamos.to_csv(index=False).encode('utf-8')
        col_descarga, _ = st.columns([1, 3])
        with col_descarga:
            st.download_button(
                label="📥 Exportar Reporte a CSV",
                data=csv_export,
                file_name=f"Reporte_San_Pedro_{datetime.date.today()}.csv",
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
            
        btn_guardar = st.form_submit_button("⚡ Registrar e Impactar en la Nube")
        
        if btn_guardar:
            if nombre and barrio and descripcion:
                id_unico = str(uuid.uuid4())[:8]
                datos = {
                    "id": id_unico,
                    "fecha": str(fecha),
                    "nombre": nombre,
                    "barrio": barrio,
                    "tipo": tipo,
                    "descripcion": descripcion,
                    "estado": "Pendiente"
                }
                try:
                    # Nuevo sistema de carga con st.status
                    with st.status("📡 Conectando con la base de datos...", expanded=True) as status:
                        st.write("Enviando paquete de datos...")
                        res = requests.post(GAS_WEBAPP_URL, json=datos, timeout=10)
                        
                        if res.json().get("success"):
                            status.update(label="Reclamo registrado con éxito", state="complete", expanded=False)
                            # Notificación Toast sutil
                            st.toast(f"✅ ¡Guardado! ID: {id_unico}", icon="🎉")
                            st.balloons()
                            st.cache_data.clear() # Limpia la memoria correctamente
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
    
    if df_reclamos.empty:
        st.info("Registre al menos un reclamo para poder redactar una ordenanza basada en datos reales.")
    else:
        opciones_reclamos = [f"{row['ID']} - {row['Barrio']} ({row['Tipo']})" for _, row in df_reclamos.iterrows()]
        reclamo_seleccionado = st.selectbox("Selecciona el reclamo del vecino para procesar:", opciones_reclamos)
        
        sel_id = reclamo_seleccionado.split(" - ")[0]
        datos_fila = df_reclamos[df_reclamos["ID"].astype(str) == str(sel_id)].iloc[0]
        
        tipo_proyecto = st.radio("Tipo de documento técnico a generar:", ["Proyecto de Ordenanza", "Minuta de Comunicación / Pedido de Informes"])
        
        if st.button("✨ Generar Borrador Legislativo"):
            with st.spinner("Generando estructura del proyecto normativo..."):
                
                borrador = f"""HONORABLE CONCEJO DELIBERANTE DE SAN PEDRO
                
VISTO:
El reclamo registrado bajo el expediente N° {datos_fila['ID']}, iniciado por el/la vecino/a {datos_fila['Nombre']} referente a una problemática de {datos_fila['Tipo']} en el barrio {datos_fila['Barrio']}, y;

CONSIDERANDO:
Que el vecino manifiesta lo siguiente: "{datos_fila['Descripcion']}".
Que es deber fundamental de este Cuerpo Deliberativo velar por el bienestar, la infraestructura urbana y la seguridad de todos los habitantes del partido de San Pedro.
Que las deficiencias en materia de {datos_fila['Tipo']} impactan negativamente en la calidad de vida diaria del barrio {datos_fila['Barrio']}.

POR ELLO:
EL HONORABLE CONCEJO DELIBERANTE DE SAN PEDRO
SANCIONA CON FUERZA DE {tipo_proyecto.upper()}

ARTÍCULO 1°: Encomiéndase al Departamento Ejecutivo Municipal, a través del área que corresponda, a realizar las obras de reparación, mantenimiento y/o solución definitiva en relación a "{datos_fila['Tipo']}" en la zona delimitada del barrio {datos_fila['Barrio']}.

ARTÍCULO 2°: Establécese un plazo de ejecución perentorio no mayor a quince (15) días corridos desde la promulgación de la presente para dar inicio a las tareas de relevamiento en el sector.

ARTÍCULO 3°: De forma."""
                
                st.subheader("📄 Borrador Generado")
                st.markdown("Pasa el cursor sobre el recuadro de abajo y haz clic en el botón de **Copiar** (esquina superior derecha) para llevarlo a Word:")
                
                st.code(borrador, language="text")
                st.success("📋 ¡Proyecto listo! Ya puedes copiarlo desde el bloque superior.")
