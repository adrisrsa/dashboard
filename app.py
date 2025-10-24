import pandas as pd
import streamlit as st
import plotly.express as px
from clean_data import df_month, df_day
import plotly.graph_objects as go
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import numpy as np


# --- Configuración de la página ---
st.set_page_config(
    page_title="Mi Dashboard",
    layout="wide",               # Hace que todo ocupe el ancho completo
    initial_sidebar_state="expanded"
)

# --- Sidebar filtros ---
st.sidebar.title("Filtros")

# Países
all_countries = sorted(df_month['Country'].unique())
select_all_countries = st.sidebar.checkbox("Seleccionar todos los países", value=True)

if select_all_countries:
    selected_country = st.sidebar.multiselect("Selecciona país(es)", all_countries, default=all_countries)
else:
    selected_country = st.sidebar.multiselect("Selecciona país(es)", all_countries)
    
# --- Plataformas ---
all_platforms = sorted(df_month['Platform'].unique())
select_all_platforms = st.sidebar.checkbox("Seleccionar todas las plataformas", value=True)

if select_all_platforms:
    selected_platform = st.sidebar.multiselect("Selecciona plataforma(s)", all_platforms, default=all_platforms)
else:
    selected_platform = st.sidebar.multiselect("Selecciona plataforma(s)", all_platforms)
    


# Pestañas principales
# -----------------------------
tab1, tab2 = st.tabs(["📊 VISTA GENERAL", "📈 VISTA DETALLADA"])



# === Pestaña VISTA GENERAL ===

with tab1:
    st.header("📊 Vista General")
    
    # Meses
    all_months = df_month['Month_Name'].unique()
    select_all_months = st.sidebar.checkbox("Seleccionar todos los meses", value=True)

    if select_all_months:
        selected_month = st.sidebar.multiselect("Selecciona mes(es)", all_months, default=all_months)
    else:
        selected_month = st.sidebar.multiselect("Selecciona mes(es)", all_months)

    # --- Filtrar datos según selección ---
    df_filtered = df_month[
        (df_month['Country'].isin(selected_country)) &
        (df_month['Month_Name'].isin(selected_month)) &
        (df_month['Platform'].isin(selected_platform))
    ]


    
    #CREAMOS LOS PIE CHARTS

    # Paleta personalizada: asignamos colores fijos por plataforma
    color_map = {
        "App Store": "#636EFA",   # azul (color por defecto de Plotly)
        "Google Play": "#00CC96"  # verde
    }

    # Pie chart para Revenue
    revenue_by_platform = df_filtered.groupby("Platform", as_index=False)["Revenue"].sum()
    fig_pie_revenue = px.pie(
        revenue_by_platform,
        names="Platform",
        values="Revenue",
        title="Distribución de Revenue por Plataforma",
        color="Platform",
        color_discrete_map=color_map
    )

    # Pie chart para Downloads
    installs_by_platform = df_filtered.groupby("Platform", as_index=False)["Downloads"].sum()
    fig_pie_installs = px.pie(
        installs_by_platform,
        names="Platform",
        values="Downloads",
        title="Distribución de Installs por Plataforma",
        color="Platform",
        color_discrete_map=color_map
    )


    col1, col2 = st.columns(2)

    with col1:
        total_revenue = df_filtered['Revenue'].sum()
        st.metric("💰 Revenue Total", f"${total_revenue:,.2f}")

        revenue_by_platform = df_filtered.groupby('Platform', as_index=False)['Revenue'].sum()
        st.plotly_chart(fig_pie_revenue, use_container_width=True)

    with col2:
        total_installs = df_filtered['Downloads'].sum()
        st.metric("📥 Installs Totales", f"{total_installs:,}")

        installs_by_platform = df_filtered.groupby('Platform', as_index=False)['Downloads'].sum()
        st.plotly_chart(fig_pie_installs, use_container_width=True)
        

    #VAMOS CON EL GRÁFICO DE BARRAS Y LÍNEA

    import plotly.graph_objects as go

    # Agrupar por mes y plataforma para el gráfico combinado
    df_monthly_summary = df_filtered.groupby('Month_Name', as_index=False).agg({
        'Revenue': 'sum',
        'Downloads': 'sum'
    })

    # Ordenar los meses cronológicamente
    months_order = ['January', 'February', 'March', 'April', 'May', 'June',
                    'July', 'August', 'September', 'October', 'November', 'December']
    df_monthly_summary['Month_Name'] = pd.Categorical(df_monthly_summary['Month_Name'], categories=months_order, ordered=True)
    df_monthly_summary = df_monthly_summary.sort_values('Month_Name')

    # Crear gráfico combinado: barras para Revenue, línea para Installs
    fig_combined = go.Figure()

    # Barras: Revenue
    fig_combined.add_trace(
        go.Bar(
            x=df_monthly_summary['Month_Name'],
            y=df_monthly_summary['Revenue'],
            name='Revenue',
            marker_color='indianred',
            yaxis='y1'
        )
    )

    # Línea: Installs
    fig_combined.add_trace(
        go.Scatter(
            x=df_monthly_summary['Month_Name'],
            y=df_monthly_summary['Downloads'],
            name='Installs',
            mode='lines+markers',
            line=dict(color='royalblue', width=3),
            yaxis='y2'
        )
    )

    # Configurar ejes y layout
    fig_combined.update_layout(
        title='Revenue y Installs Mensuales',
        xaxis=dict(title='Mes'),
        yaxis=dict(
            title='Revenue ($)',
            side='left'
        ),
        yaxis2=dict(
            title='Installs',
            overlaying='y',
            side='right'
        ),
        legend=dict(x=0.1, y=1.1, orientation='h'),
        margin=dict(l=40, r=40, t=80, b=40)
    )

    # Mostrar gráfico
    st.plotly_chart(fig_combined, use_container_width=True)

    #AÑADIMOS EL GRÁFICO DE TREEMAP

    # Sección destacada "Datos por país"
    st.markdown("""
    <div style="
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        background-color: #f9f9f9;
        margin-top: 25px;
    ">
        <h3 style="text-align:center; color:#333;">🌍 Datos por país</h3>
    </div>
    """, unsafe_allow_html=True)

    # Mostrar los dos treemaps en columnas
    if not df_filtered.empty:
        col1, col2 = st.columns(2)

        # --- Treemap Revenue ---
        with col1:
            revenue_by_country = df_filtered.groupby('Country', as_index=False)['Revenue'].sum()
            fig_treemap_revenue = px.treemap(
                revenue_by_country,
                path=['Country'],
                values='Revenue',
                title='Revenue por País',
                color='Revenue',
                color_continuous_scale='Rainbow'
            )
            st.plotly_chart(fig_treemap_revenue, use_container_width=True)

        # --- Treemap Downloads ---
        with col2:
            downloads_by_country = df_filtered.groupby('Country', as_index=False)['Downloads'].sum()
            fig_treemap_downloads = px.treemap(
                downloads_by_country,
                path=['Country'],
                values='Downloads',
                title='Installs por País',
                color='Downloads',
                color_continuous_scale='Rainbow'
            )
            st.plotly_chart(fig_treemap_downloads, use_container_width=True)
    else:
        st.warning("No hay datos para los filtros seleccionados")
    
    
