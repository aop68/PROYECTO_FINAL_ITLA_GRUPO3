/**
 * Dashboard de Análisis de Pagos en Tiempo Real para Cardnet RD
 * Este script maneja la inicialización, actualización y funcionalidad interactiva
 * del dashboard de transacciones de pagos.
 */

// Variables globales
let dashboardData = null;
const updateInterval = 60000; // 1 minuto (actualizado de 30 segundos)
let updateTimer = null;
let mapFigure = null;
let isUpdating = false;

// Filtros iniciales
const filtros = {
    fecha: 'hoy',
    tipo_tarjeta: 'todas',
    provincia: 'todas',
    tipo_negocio: 'todos'
};

/**
 * Inicializa el dashboard cuando la página se carga
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando dashboard...');
    
    // Inicializar filtros y eventos
    inicializarFiltros();
    
    // Inicializar componentes del dashboard
    inicializarDashboard();
});

/**
 * Inicializa los filtros y sus eventos
 */
function inicializarFiltros() {
    console.log('Inicializando filtros...');
    
    // Agregar eventos para los selectores de filtros
    document.getElementById('filtro-fecha').addEventListener('change', function() {
        filtros.fecha = this.value;
        actualizarDashboardCompleto();
    });
    
    document.getElementById('filtro-tipo-tarjeta').addEventListener('change', function() {
        filtros.tipo_tarjeta = this.value;
        actualizarDashboardCompleto();
    });
    
    document.getElementById('filtro-provincia').addEventListener('change', function() {
        filtros.provincia = this.value;
        actualizarDashboardCompleto();
    });
    
    document.getElementById('filtro-tipo-negocio').addEventListener('change', function() {
        filtros.tipo_negocio = this.value;
        actualizarDashboardCompleto();
    });
}

/**
 * Inicializa el dashboard con los componentes iniciales
 */
function inicializarDashboard() {
    console.log('Inicializando dashboard en tiempo real...');
    
    // Inicializar filtros
    inicializarFiltros();
    
    // Cargar datos iniciales una sola vez para establecer los gráficos
    fetch('/api/dashboard/data')
        .then(response => response.json())
        .then(data => {
            // Guardar datos en variable global
            dashboardData = data;
            
            // Crear componentes iniciales (solo una vez)
            crearKPIs(data);
            crearGraficoTransaccionesPorHora(data);
            crearGraficoEstadoTerminales(data);
            crearGraficoTiposNegocios(data);
            crearMapaTransacciones(data);
            crearTablaTransaccionesRecientes(data);
            
            // Actualizar última actualización
            document.getElementById('last-update-time').textContent = new Date().toLocaleTimeString();
            
            // Ocultar indicador de carga
            document.getElementById('loading-indicator').style.display = 'none';
            document.getElementById('dashboard-content').style.display = 'block';
            
            // Ahora programar la actualización automática solo para KPIs y tablas
            cargarDatos(true);
        })
        .catch(error => {
            console.error('Error al inicializar dashboard:', error);
            mostrarError('Error al cargar datos iniciales. Por favor, intente nuevamente.');
            document.getElementById('loading-indicator').style.display = 'none';
        });
}

/**
 * Programa la próxima actualización automática
 * NOTA: Esta función ha sido deshabilitada para evitar problemas de bucle
 */
function programarActualizacion() {
    console.log('La función de actualización automática ha sido deshabilitada');
    // Código original comentado
    /*
    // Cancelar cualquier temporizador existente
    if (updateTimer) {
        clearTimeout(updateTimer);
    }
    
    // Programar próxima actualización
    updateTimer = setTimeout(() => {
        console.log('Ejecutando actualización programada');
        cargarDatos(true);
    }, updateInterval);
    
    console.log(`Próxima actualización programada en ${updateInterval/1000} segundos`);
    */
}

/**
 * Carga los datos desde el servidor con los filtros actuales
 * NOTA: Esta función ha sido deshabilitada para evitar problemas de bucle
 * @param {boolean} autoUpdate - Indica si debe programar la próxima actualización automática
 */
function cargarDatos(autoUpdate = false) {
    console.log('La función de carga automática ha sido deshabilitada');
    return Promise.resolve(null);
    
    // Código original comentado
    /*
    // Evitar múltiples solicitudes simultáneas
    if (isUpdating) {
        debug('Ya hay una actualización en curso, saltando esta solicitud');
        return Promise.resolve(); // Devuelve una promesa resuelta para mantener la cadena
    }
    
    isUpdating = true;
    mostrarIndicadorCarga(true);
    
    // Actualizar hora de última actualización
    document.getElementById('ultima-actualizacion').textContent = new Date().toLocaleTimeString();
    
    // Obtener valores de filtros
    const fechaInicio = document.getElementById('filtro-fecha-inicio').value;
    const fechaFin = document.getElementById('filtro-fecha-fin').value;
    const tipoTarjeta = document.getElementById('filtro-tipo-tarjeta').value;
    const provincia = document.getElementById('filtro-provincia').value;
    const tipoNegocio = document.getElementById('filtro-tipo-negocio').value;
    
    // Construir parámetros para la solicitud
    const params = new URLSearchParams({
        fecha_inicio: fechaInicio,
        fecha_fin: fechaFin,
        tipo_tarjeta: tipoTarjeta,
        provincia: provincia,
        tipo_negocio: tipoNegocio
    });
    
    debug(`Cargando datos con parámetros: ${params.toString()}`);
    
    return fetch(`/api/dashboard/data?${params.toString()}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error en la respuesta: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            debug('Datos recibidos del servidor', {
                kpis: data.kpis ? 'Recibidos' : 'Faltantes',
                transacciones_por_hora: data.transacciones_por_hora ? `${data.transacciones_por_hora.length} registros` : 'Faltantes',
                terminales: data.terminales ? 'Recibidos' : 'Faltantes',
                tipos_negocio: data.tipos_negocio ? `${data.tipos_negocio.length} registros` : 'Faltantes',
                mapa_transacciones: data.mapa_transacciones ? `${data.mapa_transacciones.length} registros` : 'Faltantes',
                transacciones_recientes: data.transacciones_recientes ? `${data.transacciones_recientes.length} registros` : 'Faltantes'
            });
            
            dashboardData = data;
            
            // Actualizar elementos del dashboard
            try {
                debug('Actualizando filtros');
                actualizarFiltros(data);
                
                debug('Creando KPIs');
                crearKPIs(data);
                
                // Las siguientes líneas se comentan para evitar bucles de actualización
                // debug('Creando gráfico de transacciones');
                // crearGraficoTransacciones(data);
                
                // debug('Creando gráfico de terminales');
                // crearGraficoTerminales(data);
                
                // debug('Creando gráfico de tipos de negocio');
                // crearGraficoTiposNegocio(data);
                
                // debug('Creando mapa de transacciones');
                // crearMapaTransacciones(data);
                
                debug('Actualizando tabla de transacciones');
                actualizarTablaTransacciones(data);
                
                // Ocultar indicador de carga
                mostrarIndicadorCarga(false);
                
                // Ocultar mensajes de error si existen
                document.getElementById('error-container').style.display = 'none';
                
                debug('Dashboard actualizado correctamente');
            } catch (e) {
                console.error('Error al actualizar componentes del dashboard:', e);
                const errorContainer = document.getElementById('error-container');
                errorContainer.textContent = `Error al actualizar dashboard: ${e.message}`;
                errorContainer.style.display = 'block';
            }
            
            return data;
        })
        .catch(error => {
            console.error('Error al cargar datos:', error);
            
            // Mostrar mensaje de error
            const errorContainer = document.getElementById('error-container');
            errorContainer.textContent = `Error al cargar datos: ${error.message}`;
            errorContainer.style.display = 'block';
            
            return null;
        })
        .finally(() => {
            // Siempre ocultar el indicador de carga y marcar como no actualizando
            mostrarIndicadorCarga(false);
            isUpdating = false;
            
            // Programar próxima actualización solo si se solicita
            if (autoUpdate) {
                programarActualizacion();
            }
        });
    */
}

