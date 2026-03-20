# Colombia Economic Insights

Proyecto para extraer, procesar y analizar datos económicos de Colombia desde BigQuery, con análisis estadístico automatizado y dashboard web interactivo.

## Descripción

Este proyecto integra datos de BigQuery con Python para generar insights económicos sobre Colombia. Incluye análisis estadístico automatizado, generación de reportes CSV y un dashboard web interactivo construido con Streamlit.

## 🗄️ Extracción de Datos y Metodología SQL

Para este análisis, se utilizaron los datasets públicos del **Banco Mundial (World Bank WDI)** alojados en **Google BigQuery**. La extracción se realizó mediante una consulta optimizada que combina información geográfica y métricas económicas.

### 🔍 Consulta de Extracción (ETL)
Se realizó un `JOIN` entre la tabla de resumen de países y la tabla de indicadores históricos para garantizar la integridad de los datos de Colombia:

```sql
SELECT 
    t1.country_code,
    t1.short_name AS country,
    t1.currency_unit,
    t2.year,
    t2.value AS inflation_rate
FROM 
    `bigquery-public-data.world_bank_wdi.country_summary` AS t1
JOIN 
    `bigquery-public-data.world_bank_wdi.indicators_data` AS t2 
    ON t2.country_code = t1.country_code
WHERE 
    t2.indicator_code = 'FP.CPI.TOTL.ZG' -- Código para Inflación (Precios al Consumidor)
    AND t1.short_name = 'Colombia'
ORDER BY 
    t2.year ASC;S
```

## Estructura del Proyecto

```
colombia-economic-insights/
├── src/                    # Código principal
│   ├── __init__.py
│   ├── bigquery_client.py  # Cliente para conectar a BigQuery
│   ├── analysis.py         # Análisis estadístico automatizado
│   ├── looker_integration.py # Integración con Looker Studio [NO IMPLEMENTADO]
│   └── main.py             # Script principal con CLI
├── output/                 # Reportes generados automáticamente
│   ├── charts/            # Gráficos (cuando estén disponibles)
│   ├── *.csv              # Archivos CSV con datos y estadísticas
├── config/                 # Configuración
├── requirements.txt        # Dependencias Python
├── .env.example           # Variables de entorno (ejemplo)
├── service-account-key.json # Credenciales GCP (no subir a git)
└── README.md              # Este archivo
```

## Requisitos Técnicos

- Python 3.8+
- Google Cloud Project con BigQuery API habilitada
- Service Account con permisos adecuados
- Conexión a internet para APIs de Google

## Instalación y Configuración

### 1. Clonar e instalar dependencias

```bash
git clone <repository-url>
cd colombia-economic-insights
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Configurar credenciales de GCP

#### Opción A: Service Account (Recomendado)

- Ve a [Google Cloud Console](https://console.cloud.google.com/)
- Crea o selecciona el proyecto `analisis-finanzas-globales`
- **Habilita las APIs necesarias:**
  - BigQuery API
- **Crea una Service Account:**
  - Ve a "IAM & Admin" > "Service Accounts"
  - Crea nueva Service Account: `colombia-economic-insights@analisis-finanzas-globales.iam.gserviceaccount.com`
  - Otorga los siguientes roles:
    - `BigQuery Data Viewer` (para leer datos)
    - `BigQuery Job User` (para ejecutar queries)
- **Descarga la clave JSON** y guárdala como `service-account-key.json`

#### Opción B: OAuth 2.0

Si ya tienes credenciales OAuth y un Client ID, descarga el archivo JSON completo desde Google Cloud Console:

1. Ve a [Google Cloud Console > APIs & Credentials](https://console.cloud.google.com/apis/credentials)
2. Encuentra tus "OAuth 2.0 Client IDs"
3. Haz clic en el botón de descarga junto a tu Client ID
4. Renómbralo a `client_secret.json` y colócalo en la raíz del proyecto

> **Nota**: OAuth requiere autenticación manual en el navegador la primera vez, mientras que Service Account es completamente automático.

### 3. Probar la configuración

```bash
# Ejecuta el verificador automático de configuración
python src/verify_config.py

