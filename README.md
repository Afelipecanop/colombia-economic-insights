# Colombia Economic Insights

Proyecto para extraer, procesar y analizar datos económicos de Colombia desde BigQuery y automatizar reportes en Looker Studio.

## Descripción

Este proyecto integra datos de BigQuery y Looker Studio para generar insights económicos sobre Colombia con análisis estadístico automatizado y reportes en la nube.

## Estructura del Proyecto

```
colombia-economic-insights/
├── src/                    # Código principal
│   ├── __init__.py
│   ├── bigquery_client.py  # Cliente para conectar a BigQuery
│   ├── analysis.py         # Análisis estadístico automatizado
│   ├── looker_integration.py # Integración con Looker Studio
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

#### Opción A: Service Account (Recomendado para automatización)
- Ve a [Google Cloud Console](https://console.cloud.google.com/)
- Crea o selecciona el proyecto `analisis-finanzas-globales`
- **Habilita las APIs necesarias:**
  - BigQuery API
  - Google Drive API
  - Looker Studio API (Data Studio API)
- **Crea una Service Account:**
  - Ve a "IAM & Admin" > "Service Accounts"
  - Crea nueva Service Account: `colombia-economic-insights@analisis-finanzas-globales.iam.gserviceaccount.com`
  - Otorga los siguientes roles:
    - `BigQuery Data Viewer` (para leer datos)
    - `BigQuery Job User` (para ejecutar queries)
    - `Editor` en Google Drive (para subir archivos)
- **Descarga la clave JSON** y guárdala como `service-account-key.json`

#### Opción B: OAuth 2.0 (Si ya tienes credenciales OAuth)
Si ya creaste credenciales OAuth y tienes un Client ID como `938562543425-8sp90m8cegbhh9p0eop9eurkd8fufh2q.apps.googleusercontent.com`, necesitas descargar el archivo JSON completo:

1. Ve a [Google Cloud Console > APIs & Credentials](https://console.cloud.google.com/apis/credentials)
2. Encuentra tus "OAuth 2.0 Client IDs"
3. Haz clic en el botón de descarga (ícono de flecha hacia abajo) junto a tu Client ID
4. El archivo descargado debería llamarse algo como `client_secret_XXXX.json`
5. **Renómbralo a `client_secret.json`** y colócalo en la raíz del proyecto

**Nota**: OAuth requiere autenticación manual en el navegador la primera vez, mientras que Service Account es completamente automático.

**¿Ya tienes el Client ID?** Si descargaste las credenciales OAuth desde GCP Console, el archivo JSON ya contiene toda la información necesaria. Solo asegúrate de que se llame `client_secret.json`.

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

### Análisis Completo con Looker Studio
```bash
# Análisis completo + subir a Looker Studio
python src/main.py --table analisis-finanzas-globales.colombia_economic_data.inflation --looker
```

### Reportes Generados Automáticamente
- **`summary.csv`**: Tabla resumen con métricas principales
- **`basic_stats.csv`**: Estadísticas descriptivas (media, mediana, desviación)
- **`yearly_stats.csv`**: Estadísticas por año con cambio interanual
- **`percentiles.csv`**: Análisis de percentiles
- **`outliers.csv`**: Detección automática de valores atípicos

### Estadísticas Incluidas
- 📊 Media, mediana, desviación estándar
- 📈 Tendencias año a año (% cambio interanual)
- 📉 Percentiles (10%, 25%, 50%, 75%, 90%, 95%, 99%)
- 🎯 Detección automática de outliers (IQR method)
- 📅 Cobertura temporal completa de datos

## Integración con Looker Studio

Cuando usas la opción `--looker`, el sistema automáticamente:
1. ✅ Sube todos los archivos CSV generados a Google Drive
2. ✅ Crea datasets en Looker Studio conectados a estos archivos
3. ✅ Proporciona URLs para acceder a los reportes en la nube

### Beneficios de Looker Studio
- 🔄 **Actualización automática**: Los datos se refrescan automáticamente
- 📊 **Visualizaciones interactivas**: Gráficos, dashboards y reportes
- 👥 **Compartible**: Comparte reportes con stakeholders
- ☁️ **En la nube**: Accede desde cualquier dispositivo

## Ejemplos de Uso

```bash
# Análisis de inflación con reportes locales
python src/main.py --table analisis-finanzas-globales.colombia_economic_data.inflation