/**
 * Crea las tarjetas de KPIs con los datos proporcionados
 */
function crearKPIs(data) {
    if (!data || !data.kpis) {
        debug('No hay datos de KPIs disponibles');
        return;
    }
    
    debug('Creando tarjetas KPI');
    
    const kpiContainer = document.querySelector('.kpi-container');
    kpiContainer.innerHTML = ''; // Limpiar contenedor
    
    try {
        // Datos de KPIs normalizados (con valores por defecto en caso de valores nulos)
        const kpisData = {
            num_transacciones: data.kpis.num_transacciones || 0,
            monto_total: data.kpis.monto_total || 0,
            tasa_aprobacion: data.kpis.tasa_aprobacion || 0,
            porcentaje_credito: data.kpis.porcentaje_credito || 0,
            porcentaje_debito: data.kpis.porcentaje_debito || 0,
            porcentaje_prepago: data.kpis.porcentaje_prepago || 0,
            comparativa_transacciones: data.kpis.comparativa_transacciones || 0,
            comparativa_monto: data.kpis.comparativa_monto || 0
        };
        
        // KPI: Total de Transacciones
        const kpiTransacciones = document.createElement('div');
        kpiTransacciones.className = 'kpi-card';
        kpiTransacciones.innerHTML = `
            <h3>Total Transacciones</h3>
            <div class="kpi-value">${kpisData.num_transacciones.toLocaleString()}</div>
            <div class="kpi-comparison ${kpisData.comparativa_transacciones >= 0 ? 'positive' : 'negative'}">
                ${kpisData.comparativa_transacciones >= 0 ? '+' : ''}${kpisData.comparativa_transacciones.toFixed(1)}% vs período anterior
            </div>
        `;
        kpiContainer.appendChild(kpiTransacciones);
        
        // KPI: Monto Total
        const kpiMonto = document.createElement('div');
        kpiMonto.className = 'kpi-card';
        
        // Formatear monto para mejor visualización
        let montoFormateado;
        if (kpisData.monto_total >= 1000000000) {
            montoFormateado = `RD$ ${(kpisData.monto_total / 1000000000).toFixed(1)}B`;
        } else if (kpisData.monto_total >= 1000000) {
            montoFormateado = `RD$ ${(kpisData.monto_total / 1000000).toFixed(1)}M`;
        } else if (kpisData.monto_total >= 1000) {
            montoFormateado = `RD$ ${(kpisData.monto_total / 1000).toFixed(1)}K`;
        } else {
            montoFormateado = `RD$ ${kpisData.monto_total.toFixed(2)}`;
        }
        
        kpiMonto.innerHTML = `
            <h3>Monto Total</h3>
            <div class="kpi-value">${montoFormateado}</div>
            <div class="kpi-comparison ${kpisData.comparativa_monto >= 0 ? 'positive' : 'negative'}">
                ${kpisData.comparativa_monto >= 0 ? '+' : ''}${kpisData.comparativa_monto.toFixed(1)}% vs período anterior
            </div>
        `;
        kpiContainer.appendChild(kpiMonto);
        
        // KPI: Tasa de Aprobación
        const kpiAprobacion = document.createElement('div');
        kpiAprobacion.className = 'kpi-card';
        kpiAprobacion.innerHTML = `
            <h3>Tasa de Aprobación</h3>
            <div class="kpi-value">${kpisData.tasa_aprobacion.toFixed(1)}%</div>
            <div class="progress-bar">
                <div class="progress" style="width: ${kpisData.tasa_aprobacion}%"></div>
            </div>
        `;
        kpiContainer.appendChild(kpiAprobacion);
        
        // KPI: Distribución por Tipo
        const kpiDistribucion = document.createElement('div');
        kpiDistribucion.className = 'kpi-card';
        kpiDistribucion.innerHTML = `
            <h3>Distribución por Tipo</h3>
            <div id="donut-chart-container" style="height: 150px;"></div>
        `;
        kpiContainer.appendChild(kpiDistribucion);
        
        debug('Tarjetas KPI creadas, generando gráfico de distribución');
        
        // Crear gráfico de distribución por tipo
        const valores = [
            kpisData.porcentaje_credito, 
            kpisData.porcentaje_debito, 
            kpisData.porcentaje_prepago
        ];
        
        const etiquetas = ['Crédito', 'Débito', 'Prepago'];
        
        const data = [{
            values: valores,
            labels: etiquetas,
            type: 'pie',
            hole: 0.4,
            marker: {
                colors: ['#e74c3c', '#3498db', '#f39c12']
            },
            textinfo: 'percent',
            textposition: 'inside',
            showlegend: true
        }];
        
        const layout = {
            margin: {l: 0, r: 0, b: 0, t: 0},
            showlegend: true,
            legend: {
                orientation: 'h',
                x: 0.5,
                y: -0.1,
                xanchor: 'center'
            },
            height: 150
        };
        
        Plotly.newPlot('donut-chart-container', data, layout, {responsive: true, displayModeBar: false});
        
        debug('KPIs creados correctamente');
        
    } catch (error) {
        console.error('Error al crear KPIs:', error);
        kpiContainer.innerHTML = '<div class="error-message">Error al cargar los KPIs</div>';
    }
}

/**
 * Actualiza los KPIs con los datos más recientes
 */
function actualizarKPIs() {
    if (!dashboardData.kpis) {
        console.warn('No hay datos de KPIs para actualizar');
        return;
    }
    
    console.log('Actualizando KPIs...');
    
    // Usar la misma función de crear KPIs para actualizarlos
    crearKPIs(dashboardData);
}