# Prueba básica de conexión
python src/main.py --test-connection
```

## Uso del Sistema

### Análisis Básico

```bash
# Ver tablas disponibles
python src/main.py

# Analizar una tabla específica
python src/main.py --table analisis-finanzas-globales.colombia_economic_data.inflation
```

### Reportes Generados Automáticamente

Los siguientes archivos CSV se generan en el directorio `output/`:

| Archivo | Descripción |
|---|---|
| `summary.csv` | Tabla resumen con métricas principales |
| `basic_stats.csv` | Estadísticas descriptivas (media, mediana, desviación) |
| `yearly_stats.csv` | Estadísticas por año con cambio interanual |
| `percentiles.csv` | Análisis de percentiles |
| `outliers.csv` | Detección automática de valores atípicos |

### Estadísticas Incluidas

- 📊 Media, mediana, desviación estándar
- 📈 Tendencias año a año (% cambio interanual)
- 📉 Percentiles (10%, 25%, 50%, 75%, 90%, 95%, 99%)
- 🎯 Detección automática de outliers (método IQR)
- 📅 Cobertura temporal completa de datos

## Dashboard Web Interactivo (Streamlit)

### Ejecutar el Dashboard

```bash
# Opción 1: Ejecutar directamente
streamlit run app.py

# Opción 2: Usar el script de Windows
run_dashboard.bat

# Opción 3: Ejecutar con Python (si streamlit no está en PATH)
python -m streamlit run app.py
```

Una vez ejecutado, abre tu navegador en:

```
http://localhost:8501
```

### Características del Dashboard

- 📊 **Visualizaciones Interactivas**: Gráficos de series temporales, distribuciones y tendencias
- 📈 **Métricas en Tiempo Real**: KPIs principales en tarjetas
- 📉 **Análisis de Tendencias**: Medias móviles y cambios porcentuales
- 📋 **Exploración de Datos**: Tablas interactivas con filtros
- 📥 **Descargas**: Exportar datos en formato CSV
- 🎯 **Análisis de Outliers**: Detección y visualización de valores atípicos

### Pestañas Disponibles

1. **📈 Resumen**: Vista general con métricas clave y gráficos principales
2. **📊 Estadísticas**: Análisis detallado de estadísticas y percentiles
3. **📉 Tendencias**: Análisis de tendencias con medias móviles
4. **📋 Datos**: Tablas de datos crudos con opciones de descarga
5. **ℹ️ Información**: Documentación del proyecto y metodología

## Ejemplos de Uso

```bash
# Análisis de inflación
python src/main.py --table analisis-finanzas-globales.colombia_economic_data.inflation

# Análisis de PIB
python src/main.py --table analisis-finanzas-globales.colombia_economic_data.gdp

# Solo probar conexión
python src/main.py --test-connection
```

## Estado del Proyecto

| Componente | Estado |
|---|---|
| Conexión a BigQuery | ✅ Implementado |
| Extracción de datos | ✅ Implementado |
| Análisis estadístico automatizado | ✅ Implementado |
| Generación de reportes CSV | ✅ Implementado |
| Dashboard web interactivo (Streamlit) | ✅ Implementado |
| Integración con Looker Studio | ❌ No implementado |
| Visualizaciones automáticas (matplotlib) | ⏳ Pendiente (problemas de compatibilidad) |

## Solución de Problemas

### Error de credenciales

```bash
# Asegúrate de que el archivo existe
ls service-account-key.json

# O configura la variable de entorno
set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\service-account-key.json
```

### Error de permisos en BigQuery

1. Ve a [APIs & Services > Library](https://console.cloud.google.com/apis/library)
2. Verifica que estén habilitadas:
   - **BigQuery API**
3. Ve a "IAM & Admin > IAM" y confirma que tu Service Account tenga los roles:
   - `BigQuery Data Viewer`
   - `BigQuery Job User`

### Error de matplotlib

Las visualizaciones automáticas están temporalmente deshabilitadas. Usa los CSV generados en Excel, Google Sheets, o explóralos directamente desde el dashboard de Streamlit.

### Probar configuración

```bash
python src/verify_config.py
python src/main.py --test-connection
```
Table No_implementada --looker
``` 
