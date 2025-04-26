from dash import Dash, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import numpy as np
import requests
import json
from datetime import datetime
import os

# Inicializar la aplicación Dash con tema de Bootstrap
server = None  # Variable global para el servidor

def init_app(flask_app):
    global server
    server = flask_app
    
    app = Dash(__name__, 
            server=flask_app,
            url_base_pathname='/dash/',
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
            suppress_callback_exceptions=True)
            
    # Diseño del dashboard
    app.layout = dbc.Container([
        dcc.Interval(
            id='interval-component',
            interval=30*1000,  # en milisegundos (30 segundos)
            n_intervals=0
        ),
        
        dbc.Row([
            dbc.Col([
                html.Div([
                    dcc.Loading(
                        id="loading-data",
                        type="circle",
                        children=[html.Div(id="loading-output")]
                    ),
                    html.Div(id="error-container", className="alert alert-danger", style={"display": "none"}),
                ])
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Filtros", className="card-header"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Período:"),
                                dcc.Dropdown(
                                    id='filtro-fecha',
                                    options=[
                                        {'label': 'Hoy', 'value': 'hoy'},
                                        {'label': 'Ayer', 'value': 'ayer'},
                                        {'label': 'Última semana', 'value': 'semana'}
                                    ],
                                    value='hoy',
                                    clearable=False
                                )
                            ], width=3),
                            dbc.Col([
                                html.Label("Tipo de tarjeta:"),
                                dcc.Dropdown(
                                    id='filtro-tipo-tarjeta',
                                    options=[
                                        {'label': 'Todas', 'value': 'todas'},
                                        {'label': 'Crédito', 'value': 'credito'},
                                        {'label': 'Débito', 'value': 'debito'}
                                    ],
                                    value='todas',
                                    clearable=False
                                )
                            ], width=3),
                            dbc.Col([
                                html.Label("Provincia:"),
                                dcc.Dropdown(
                                    id='filtro-provincia',
                                    options=[{'label': 'Todas', 'value': 'todas'}],
                                    value='todas',
                                    clearable=False
                                )
                            ], width=3),
                            dbc.Col([
                                html.Label("Tipo de negocio:"),
                                dcc.Dropdown(
                                    id='filtro-tipo-negocio',
                                    options=[{'label': 'Todos', 'value': 'todos'}],
                                    value='todos',
                                    clearable=False
                                )
                            ], width=3)
                        ])
                    ])
                ], className="mb-4")
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Total Transacciones", className="card-title"),
                        html.H2(id="kpi-transacciones", className="display-4 text-primary"),
                        html.Div(id="kpi-transacciones-comp", className="text-success")
                    ])
                ], className="text-center h-100")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Monto Total", className="card-title"),
                        html.H2(id="kpi-monto", className="display-4 text-primary"),
                        html.Div(id="kpi-monto-comp", className="text-success")
                    ])
                ], className="text-center h-100")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Tasa de Aprobación", className="card-title"),
                        html.H2(id="kpi-aprobacion", className="display-4 text-primary"),
                        dbc.Progress(id="progress-aprobacion", className="mt-2")
                    ])
                ], className="text-center h-100")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Distribución por Tipo", className="card-title"),
                        dcc.Graph(id="grafico-distribucion", config={'displayModeBar': False}, 
                                 style={"height": "150px"})
                    ])
                ], className="text-center h-100")
            ], width=3)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Transacciones por Hora"),
                    dbc.CardBody([
                        dcc.Graph(id="grafico-linea-temporal", config={'displayModeBar': False})
                    ])
                ])
            ], width=8),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Estado de Terminales"),
                    dbc.CardBody([
                        dcc.Graph(id="grafico-terminales", config={'displayModeBar': False})
                    ])
                ], className="mb-4"),
                dbc.Card([
                    dbc.CardHeader("Tipos de Negocio"),
                    dbc.CardBody([
                        dcc.Graph(id="grafico-tipos-negocios", config={'displayModeBar': False})
                    ])
                ])
            ], width=4)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Distribución Geográfica"),
                    dbc.CardBody([
                        dcc.Graph(id="mapa-transacciones")
                    ])
                ])
            ], width=8),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Transacciones Recientes"),
                    dbc.CardBody([
                        html.Div(id="tabla-transacciones")
                    ], style={"maxHeight": "400px", "overflow": "auto"})
                ])
            ], width=4)
        ]),
        
        dbc.Row([
            dbc.Col([
                html.Div(id="ultima-actualizacion", className="text-muted text-right mt-3"),
            ])
        ])
    ], fluid=True)
    
    # Registrar los callbacks
    register_callbacks(app)
    
    return app