# Análisis completo con Looker Studio
python src/main.py --table analisis-finanzas-globales.colombia_economic_data.inflation --looker

# Análisis de PIB
python src/main.py --table analisis-finanzas-globales.colombia_economic_data.gdp --looker

# Solo probar conexión
python src/main.py --test-connection
```

## Requisitos Técnicos
- Python 3.8+
- Google Cloud Project con APIs habilitadas
- Service Account con permisos adecuados
- Conexión a internet para APIs de Google

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

### Características del Dashboard
- 📊 **Visualizaciones Interactivas**: Gráficos de series temporales, distribuciones y tendencias
- 📈 **Métricas en Tiempo Real**: KPIs principales en tarjetas
- 📉 **Análisis de Tendencias**: Medias móviles y cambios porcentuales
- 📋 **Exploración de Datos**: Tablas interactivas con filtros
- 📥 **Descargas**: Exportar datos en formato CSV
- 🎯 **Análisis de Outliers**: Detección y visualización de valores atípicos

### Acceso al Dashboard
Una vez ejecutado `streamlit run app.py`, abre tu navegador en:
```
http://localhost:8501
```

### Pestañas Disponibles
1. **📈 Resumen**: Vista general con métricas clave y gráficos principales
2. **📊 Estadísticas**: Análisis detallado de estadísticas y percentiles
3. **📉 Tendencias**: Análisis de tendencias con medias móviles
4. **📋 Datos**: Tablas de datos crudos con opciones de descarga
5. **ℹ️ Información**: Documentación del proyecto y metodología

## Estado del Proyecto
- ✅ Conexión a BigQuery
- ✅ Extracción de datos
- ✅ Análisis estadístico automatizado
- ✅ Generación de reportes CSV
- ✅ Integración con Looker Studio
- ✅ Dashboard web interactivo (Streamlit)
- ⏳ Visualizaciones automáticas (matplotlib compatibility issues)
- 🔄 Pipeline completo BigQuery → Análisis → Web Dashboard

## Solución de Problemas

### Error de credenciales
```bash
# Asegúrate de que el archivo existe
ls service-account-key.json

# O configura la variable de entorno
set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\service-account-key.json
```

### Error de permisos en Looker Studio
Si ves errores como "Insufficient permissions" al subir a Looker:

1. **Verifica que las APIs estén habilitadas:**
   - Ve a [APIs & Services > Library](https://console.cloud.google.com/apis/library)
   - Busca y habilita:
     - "Google Drive API"
     - "Looker Studio API" (Data Studio API)
     - "BigQuery API"

2. **Configura permisos de Service Account:**
   - Ve a "IAM & Admin > IAM"
   - Encuentra tu Service Account
   - Asegúrate de que tenga estos roles:
     - `BigQuery Data Viewer`
     - `BigQuery Job User`
     - `Editor` (en el proyecto completo)

3. **Permisos específicos para Looker Studio:**
   - La Service Account necesita acceso a Looker Studio
   - Si usas OAuth flow alternativo, asegúrate de que tu cuenta de usuario tenga permisos

### Error de matplotlib
- Las visualizaciones están temporalmente deshabilitadas
- Usa los CSV generados en Excel, Google Sheets o Looker Studio

### Probar configuración
```bash
# Ejecuta el verificador automático de configuración
python src/verify_config.py

# Prueba básica de conexión
python src/main.py --test-connection

# Prueba análisis sin Looker
python src/main.py --table TU_TABLA

# Prueba análisis con Looker (requiere configuración completa)
python src/main.py --table TU_TABLA --looker
```