/**
 * Crea el gráfico donut para distribución de tarjetas
 */
function crearGraficoDistribucion() {
    if (!dashboardData.kpis) return;
    
    const chartDiv = document.getElementById('grafico-distribucion');
    if (!chartDiv) return;
    
    const data = [{
        values: [dashboardData.kpis.porcentaje_credito, dashboardData.kpis.porcentaje_debito],
        labels: ['Crédito', 'Débito'],
        type: 'pie',
        hole: 0.6,
        marker: {
            colors: ['#e53e3e', '#3182ce']
        },
        textinfo: 'percent',
        insidetextorientation: 'radial'
    }];
    
    const layout = {
        showlegend: true,
        legend: {
            orientation: 'h',
            y: 0,
            x: 0.5,
            xanchor: 'center'
        },
        margin: {t: 0, b: 0, l: 0, r: 0},
        height: 160,
        width: chartDiv.offsetWidth
    };
    
    Plotly.newPlot('grafico-distribucion', data, layout, {displayModeBar: false, responsive: true});
}

/**
 * Crea el gráfico de línea temporal para transacciones por hora
 */
function crearGraficoLineaTemporal() {
    if (!dashboardData.transacciones_por_hora) {
        console.warn('No hay datos de transacciones por hora');
        return;
    }
    
    console.log('Creando gráfico de línea temporal...');
    
    const chartDiv = document.getElementById('grafico-linea-temporal');
    if (!chartDiv) {
        console.error('No se encontró el contenedor del gráfico de línea temporal');
        return;
    }
    
    // Preparar datos para el gráfico
    const horas = dashboardData.transacciones_por_hora.map(item => item.hora);
    const transaccionesTotal = dashboardData.transacciones_por_hora.map(item => item.total || (item.credito + item.debito));
    const transaccionesCredito = dashboardData.transacciones_por_hora.map(item => item.credito);
    const transaccionesDebito = dashboardData.transacciones_por_hora.map(item => item.debito);
    
    const data = [
        {
            x: horas,
            y: transaccionesTotal,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Total',
            line: {
                color: '#4a5568',
                width: 3
            },
            marker: {
                size: 6,
                color: '#4a5568'
            }
        },
        {
            x: horas,
            y: transaccionesCredito,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Crédito',
            line: {
                color: '#e53e3e',
                width: 2.5
            },
            marker: {
                size: 5,
                color: '#e53e3e'
            }
        },
        {
            x: horas,
            y: transaccionesDebito,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Débito',
            line: {
                color: '#3182ce',
                width: 2.5,
                dash: 'dash'
            },
            marker: {
                size: 5,
                color: '#3182ce'
            }
        }
    ];
    
    const layout = {
        xaxis: {
            title: 'Hora',
            tickformat: '%H:%M',
            gridcolor: '#e2e8f0'
        },
        yaxis: {
            title: 'Número de Transacciones',
            gridcolor: '#e2e8f0'
        },
        hovermode: 'closest',
        legend: {
            orientation: 'h',
            y: 1.1,
            x: 0.5,
            xanchor: 'center'
        },
        margin: {
            l: 50,
            r: 20,
            t: 10,
            b: 50
        },
        plot_bgcolor: '#ffffff',
        paper_bgcolor: '#ffffff',
        autosize: true,
        height: 300
    };
    
    const config = {
        responsive: true,
        displayModeBar: false
    };
    
    Plotly.newPlot('grafico-linea-temporal', data, layout, config);
    
    // Auto-ajustar en caso de cambio de tamaño de ventana
    window.addEventListener('resize', function() {
        Plotly.relayout('grafico-linea-temporal', {
            width: chartDiv.offsetWidth
        });
    });
}

/**
 * Actualiza el gráfico de línea temporal con los datos más recientes
 */
function actualizarGraficoLineaTemporal() {
    if (!dashboardData.transacciones_por_hora) return;
    
    const chartDiv = document.getElementById('grafico-linea-temporal');
    if (!chartDiv) return;
    
    // Verificar si el gráfico existe
    if (chartDiv.data) {
        // Actualizar datos
        const horas = dashboardData.transacciones_por_hora.map(item => item.hora);
        const transaccionesTotal = dashboardData.transacciones_por_hora.map(item => item.total || (item.credito + item.debito));
        const transaccionesCredito = dashboardData.transacciones_por_hora.map(item => item.credito);
        const transaccionesDebito = dashboardData.transacciones_por_hora.map(item => item.debito);
        
        const update = {
            x: [horas, horas, horas],
            y: [transaccionesTotal, transaccionesCredito, transaccionesDebito]
        };
        
        Plotly.update('grafico-linea-temporal', update);
    } else {
        // Si no existe, crearlo
        crearGraficoLineaTemporal();
    }
}

/**
 * Crea el gráfico de barras horizontales para el estado de terminales
 * Ahora usando barras HTML personalizadas
 */
function crearGraficoTerminales() {
    if (!dashboardData.terminales) return;
    
    actualizarGraficoTerminales();
}

/**
 * Actualiza el gráfico de barras horizontales para el estado de terminales
 * Ahora usando barras HTML personalizadas
 */
function actualizarGraficoTerminales() {
    if (!dashboardData.terminales) return;
    
    // Calcular el total para los porcentajes
    const total = dashboardData.terminales.activos + dashboardData.terminales.inactivos + dashboardData.terminales.mantenimiento;
    
    // Calcular porcentajes para el ancho de las barras
    const porcentajeActivos = total > 0 ? (dashboardData.terminales.activos / total) * 100 : 0;
    const porcentajeInactivos = total > 0 ? (dashboardData.terminales.inactivos / total) * 100 : 0;
    const porcentajeMantenimiento = total > 0 ? (dashboardData.terminales.mantenimiento / total) * 100 : 0;
    
    // Actualizar las barras con los nuevos datos
    const barsContainer = document.getElementById('terminal-bars');
    
    // Verificar si existen las barras, si no, crearlas
    if (barsContainer.children.length === 0) {
        barsContainer.innerHTML = `
            <div class="terminal-bar">
                <div class="terminal-label">Activos:</div>
                <div class="terminal-bar-container">
                    <div class="terminal-bar-fill activos" style="width: ${porcentajeActivos}%">
                        <span class="terminal-value">${dashboardData.terminales.activos.toLocaleString()}</span>
                    </div>
                </div>
            </div>
            <div class="terminal-bar">
                <div class="terminal-label">Inactivos:</div>
                <div class="terminal-bar-container">
                    <div class="terminal-bar-fill inactivos" style="width: ${porcentajeInactivos}%">
                        <span class="terminal-value">${dashboardData.terminales.inactivos.toLocaleString()}</span>
                    </div>
                </div>
            </div>
            <div class="terminal-bar">
                <div class="terminal-label">Mantenimiento:</div>
                <div class="terminal-bar-container">
                    <div class="terminal-bar-fill mantenimiento" style="width: ${porcentajeMantenimiento}%">
                        <span class="terminal-value">${dashboardData.terminales.mantenimiento.toLocaleString()}</span>
                    </div>
                </div>
            </div>
        `;
    } else {
        // Actualizar barras existentes
        const barActivos = barsContainer.querySelector('.terminal-bar-fill.activos');
        const barInactivos = barsContainer.querySelector('.terminal-bar-fill.inactivos');
        const barMantenimiento = barsContainer.querySelector('.terminal-bar-fill.mantenimiento');
        
        // Actualizar ancho de barras
        barActivos.style.width = `${porcentajeActivos}%`;
        barInactivos.style.width = `${porcentajeInactivos}%`;
        barMantenimiento.style.width = `${porcentajeMantenimiento}%`;
        
        // Actualizar valores
        barActivos.querySelector('.terminal-value').textContent = dashboardData.terminales.activos.toLocaleString();
        barInactivos.querySelector('.terminal-value').textContent = dashboardData.terminales.inactivos.toLocaleString();
        barMantenimiento.querySelector('.terminal-value').textContent = dashboardData.terminales.mantenimiento.toLocaleString();
    }
}