#------------- FIN DE PESTAÑA VISTA GENERAL
            
# === Comienza Pestaña VISTA DETALLADA ===

with tab2:
    st.header("📈 VISTA DETALLADA")

    # --- Selector de mes único ---
    all_periods = df_month['Date'].dt.to_period('M').drop_duplicates().sort_values().astype(str).tolist()

    # Índice de diciembre por defecto
    december_index = 0
    for i, period in enumerate(all_periods):
        if period.endswith("-12"):
            december_index = i
            break

    selected_period = st.selectbox(
        "Selecciona un mes (solo uno)",
        options=all_periods,
        index=december_index
    )
    sel_period = pd.Period(selected_period, freq='M')

    # --- Filtrado mensual ---
    df_month_filtered = df_month[
        (df_month['Country'].isin(selected_country)) &
        (df_month['Platform'].isin(selected_platform)) &
        (df_month['Date'].dt.to_period('M') == sel_period)
    ]

    df_month_prev = df_month[
        (df_month['Country'].isin(selected_country)) &
        (df_month['Platform'].isin(selected_platform)) &
        (df_month['Date'].dt.to_period('M') == sel_period - 1)
    ]

    # --- Función delta ---
    def pct_delta(curr, prev):
        if prev == 0 or pd.isna(prev) or pd.isna(curr):
            return None
        return (curr - prev) / prev * 100

    # --- KPIs totales ---
    curr_revenue = df_month_filtered['Revenue'].sum()
    prev_revenue = df_month_prev['Revenue'].sum() if not df_month_prev.empty else 0
    curr_installs = df_month_filtered['Downloads'].sum()
    prev_installs = df_month_prev['Downloads'].sum() if not df_month_prev.empty else 0

    rev_delta = pct_delta(curr_revenue, prev_revenue)
    inst_delta = pct_delta(curr_installs, prev_installs)

    # --- Mostrar KPIs en dos columnas ---
    col1, col2 = st.columns(2)

    with col1:
        rev_display = f"${curr_revenue:,.2f}" if curr_revenue else "—"
        rev_delta_display = f"{rev_delta:+.2f}%" if rev_delta is not None else "—"
        st.metric("💰 Revenue Total", rev_display, delta=rev_delta_display)

        st.markdown("**Revenue por Plataforma**")
        if not df_month_filtered.empty:
            curr_by_plat = df_month_filtered.groupby('Platform')['Revenue'].sum()
            prev_by_plat = df_month_prev.groupby('Platform')['Revenue'].sum() if not df_month_prev.empty else pd.Series(dtype=float)
            for plat in curr_by_plat.index:
                c = curr_by_plat.loc[plat]
                p = prev_by_plat.loc[plat] if plat in prev_by_plat.index else 0
                d = pct_delta(c, p)
                delta_str = f"{d:+.2f}%" if d is not None else "—"
                st.write(f"**{plat}**: ${c:,.2f}  ({delta_str})")
        else:
            st.write("No hay datos para el mes/plataforma/país seleccionados.")

    with col2:
        inst_display = f"{int(curr_installs):,}" if curr_installs else "—"
        inst_delta_display = f"{inst_delta:+.2f}%" if inst_delta is not None else "—"
        st.metric("📥 Installs Totales", inst_display, delta=inst_delta_display)

        st.markdown("**Installs por Plataforma**")
        if not df_month_filtered.empty:
            curr_by_plat_d = df_month_filtered.groupby('Platform')['Downloads'].sum()
            prev_by_plat_d = df_month_prev.groupby('Platform')['Downloads'].sum() if not df_month_prev.empty else pd.Series(dtype=float)
            for plat in curr_by_plat_d.index:
                c = curr_by_plat_d.loc[plat]
                p = prev_by_plat_d.loc[plat] if plat in prev_by_plat_d.index else 0
                d = pct_delta(c, p)
                delta_str = f"{d:+.2f}%" if d is not None else "—"
                st.write(f"**{plat}**: {int(c):,}  ({delta_str})")
        else:
            st.write("No hay datos para el mes/plataforma/país seleccionados.")



    #AÑADIMOS GRÁFICO DIARIO
    # Filtrar df_day para el mes seleccionado
    df_day_filtered = df_day[
        (df_day['Country'].isin(selected_country)) &
        (df_day['Platform'].isin(selected_platform)) &
        (df_day['Date'].dt.to_period('M') == sel_period)
    ]

    if not df_day_filtered.empty:
        # Agregamos por día
        daily_summary = df_day_filtered.groupby('Date', as_index=False).agg({
            'Revenue': 'sum',
            'Downloads': 'sum'
        })

        fig = go.Figure()
        # Revenue en barras
        fig.add_trace(go.Bar(
            x=daily_summary['Date'],
            y=daily_summary['Revenue'],
            name='Revenue',
            marker_color='green'
        ))
        # Installs en línea
        fig.add_trace(go.Scatter(
            x=daily_summary['Date'],
            y=daily_summary['Downloads'],
            mode='lines+markers',
            name='Installs',
            yaxis='y2',
            line=dict(color='blue')
        ))

        # Configurar eje secundario
        fig.update_layout(
            title=dict(text="Revenue e Installs diarios", font=dict(size=25)),
            yaxis=dict(title='Revenue ($)'),
            yaxis2=dict(title='Installs', overlaying='y', side='right'),
            legend=dict(x=0.1, y=1.1, orientation='h')
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No hay datos diarios para el mes/plataforma/país seleccionados.")


#GRID POR PAISES

    # --- Preparar dataframe por país ---
    df_country_summary = df_month_filtered.groupby('Country', as_index=False).agg({
        'Revenue': 'sum',
        'Downloads': 'sum'
    })

    df_country_prev = df_month_prev.groupby('Country', as_index=False).agg({
        'Revenue': 'sum',
        'Downloads': 'sum'
    })

    # Función delta %
    def pct_delta(curr, prev):
        if prev == 0:
            return None
        return (curr - prev) / prev * 100

    df_country_summary['Revenue Δ%'] = df_country_summary.apply(
        lambda row: pct_delta(
            row['Revenue'], 
            df_country_prev.loc[df_country_prev['Country']==row['Country'], 'Revenue'].sum()
            if row['Country'] in df_country_prev['Country'].values else 0
        ), axis=1
    )

    df_country_summary['Installs Δ%'] = df_country_summary.apply(
        lambda row: pct_delta(
            row['Downloads'], 
            df_country_prev.loc[df_country_prev['Country']==row['Country'], 'Downloads'].sum()
            if row['Country'] in df_country_prev['Country'].values else 0
        ), axis=1
    )

    # Renombrar columnas
    df_country_summary.rename(columns={
        'Revenue': 'Revenue ($)',
        'Downloads': 'Installs'
    }, inplace=True)

    # Orden inicial por Revenue descendente
    df_country_summary.sort_values(by='Revenue ($)', ascending=False, inplace=True)

    # --- Configurar AgGrid ---
    gb = GridOptionsBuilder.from_dataframe(df_country_summary)

    # Hacer todas las columnas ordenables
    gb.configure_default_column(sortable=True, filter=True, resizable=True)

    # Ajustes de formato
    gb.configure_column("Revenue ($)", type=["numericColumn","numberColumnFilter"], valueFormatter="`${value.toLocaleString()}`")
    gb.configure_column("Revenue Δ%", type=["numericColumn","numberColumnFilter"], valueFormatter="`${value.toFixed(2)}%`")
    gb.configure_column("Installs", type=["numericColumn","numberColumnFilter"], valueFormatter="`${value.toLocaleString()}`")
    gb.configure_column("Installs Δ%", type=["numericColumn","numberColumnFilter"], valueFormatter="`${value.toFixed(2)}%`")

    grid_options = gb.build()

    # --- Mostrar AgGrid ---
    st.subheader("Variacion por país")
    AgGrid(
        df_country_summary,
        gridOptions=grid_options,
        height=400,
        fit_columns_on_grid_load=True
    )
    
    #GRID DIARIO


    # Filtrar df_day para el mes seleccionado
    df_day_filtered = df_day[
        (df_day['Country'].isin(selected_country)) &
        (df_day['Date'].dt.to_period('M') == sel_period)
    ]

    if not df_day_filtered.empty:
        # Agrupar por día y plataforma
        df_grouped = df_day_filtered.groupby(['Date','Platform']).agg(
            Revenue=('Revenue','sum'),
            Downloads=('Downloads','sum')
        ).reset_index()

        # Pivotar para columnas por plataforma
        df_pivot = df_grouped.pivot(index='Date', columns='Platform', values=['Revenue','Downloads'])
        df_pivot.columns = [f"{plat} {metric}" for metric, plat in df_pivot.columns]
        df_pivot = df_pivot.reset_index()

        # Calcular totales
        df_pivot['Totales Revenue'] = df_pivot[['App Store Revenue','Google Play Revenue']].sum(axis=1)
        df_pivot['Totales Downloads'] = df_pivot[['App Store Downloads','Google Play Downloads']].sum(axis=1)

        # --- Configuración AgGrid ---
        gb = GridOptionsBuilder.from_dataframe(df_pivot)

        # Formatter para revenue con 2 decimales y miles
        revenue_formatter = JsCode("""
            function(params) {
                if (params.value == null) return '';
                return params.value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
            }
        """)

        # Formatter para installs como entero
        installs_formatter = JsCode("""
            function(params) {
                if (params.value == null) return '';
                return Math.round(params.value).toLocaleString();
            }
        """)

        # App Store
        gb.configure_column("App Store Revenue", header_name="App Store\nRevenue($)", type=["numericColumn"], valueFormatter=revenue_formatter)
        gb.configure_column("App Store Downloads", header_name="App Store\nInstalls", type=["numericColumn"], valueFormatter=installs_formatter)

        # Google Play
        gb.configure_column("Google Play Revenue", header_name="Google Play\nRevenue($)", type=["numericColumn"], valueFormatter=revenue_formatter)
        gb.configure_column("Google Play Downloads", header_name="Google Play\nInstalls", type=["numericColumn"], valueFormatter=installs_formatter)

        # Totales
        gb.configure_column("Totales Revenue", header_name="Totales\nRevenue($)", type=["numericColumn"], valueFormatter=revenue_formatter)
        gb.configure_column("Totales Downloads", header_name="Totales\nInstalls", type=["numericColumn"], valueFormatter=installs_formatter)

        # Opciones por defecto
        gb.configure_default_column(sortable=True, filter=True, resizable=True)
        gridOptions = gb.build()

        st.subheader("📅 Detalle Diario por Plataforma")
        AgGrid(df_pivot, gridOptions=gridOptions, fit_columns_on_grid_load=True, allow_unsafe_jscode=True)

    else:
        st.warning("No hay datos para los filtros seleccionados")