# Función para registrar los callbacks
def register_callbacks(app):
    @app.callback(
        [Output("filtro-provincia", "options"),
         Output("filtro-tipo-negocio", "options"),
         Output("loading-output", "children"),
         Output("error-container", "style"),
         Output("error-container", "children"),
         Output("kpi-transacciones", "children"),
         Output("kpi-transacciones-comp", "children"),
         Output("kpi-transacciones-comp", "className"),
         Output("kpi-monto", "children"),
         Output("kpi-monto-comp", "children"),
         Output("kpi-monto-comp", "className"),
         Output("kpi-aprobacion", "children"),
         Output("progress-aprobacion", "value"),
         Output("grafico-distribucion", "figure"),
         Output("grafico-linea-temporal", "figure"),
         Output("grafico-terminales", "figure"),
         Output("grafico-tipos-negocios", "figure"),
         Output("mapa-transacciones", "figure"),
         Output("tabla-transacciones", "children"),
         Output("ultima-actualizacion", "children")],
        [Input("interval-component", "n_intervals"),
         Input("filtro-fecha", "value"),
         Input("filtro-tipo-tarjeta", "value"),
         Input("filtro-provincia", "value"),
         Input("filtro-tipo-negocio", "value")]
    )
    def actualizar_dashboard(n_intervals, fecha, tipo_tarjeta, provincia, tipo_negocio):
        # Obtener datos de la API
        datos = obtener_datos(fecha, tipo_tarjeta, provincia, tipo_negocio)
        
        if not datos:
            # Mostrar mensaje de error y retornar datos vacíos
            return (
                [{"label": "Todas", "value": "todas"}],
                [{"label": "Todos", "value": "todos"}],
                "",
                {"display": "block"},
                "Error al cargar los datos. Reintentando...",
                "0",
                "+0.0% vs ayer",
                "text-success",
                "RD$ 0",
                "+0.0% vs ayer",
                "text-success",
                "0.0%",
                0,
                {}, {}, {}, {}, {},
                html.P("No hay datos disponibles"),
                f"Última actualización: {datetime.now().strftime('%H:%M:%S')}"
            )
        
        # Actualizar opciones de filtros
        opciones_provincia = [{"label": "Todas", "value": "todas"}]
        opciones_provincia.extend([{"label": p, "value": p} for p in datos.get("filtros", {}).get("provincias", [])])
        
        opciones_tipo_negocio = [{"label": "Todos", "value": "todos"}]
        opciones_tipo_negocio.extend([{"label": t, "value": t} for t in datos.get("filtros", {}).get("tipos_negocio", [])])
        
        # Formatear KPIs
        num_transacciones = f"{datos.get('kpis', {}).get('num_transacciones', 0):,}"
        
        monto_total = datos.get('kpis', {}).get('monto_total', 0)
        if monto_total >= 1000000000:
            monto_format = f"RD$ {monto_total/1000000000:.1f}B"
        elif monto_total >= 1000000:
            monto_format = f"RD$ {monto_total/1000000:.1f}M"
        elif monto_total >= 1000:
            monto_format = f"RD$ {monto_total/1000:.1f}K"
        else:
            monto_format = f"RD$ {monto_total:,.2f}"
        
        # Comparativas
        comp_trans = datos.get('kpis', {}).get('comparativa_transacciones', 0)
        comp_trans_texto = f"{'+' if comp_trans >= 0 else ''}{comp_trans:.1f}% vs ayer"
        comp_trans_clase = "text-success" if comp_trans >= 0 else "text-danger"
        
        comp_monto = datos.get('kpis', {}).get('comparativa_monto', 0)
        comp_monto_texto = f"{'+' if comp_monto >= 0 else ''}{comp_monto:.1f}% vs ayer"
        comp_monto_clase = "text-success" if comp_monto >= 0 else "text-danger"
        
        # Tasa de aprobación
        tasa_aprob = datos.get('kpis', {}).get('tasa_aprobacion', 0)
        
        # Gráfico de distribución (donut)
        porc_credito = datos.get('kpis', {}).get('porcentaje_credito', 50)
        porc_debito = datos.get('kpis', {}).get('porcentaje_debito', 50)
        
        fig_distribucion = go.Figure(go.Pie(
            values=[porc_credito, porc_debito],
            labels=['Crédito', 'Débito'],
            hole=0.7,
            marker=dict(colors=['#e53e3e', '#3182ce']),
            textinfo='percent',
            insidetextorientation='radial'
        ))
        fig_distribucion.update_layout(
            showlegend=True,
            legend=dict(orientation='h', y=0, x=0.5, xanchor='center'),
            margin=dict(t=0, b=0, l=10, r=10),
            height=150
        )
        
        # Gráfico de línea temporal
        datos_por_hora = datos.get('transacciones_por_hora', [])
        
        fig_linea = go.Figure()
        fig_linea.add_trace(go.Scatter(
            x=[item.get('hora') for item in datos_por_hora],
            y=[item.get('total', 0) for item in datos_por_hora],
            mode='lines',
            name='Total',
            line=dict(color='#4a5568', width=3)
        ))
        fig_linea.add_trace(go.Scatter(
            x=[item.get('hora') for item in datos_por_hora],
            y=[item.get('credito', 0) for item in datos_por_hora],
            mode='lines',
            name='Crédito',
            line=dict(color='#e53e3e', width=3)
        ))
        fig_linea.add_trace(go.Scatter(
            x=[item.get('hora') for item in datos_por_hora],
            y=[item.get('debito', 0) for item in datos_por_hora],
            mode='lines',
            name='Débito',
            line=dict(color='#3182ce', width=3, dash='dash')
        ))
        fig_linea.update_layout(
            xaxis=dict(title='Hora', gridcolor='#e2e8f0'),
            yaxis=dict(title='Número de Transacciones', gridcolor='#e2e8f0'),
            legend=dict(orientation='h', y=1.1, x=0.5, xanchor='center'),
            margin=dict(l=50, r=20, t=30, b=50),
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            height=300
        )
        
        # Gráfico de terminales
        terminales = datos.get('terminales', {})
        activos = terminales.get('activos', 0)
        inactivos = terminales.get('inactivos', 0)
        mantenimiento = terminales.get('mantenimiento', 0)
        
        fig_terminales = go.Figure()
        fig_terminales.add_trace(go.Bar(
            y=['Terminales'],
            x=[activos],
            name='Activos',
            orientation='h',
            marker=dict(color='#48bb78'),
            text=[f"{activos:,}"]
        ))
        fig_terminales.add_trace(go.Bar(
            y=['Terminales'],
            x=[inactivos],
            name='Inactivos',
            orientation='h',
            marker=dict(color='#f56565'),
            text=[f"{inactivos:,}"]
        ))
        fig_terminales.add_trace(go.Bar(
            y=['Terminales'],
            x=[mantenimiento],
            name='Mantenimiento',
            orientation='h',
            marker=dict(color='#ecc94b'),
            text=[f"{mantenimiento:,}"]
        ))
        fig_terminales.update_layout(
            barmode='stack',
            legend=dict(orientation='h', y=1.1, x=0.5, xanchor='center'),
            margin=dict(l=20, r=20, t=20, b=20),
            height=140,
            showlegend=True,
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False)
        )
        
        # Gráfico de tipos de negocios
        tipos_negocio = datos.get('tipos_negocio', [])
        tipos_negocio = sorted(tipos_negocio, key=lambda x: x.get('transacciones', 0), reverse=True)[:5]
        
        fig_tipos = go.Figure()
        fig_tipos.add_trace(go.Bar(
            x=[item.get('tipo_negocio', '') for item in tipos_negocio],
            y=[item.get('transacciones', 0) for item in tipos_negocio],
            marker=dict(color='#4299e1'),
            text=[f"{item.get('transacciones', 0):,}" for item in tipos_negocio]
        ))
        fig_tipos.update_layout(
            xaxis=dict(title='Tipo de Negocio'),
            yaxis=dict(title='Transacciones'),
            margin=dict(l=50, r=20, t=20, b=100),
            height=200,
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff'
        )
        
        # Mapa de calor
        mapa_datos = datos.get('mapa_transacciones', [])
        
        fig_mapa = go.Figure()
        
        if mapa_datos:
            fig_mapa.add_trace(go.Scattermapbox(
                lat=[float(item.get('latitud', 0)) for item in mapa_datos],
                lon=[float(item.get('longitud', 0)) for item in mapa_datos],
                mode='markers',
                marker=dict(
                    size=[min(max(item.get('transacciones', 0) / 50, 5), 30) for item in mapa_datos],
                    color=[item.get('transacciones', 0) for item in mapa_datos],
                    colorscale='Blues',
                    opacity=0.8,
                    colorbar=dict(title='Transacciones', thickness=20, xpad=10)
                ),
                text=[
                    f"{item.get('nombre_negocio', '')}<br>" +
                    f"Provincia: {item.get('provincia', '')}<br>" +
                    f"Transacciones: {item.get('transacciones', 0):,}<br>" +
                    f"Monto total: RD$ {item.get('monto_total', 0):,.2f}"
                    for item in mapa_datos
                ],
                hoverinfo='text'
            ))
            
        fig_mapa.update_layout(
            mapbox=dict(
                style='carto-positron',
                center=dict(lat=18.8, lon=-70.2),  # Centro de República Dominicana
                zoom=7
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            height=400
        )
        
        # Tabla de transacciones recientes
        transacciones_recientes = datos.get('transacciones_recientes', [])
        
        tabla_html = dbc.Table([
            html.Thead(
                html.Tr([
                    html.Th("ID"), 
                    html.Th("Hora"), 
                    html.Th("Negocio"), 
                    html.Th("Monto", className="text-right"), 
                    html.Th("Tipo"), 
                    html.Th("Estado")
                ])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(t.get('transaccion_id', '')),
                    html.Td(datetime.fromisoformat(t.get('fecha_hora', '')).strftime('%H:%M:%S') if t.get('fecha_hora') else ''),
                    html.Td(t.get('nombre_negocio', '')),
                    html.Td(f"RD$ {t.get('monto', 0):,.2f}", className="text-right"),
                    html.Td(t.get('tipo_tarjeta', '').capitalize()),
                    html.Td(
                        dbc.Badge(
                            "Aprobada" if t.get('aprobada') else "Rechazada",
                            color="success" if t.get('aprobada') else "danger"
                        )
                    )
                ]) for t in transacciones_recientes
            ])
        ], bordered=False, hover=True, responsive=True, striped=True, size="sm")
        
        # Actualización del tiempo
        tiempo_actualizacion = f"Última actualización: {datetime.now().strftime('%H:%M:%S')} (actualización automática cada 30 segundos)"
        
        return (
            opciones_provincia,
            opciones_tipo_negocio,
            "",
            {"display": "none"},
            "",
            num_transacciones,
            comp_trans_texto,
            comp_trans_clase,
            monto_format,
            comp_monto_texto,
            comp_monto_clase,
            f"{tasa_aprob:.1f}%",
            tasa_aprob,
            fig_distribucion,
            fig_linea,
            fig_terminales,
            fig_tipos,
            fig_mapa,
            tabla_html,
            tiempo_actualizacion
        )

# Función para obtener los datos de la API
def obtener_datos(fecha='hoy', tipo_tarjeta='todas', provincia='todas', tipo_negocio='todos'):
    try:
        # Para desarrollo local
        url = f"/api/dashboard/data?fecha={fecha}&tipo_tarjeta={tipo_tarjeta}&provincia={provincia}&tipo_negocio={tipo_negocio}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"Error al obtener datos: {str(e)}")
        return None

# Servidor para integraciones
server = app.server 