/**
 * Crea el gráfico de barras para los tipos de negocios
 * Ahora usando barras HTML personalizadas
 */
function crearGraficoTiposNegocios() {
    if (!dashboardData.tipos_negocio || !dashboardData.tipos_negocio.length) return;
    
    actualizarGraficoTiposNegocios();
}

/**
 * Actualiza el gráfico de barras para los tipos de negocios
 * Ahora usando barras HTML personalizadas
 */
function actualizarGraficoTiposNegocios() {
    if (!dashboardData.tipos_negocio || !dashboardData.tipos_negocio.length) return;
    
    // Ordenar por volumen de transacciones (de mayor a menor)
    const tiposNegocio = [...dashboardData.tipos_negocio]
        .sort((a, b) => b.transacciones - a.transacciones)
        .slice(0, 5);
    
    // Calcular el máximo para escalar las barras adecuadamente
    const maxTransacciones = tiposNegocio.length > 0 ? tiposNegocio[0].transacciones : 0;
    
    // Contenedor de barras
    const barsContainer = document.getElementById('business-bars');
    barsContainer.innerHTML = ''; // Limpiar contenido anterior
    
    // Crear barras para cada tipo de negocio
    tiposNegocio.forEach(item => {
        const porcentajeBarra = maxTransacciones > 0 ? (item.transacciones / maxTransacciones) * 100 : 0;
        const porcentajeLabel = (item.porcentaje * 100).toFixed(0);
        
        const barHTML = `
            <div class="business-bar">
                <div class="business-label">${item.tipo_negocio} (${porcentajeLabel}%)</div>
                <div class="business-bar-container">
                    <div class="business-bar-fill" style="width: ${porcentajeBarra}%"></div>
                </div>
                <div class="business-value">${item.transacciones.toLocaleString()}</div>
            </div>
        `;
        
        barsContainer.innerHTML += barHTML;
    });
}

/**
 * Crea el mapa de transacciones por ubicación
 * @param {Object} data - Datos para el mapa
 */
function crearMapaTransacciones(data) {
    const container = document.getElementById('mapa-transacciones');
    
    // Verificar si hay datos disponibles
    if (!data || !data.mapa || data.mapa.length === 0) {
        container.innerHTML = '<div class="no-data-message">No hay datos de ubicación disponibles</div>';
        return;
    }
    
    try {
        // Preparar datos para el mapa
        const puntos = data.mapa.map(item => ({
            lat: parseFloat(item.latitud),
            lon: parseFloat(item.longitud),
            valor: item.cantidad_transacciones
        }));
        
        // Verificar la validez de las coordenadas
        const datosFiltrados = puntos.filter(p => 
            !isNaN(p.lat) && !isNaN(p.lon) && 
            p.lat >= 17.5 && p.lat <= 20 && 
            p.lon >= -72 && p.lon <= -68
        );
        
        if (datosFiltrados.length === 0) {
            container.innerHTML = '<div class="no-data-message">No hay coordenadas válidas para mostrar</div>';
            return;
        }
        
        // Encontrar el centro del mapa
        const centroMapa = {
            lat: 18.735693,
            lon: -70.162651 // Centro aproximado de República Dominicana
        };
        
        // Crear trace para un mapa de calor
        const trace = {
            type: 'densitymapbox',
            lat: datosFiltrados.map(p => p.lat),
            lon: datosFiltrados.map(p => p.lon),
            z: datosFiltrados.map(p => p.valor),
            radius: 20,
            colorscale: [
                [0, 'rgba(0,0,255,0.5)'],
                [0.5, 'rgba(0,255,0,0.5)'],
                [1, 'rgba(255,0,0,0.8)']
            ],
            hoverinfo: 'text',
            hovertext: datosFiltrados.map(p => `Transacciones: ${p.valor}`),
            showscale: true,
            colorbar: {
                title: 'Cantidad<br>Transacciones',
                thickness: 15,
                xpad: 10
            }
        };
        
        // Configurar el layout
        const layout = {
            title: 'Distribución Geográfica de Transacciones',
            mapbox: {
                style: 'carto-positron',
                center: {
                    lat: centroMapa.lat,
                    lon: centroMapa.lon
                },
                zoom: 7
            },
            autosize: true,
            margin: { t: 50, b: 0, l: 0, r: 0 }
        };
        
        // Configurar opciones
        const config = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['lasso2d', 'select2d']
        };
        
        // Crear o actualizar el mapa
        Plotly.newPlot(container, [trace], layout, config);
        
        // Guardar referencia global para actualizaciones
        mapFigure = { data: [trace], layout: layout };
        
    } catch (error) {
        console.error('Error al crear mapa de transacciones:', error);
        container.innerHTML = '<div class="error-message">Error al crear el mapa</div>';
    }
}

/**
 * Crea la tabla de transacciones recientes
 * @param {Object} data - Datos con las transacciones recientes
 */
function crearTablaTransaccionesRecientes(data) {
    const container = document.getElementById('transacciones-recientes');
    
    // Verificar si hay datos disponibles
    if (!data || !data.recientes || data.recientes.length === 0) {
        container.innerHTML = '<div class="no-data-message">No hay transacciones recientes disponibles</div>';
        return;
    }
    
    try {
        // Crear estructura de la tabla
        let tablaHTML = `
            <table class="tabla-transacciones">
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>Terminal</th>
                        <th>Negocio</th>
                        <th>Monto</th>
                        <th>Tarjeta</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        // Agregar filas con las transacciones recientes
        data.recientes.forEach(tx => {
            // Formatear fecha
            const fecha = new Date(tx.fecha_transaccion);
            const fechaFormateada = fecha.toLocaleDateString('es-DO') + ' ' + fecha.toLocaleTimeString('es-DO', {hour: '2-digit', minute:'2-digit'});
            
            // Determinar clase CSS según el estado
            const estadoClase = tx.estado === 'Aprobada' ? 'estado-aprobado' : 
                               tx.estado === 'Rechazada' ? 'estado-rechazado' : 'estado-pendiente';
            
            // Formatear monto
            const montoFormateado = parseFloat(tx.monto).toLocaleString('es-DO', {
                style: 'currency',
                currency: 'DOP',
                minimumFractionDigits: 2
            });
            
            // Agregar fila a la tabla
            tablaHTML += `
                <tr>
                    <td>${fechaFormateada}</td>
                    <td>${tx.terminal_id || '-'}</td>
                    <td>${tx.nombre_negocio || '-'}</td>
                    <td class="monto">${montoFormateado}</td>
                    <td>${tx.tipo_tarjeta || '-'}</td>
                    <td><span class="estado ${estadoClase}">${tx.estado}</span></td>
                </tr>
            `;
        });
        
        // Cerrar la estructura de la tabla
        tablaHTML += `
                </tbody>
            </table>
        `;
        
        // Insertar tabla en el contenedor
        container.innerHTML = tablaHTML;
        
    } catch (error) {
        console.error('Error al crear tabla de transacciones recientes:', error);
        container.innerHTML = '<div class="error-message">Error al crear la tabla de transacciones</div>';
    }
}

/**
 * Formatea un valor numérico para mostrar como monto en pesos dominicanos
 */
function formatearMonto(valor) {
    // Para montos grandes usar formato simplificado (K, M, B)
    if (valor >= 1000000000) {
        return (valor / 1000000000).toFixed(1) + 'B';
    } else if (valor >= 1000000) {
        return (valor / 1000000).toFixed(1) + 'M';
    } else if (valor >= 1000) {
        return (valor / 1000).toFixed(1) + 'K';
    } else {
        return valor.toLocaleString('es-DO');
    }
}

/**
 * Formatea un valor de comparativa para mostrar con signo y porcentaje
 */
function formatearComparativa(valor) {
    const signo = valor >= 0 ? '+' : '';
    return `${signo}${valor.toFixed(1)}% vs ayer`;
}

/**
 * Muestra un mensaje de error en el dashboard
 */
function mostrarMensajeError(mensaje) {
    const errorContainer = document.getElementById('error-container');
    if (errorContainer) {
        errorContainer.textContent = mensaje;
        errorContainer.style.display = 'block';
        
        // Ocultar después de 5 segundos
        setTimeout(() => {
            errorContainer.style.display = 'none';
        }, 5000);
    }
}

/**
 * Carga los datos del dashboard desde el servidor
 */
function fetchDashboardData() {
    // Mostrar indicador de carga
    document.getElementById('loading-indicator').style.display = 'flex';
    
    // Construir URL con filtros
    const url = '/api/dashboard/data?' + new URLSearchParams({
        fecha_inicio: filtros.fecha_inicio,
        fecha_fin: filtros.fecha_fin,
        tipo_tarjeta: filtros.tipo_tarjeta,
        provincia: filtros.provincia,
        tipo_negocio: filtros.tipo_negocio
    }).toString();
    
    console.log('Cargando datos desde:', url);
    
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Datos recibidos:', data);
            
            // Verificar si los datos son válidos
            if (!data) {
                throw new Error('No se recibieron datos del servidor');
            }
            
            // Guardar datos en variable global
            dashboardData = data;
            
            // Actualizar solo componentes básicos, evitando gráficos
            actualizarKPIs();
            // Comentamos las siguientes líneas para evitar bucles de actualización
            // actualizarGraficoLineaTemporal();
            // actualizarGraficoTerminales();
            // actualizarGraficoTiposNegocios();
            // actualizarMapaTransacciones();
            actualizarTablaTransaccionesRecientes();
            
            // Mostrar última actualización
            const ahora = new Date();
            document.getElementById('ultima-actualizacion').textContent = 
                `Última actualización: ${ahora.toLocaleTimeString()}`;
            
            // Ocultar indicador de carga
            document.getElementById('loading-indicator').style.display = 'none';
        })
        .catch(error => {
            console.error('Error al cargar datos:', error);
            
            // Mostrar mensaje de error
            document.getElementById('error-container').innerHTML = 
                `<div class="alert alert-danger">Error al cargar datos: ${error.message}</div>`;
            document.getElementById('error-container').style.display = 'block';
            
            // Si no hay datos aún, usar datos de ejemplo básicos
            if (!dashboardData) {
                console.log('Usando datos de ejemplo básicos');
                dashboardData = {
                    kpis: {
                        num_transacciones: 0,
                        monto_total: 0,
                        tasa_aprobacion: 0,
                        porcentaje_credito: 0,
                        porcentaje_debito: 0,
                        comparativa_transacciones: 0,
                        comparativa_monto: 0
                    },
                    transacciones_hora: [],
                    terminal_status: [],
                    tipos_negocio: [],
                    mapa_transacciones: [],
                    transacciones_recientes: [],
                    filtros: {
                        provincias: [],
                        tipos_negocio: []
                    }
                };
            }
            
            // Ocultar indicador de carga
            document.getElementById('loading-indicator').style.display = 'none';
        });
}

/**
 * Crea el gráfico de línea para transacciones por hora
 */
function crearGraficoLinea(data) {
    try {
        // Verificar si hay datos disponibles
        if (!data || !data.transacciones_hora || data.transacciones_hora.length === 0) {
            console.warn('No hay datos para el gráfico de línea');
            document.getElementById('linechart-container').innerHTML = 
                '<div class="alert alert-warning">No hay datos disponibles para el período seleccionado</div>';
            return;
        }

        // Preparar datos para el gráfico
        const horas = data.transacciones_hora.map(item => item.hora);
        const numTransacciones = data.transacciones_hora.map(item => item.num_transacciones);
        const montoTotal = data.transacciones_hora.map(item => item.monto_total);

        // Configurar el gráfico
        const trace1 = {
            x: horas,
            y: numTransacciones,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Número de Transacciones',
            line: {
                color: '#4C9AFF',
                width: 3
            },
            marker: {
                size: 8
            }
        };

        const trace2 = {
            x: horas,
            y: montoTotal,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Monto Total (RD$)',
            yaxis: 'y2',
            line: {
                color: '#00C7E6',
                width: 3
            },
            marker: {
                size: 8
            }
        };

        const layout = {
            title: 'Transacciones por Hora',
            font: {
                family: 'Roboto, sans-serif'
            },
            xaxis: {
                title: 'Hora',
                tickformat: '%H:%M',
                gridcolor: '#EEEEEE'
            },
            yaxis: {
                title: 'Número de Transacciones',
                titlefont: { color: '#4C9AFF' },
                tickfont: { color: '#4C9AFF' },
                gridcolor: '#EEEEEE'
            },
            yaxis2: {
                title: 'Monto Total (RD$)',
                titlefont: { color: '#00C7E6' },
                tickfont: { color: '#00C7E6' },
                overlaying: 'y',
                side: 'right',
                gridcolor: '#EEEEEE'
            },
            legend: {
                orientation: 'h',
                y: -0.2
            },
            margin: {
                l: 70,
                r: 70,
                t: 50,
                b: 100
            },
            height: 400,
            hovermode: 'x unified',
            plot_bgcolor: '#FFFFFF',
            paper_bgcolor: '#FFFFFF'
        };

        // Renderizar el gráfico
        Plotly.newPlot('linechart-container', [trace1, trace2], layout, {responsive: true});
    } catch (error) {
        console.error('Error al crear gráfico de línea:', error);
        document.getElementById('linechart-container').innerHTML = 
            `<div class="alert alert-danger">Error al crear gráfico: ${error.message}</div>`;
    }
}

/**
 * Crea el gráfico de pie para el estado de terminales
 */
function crearGraficoStatusTerminales(data) {
    try {
        // Verificar si hay datos disponibles
        if (!data || !data.estado_terminales || data.estado_terminales.length === 0) {
            console.warn('No hay datos para el gráfico de estado de terminales');
            document.getElementById('terminalstatus-container').innerHTML = 
                '<div class="alert alert-warning">No hay datos disponibles para el período seleccionado</div>';
            return;
        }

        // Preparar datos para el gráfico
        const estados = data.estado_terminales.map(item => item.estado);
        const cantidades = data.estado_terminales.map(item => item.cantidad);
        
        // Colores para cada estado
        const colores = {
            'Activo': '#36B37E',  // Verde
            'Inactivo': '#FF5630', // Rojo
            'Mantenimiento': '#FFAB00', // Amarillo
            'Pendiente': '#6554C0'  // Morado
        };

        // Asignar colores según el estado, con un color predeterminado para estados no definidos
        const coloresActuales = estados.map(estado => colores[estado] || '#DFE1E6');

        // Configurar el gráfico
        const dataGrafico = [{
            labels: estados,
            values: cantidades,
            type: 'pie',
            textinfo: 'value+percent',
            textposition: 'inside',
            automargin: true,
            hole: 0.4,
            marker: {
                colors: coloresActuales,
                line: {
                    color: '#FFFFFF',
                    width: 2
                }
            },
            insidetextfont: {
                color: '#FFFFFF',
                size: 14
            }
        }];

        const layout = {
            title: 'Estado de Terminales',
            font: {
                family: 'Roboto, sans-serif'
            },
            showlegend: true,
            legend: {
                orientation: 'h',
                y: -0.2
            },
            height: 400,
            margin: {
                l: 20,
                r: 20,
                t: 50,
                b: 100
            },
            plot_bgcolor: '#FFFFFF',
            paper_bgcolor: '#FFFFFF'
        };

        // Renderizar el gráfico
        Plotly.newPlot('terminalstatus-container', dataGrafico, layout, {responsive: true});
    } catch (error) {
        console.error('Error al crear gráfico de estado de terminales:', error);
        document.getElementById('terminalstatus-container').innerHTML = 
            `<div class="alert alert-danger">Error al crear gráfico: ${error.message}</div>`;
    }
}

/**
 * Crea el gráfico de barras para tipos de negocio
 */
function crearGraficoTiposNegocio(data) {
    try {
        // Verificar si hay datos disponibles
        if (!data || !data.tipos_negocio || data.tipos_negocio.length === 0) {
            console.warn('No hay datos para el gráfico de tipos de negocio');
            document.getElementById('businesstypes-container').innerHTML = 
                '<div class="alert alert-warning">No hay datos disponibles para el período seleccionado</div>';
            return;
        }

        // Ordenar datos por volumen de transacciones (de mayor a menor)
        const datosOrdenados = [...data.tipos_negocio].sort((a, b) => b.transacciones - a.transacciones);
        
        // Limitar a los 10 principales tipos de negocio para mejor visualización
        const datosLimitados = datosOrdenados.slice(0, 10);
        
        // Preparar datos para el gráfico
        const tiposNegocio = datosLimitados.map(item => item.tipo_negocio);
        const transacciones = datosLimitados.map(item => item.transacciones);
        const montos = datosLimitados.map(item => item.monto_total);
        
        // Configurar los datos del gráfico
        const trace1 = {
            x: tiposNegocio,
            y: transacciones,
            name: 'Transacciones',
            type: 'bar',
            marker: {
                color: '#00B8D9',
                line: {
                    color: '#0095B3',
                    width: 1.5
                }
            }
        };
        
        const trace2 = {
            x: tiposNegocio,
            y: montos,
            name: 'Monto Total (RD$)',
            type: 'bar',
            yaxis: 'y2',
            marker: {
                color: '#6554C0',
                line: {
                    color: '#4C3D9D',
                    width: 1.5
                }
            }
        };
        
        const dataGrafico = [trace1, trace2];
        
        // Configurar el layout del gráfico
        const layout = {
            title: 'Top 10 Tipos de Negocio',
            font: {
                family: 'Roboto, sans-serif'
            },
            barmode: 'group',
            xaxis: {
                title: 'Tipo de Negocio',
                tickangle: -45,
                tickfont: {
                    size: 10
                },
                automargin: true
            },
            yaxis: {
                title: 'Número de Transacciones',
                titlefont: {
                    color: '#00B8D9'
                },
                tickfont: {
                    color: '#00B8D9'
                }
            },
            yaxis2: {
                title: 'Monto Total (RD$)',
                titlefont: {
                    color: '#6554C0'
                },
                tickfont: {
                    color: '#6554C0'
                },
                overlaying: 'y',
                side: 'right',
                tickformat: ',.0f'
            },
            legend: {
                orientation: 'h',
                y: -0.3
            },
            height: 450,
            margin: {
                l: 60,
                r: 80,
                t: 50,
                b: 120
            },
            plot_bgcolor: '#FFFFFF',
            paper_bgcolor: '#FFFFFF'
        };
        
        // Renderizar el gráfico
        Plotly.newPlot('businesstypes-container', dataGrafico, layout, {responsive: true});
    } catch (error) {
        console.error('Error al crear gráfico de tipos de negocio:', error);
        document.getElementById('businesstypes-container').innerHTML = 
            `<div class="alert alert-danger">Error al crear gráfico: ${error.message}</div>`;
    }
}

/**
 * Crea el gráfico de transacciones por hora
 */
function crearGraficoTransacciones(data) {
    if (!data || !data.transacciones_por_hora) {
        console.warn('No hay datos para el gráfico de transacciones por hora');
        return;
    }
    
    console.log('Creando gráfico de transacciones por hora');
    const container = document.querySelector('#chart-transacciones-hora .chart-content');
    if (!container) {
        console.error('No se encontró el contenedor para el gráfico de transacciones');
        return;
    }
    
    try {
        // Preparar datos para el gráfico
        const transacciones = data.transacciones_por_hora;
        const horas = transacciones.map(item => item.hora);
        const cantidades = transacciones.map(item => item.total);
        
        const trace = {
            x: horas,
            y: cantidades,
            type: 'scatter',
            mode: 'lines+markers',
            line: {
                color: '#3498db',
                width: 3
            },
            marker: {
                color: '#2980b9',
                size: 8
            },
            name: 'Transacciones'
        };
        
        const layout = {
            margin: {l: 50, r: 20, b: 50, t: 20},
            xaxis: {
                title: 'Hora',
                tickangle: -45
            },
            yaxis: {
                title: 'Cantidad',
                gridcolor: '#e0e0e0'
            },
            plot_bgcolor: '#f9f9f9',
            paper_bgcolor: '#f9f9f9',
            hovermode: 'closest'
        };
        
        Plotly.newPlot(container, [trace], layout, {responsive: true, displayModeBar: false});
        console.log('Gráfico de transacciones creado correctamente');
    } catch (error) {
        console.error('Error al crear gráfico de transacciones:', error);
        container.innerHTML = '<div class="error-message">Error al crear el gráfico de transacciones</div>';
    }
}

/**
 * Crea el gráfico de estado de terminales
 */
function crearGraficoTerminales(data) {
    if (!data || !data.terminales) {
        console.warn('No hay datos para el gráfico de terminales');
        return;
    }
    
    console.log('Creando gráfico de estado de terminales');
    const container = document.querySelector('#chart-estado-terminales .chart-content');
    if (!container) {
        console.error('No se encontró el contenedor para el gráfico de terminales');
        return;
    }
    
    try {
        const terminales = data.terminales;
        const estados = ['Activos', 'Inactivos', 'Mantenimiento'];
        const valores = [terminales.activos, terminales.inactivos, terminales.mantenimiento];
        
        const trace = {
            x: valores,
            y: estados,
            type: 'bar',
            orientation: 'h',
            marker: {
                color: ['#2ecc71', '#e74c3c', '#f1c40f'],
            }
        };
        
        const layout = {
            margin: {l: 100, r: 20, b: 30, t: 20},
            xaxis: {
                title: 'Cantidad'
            },
            plot_bgcolor: '#f9f9f9',
            paper_bgcolor: '#f9f9f9'
        };
        
        Plotly.newPlot(container, [trace], layout, {responsive: true, displayModeBar: false});
        console.log('Gráfico de terminales creado correctamente');
    } catch (error) {
        console.error('Error al crear gráfico de terminales:', error);
        container.innerHTML = '<div class="error-message">Error al crear el gráfico de terminales</div>';
    }
}

/**
 * Crea el gráfico de tipos de negocio
 */
function crearGraficoTiposNegocio(data) {
    if (!data || !data.tipos_negocio || data.tipos_negocio.length === 0) {
        console.warn('No hay datos para el gráfico de tipos de negocio');
        return;
    }
    
    console.log('Creando gráfico de tipos de negocio');
    const container = document.querySelector('#chart-tipos-negocio .chart-content');
    if (!container) {
        console.error('No se encontró el contenedor para el gráfico de tipos de negocio');
        return;
    }
    
    try {
        // Ordenar por número de transacciones (de mayor a menor)
        const tiposNegocioOrdenados = [...data.tipos_negocio].sort((a, b) => 
            b.transacciones - a.transacciones
        );
        
        // Limitar a los 5 primeros para mejor visualización
        const top5 = tiposNegocioOrdenados.slice(0, 5);
        
        const labels = top5.map(item => item.tipo_negocio);
        const valores = top5.map(item => item.transacciones);
        
        const trace = {
            x: valores,
            y: labels,
            type: 'bar',
            orientation: 'h',
            marker: {
                color: '#3498db',
                opacity: 0.8
            }
        };
        
        const layout = {
            margin: {l: 120, r: 20, b: 30, t: 20},
            xaxis: {
                title: 'Transacciones'
            },
            plot_bgcolor: '#f9f9f9',
            paper_bgcolor: '#f9f9f9'
        };
        
        Plotly.newPlot(container, [trace], layout, {responsive: true, displayModeBar: false});
        console.log('Gráfico de tipos de negocio creado correctamente');
    } catch (error) {
        console.error('Error al crear gráfico de tipos de negocio:', error);
        container.innerHTML = '<div class="error-message">Error al crear el gráfico de tipos de negocio</div>';
    }
}

/**
 * Crea el mapa de transacciones
 */
function crearMapaTransacciones(data) {
    if (!data || !data.mapa_transacciones || data.mapa_transacciones.length === 0) {
        console.warn('No hay datos para el mapa de transacciones');
        return;
    }
    
    console.log('Creando mapa de transacciones');
    const container = document.querySelector('#chart-mapa .chart-content');
    if (!container) {
        console.error('No se encontró el contenedor para el mapa');
        return;
    }
    
    try {
        const puntos = data.mapa_transacciones;
        
        // Extraer datos para el mapa
        const latitudes = puntos.map(p => p.latitud);
        const longitudes = puntos.map(p => p.longitud);
        const intensidades = puntos.map(p => p.transacciones);
        const textos = puntos.map(p => 
            `<b>${p.nombre_negocio}</b><br>` +
            `Provincia: ${p.provincia}<br>` +
            `Transacciones: ${p.transacciones}<br>` +
            `Monto: RD$ ${p.monto_total.toLocaleString()}`
        );
        
        // Centrar el mapa en República Dominicana
        const centerLat = 18.735693;
        const centerLon = -70.162651;
        
        // Configurar trace para el mapa
        const trace = {
            type: 'scattermapbox',
            lon: longitudes,
            lat: latitudes,
            text: textos,
            mode: 'markers',
            marker: {
                size: intensidades.map(i => Math.min(Math.max(i/50, 5), 20)),
                color: intensidades,
                colorscale: 'Viridis',
                colorbar: {
                    title: 'Transacciones',
                    thickness: 15,
                    xpad: 10
                },
                opacity: 0.8
            },
            hoverinfo: 'text'
        };
        
        // Configurar layout
        const layout = {
            mapbox: {
                style: 'open-street-map',
                center: {
                    lat: centerLat, 
                    lon: centerLon
                },
                zoom: 7
            },
            margin: {l: 0, r: 0, t: 0, b: 0},
            height: 400
        };
        
        // Crear el mapa
        Plotly.newPlot(container, [trace], layout, {responsive: true});
        console.log('Mapa de transacciones creado correctamente');
    } catch (error) {
        console.error('Error al crear mapa de transacciones:', error);
        container.innerHTML = '<div class="error-message">Error al crear el mapa de transacciones</div>';
    }
}

/**
 * Actualiza la tabla de transacciones recientes
 */
function actualizarTablaTransacciones(data) {
    if (!data || !data.transacciones_recientes || data.transacciones_recientes.length === 0) {
        console.warn('No hay datos para la tabla de transacciones recientes');
        return;
    }
    
    console.log('Actualizando tabla de transacciones recientes');
    const container = document.querySelector('.recent-transactions .table-container');
    if (!container) {
        console.error('No se encontró el contenedor para la tabla de transacciones');
        return;
    }
    
    try {
        // Construir tabla HTML
        let tablaHTML = `
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Fecha/Hora</th>
                        <th>Comercio</th>
                        <th>Monto</th>
                        <th>Tipo</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        // Agregar filas de transacciones
        data.transacciones_recientes.forEach(tx => {
            // Formatear fecha
            const fecha = new Date(tx.fecha_hora);
            const fechaFormateada = fecha.toLocaleString('es-DO');
            
            // Formatear monto
            const montoFormateado = parseFloat(tx.monto).toLocaleString('es-DO', {
                style: 'currency',
                currency: 'DOP'
            });
            
            // Determinar clase para el estado
            const estadoClass = tx.estado === 'aprobada' ? 'status-approved' : 
                            tx.estado === 'rechazada' ? 'status-rejected' : 
                            'status-pending';
            
            // Crear fila
            tablaHTML += `
                <tr>
                    <td>${tx.transaccion_id}</td>
                    <td>${fechaFormateada}</td>
                    <td>${tx.nombre_negocio}</td>
                    <td>${montoFormateado}</td>
                    <td>${tx.tipo_tarjeta}</td>
                    <td class="${estadoClass}">${tx.estado}</td>
                </tr>
            `;
        });
        
        // Cerrar estructura de tabla
        tablaHTML += `
                </tbody>
            </table>
        `;
        
        // Actualizar el contenedor con la tabla
        container.innerHTML = tablaHTML;
        console.log('Tabla de transacciones actualizada correctamente');
    } catch (error) {
        console.error('Error al actualizar tabla de transacciones:', error);
        container.innerHTML = '<div class="error-message">Error al actualizar la tabla de transacciones</div>';
    }
}

/**
 * Muestra u oculta el indicador de carga
 */
function mostrarIndicadorCarga(mostrar) {
    const loader = document.getElementById('loading-indicator');
    if (loader) {
        loader.style.display = mostrar ? 'flex' : 'none';
    }
}

/**
 * Actualiza las opciones de los filtros con los datos recibidos
 */
function actualizarFiltros(data) {
    if (!data || !data.filtros) {
        debug('No hay datos de filtros disponibles para actualizar las opciones');
        return;
    }
    
    debug('Actualizando opciones de filtros');
    
    // Actualizar provincias
    if (data.filtros.provincias && data.filtros.provincias.length > 0) {
        const selectProvincia = document.getElementById('filtro-provincia');
        const valorActual = selectProvincia.value;
        
        // Preservar la primera opción (Todas)
        const opcionTodas = selectProvincia.options[0];
        selectProvincia.innerHTML = '';
        selectProvincia.appendChild(opcionTodas);
        
        // Agregar opciones nuevas
        data.filtros.provincias.forEach(provincia => {
            if (provincia) {
                const option = document.createElement('option');
                option.value = provincia;
                option.textContent = provincia;
                selectProvincia.appendChild(option);
            }
        });
        
        // Restaurar valor seleccionado si existe en las nuevas opciones
        if (valorActual !== 'todos') {
            for (let i = 0; i < selectProvincia.options.length; i++) {
                if (selectProvincia.options[i].value === valorActual) {
                    selectProvincia.selectedIndex = i;
                    break;
                }
            }
        }
        
        debug(`Filtro de provincias actualizado con ${data.filtros.provincias.length} opciones`);
    }
    
    // Actualizar tipos de negocio
    if (data.filtros.tipos_negocio && data.filtros.tipos_negocio.length > 0) {
        const selectTipoNegocio = document.getElementById('filtro-tipo-negocio');
        const valorActual = selectTipoNegocio.value;
        
        // Preservar la primera opción (Todos)
        const opcionTodos = selectTipoNegocio.options[0];
        selectTipoNegocio.innerHTML = '';
        selectTipoNegocio.appendChild(opcionTodos);
        
        // Agregar opciones nuevas
        data.filtros.tipos_negocio.forEach(tipo => {
            if (tipo) {
                const option = document.createElement('option');
                option.value = tipo;
                option.textContent = tipo;
                selectTipoNegocio.appendChild(option);
            }
        });
        
        // Restaurar valor seleccionado si existe en las nuevas opciones
        if (valorActual !== 'todos') {
            for (let i = 0; i < selectTipoNegocio.options.length; i++) {
                if (selectTipoNegocio.options[i].value === valorActual) {
                    selectTipoNegocio.selectedIndex = i;
                    break;
                }
            }
        }
        
        debug(`Filtro de tipos de negocio actualizado con ${data.filtros.tipos_negocio.length} opciones`);
    }
    
    // Actualizar tipos de tarjeta (si no existen, usar valores predeterminados)
    const selectTipoTarjeta = document.getElementById('filtro-tipo-tarjeta');
    if (selectTipoTarjeta.options.length <= 1) {
        const tiposTarjeta = ['credito', 'debito', 'prepago'];
        const nombresTipos = ['Crédito', 'Débito', 'Prepago'];
        
        for (let i = 0; i < tiposTarjeta.length; i++) {
            const option = document.createElement('option');
            option.value = tiposTarjeta[i];
            option.textContent = nombresTipos[i];
            selectTipoTarjeta.appendChild(option);
        }
        
        debug('Filtro de tipos de tarjeta actualizado con valores predeterminados');
    }
}

/**
 * Actualiza el dashboard automáticamente cada cierto intervalo
 * NOTA: Esta función ha sido desactivada porque estaba causando bucles de actualización.
 * En su lugar, se utiliza programarActualizacion() que ya maneja el intervalo de actualización.
 */
function actualizarDashboard() {
    console.log('La función actualizarDashboard ha sido desactivada para evitar bucles.');
    // La implementación anterior causaba actualizaciones duplicadas:
    // cargarDatos();
    // setTimeout(actualizarDashboard, updateInterval);
} 