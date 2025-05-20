# GESI-TEMIS Integración
Sistema de integración automática entre los sistemas GESI => TEMIS => HIT para la gestión de tickets de emergencia.

## Descripción General
Este proyecto automatiza la creación y gestión de tickets y tdc entre los sistemas GESI y TEMIS, posteriormente a través de una API dispara una llamada al cliente registrado. El sistema extrae información de tickets de emergencia desde GESI, procesa los datos y los carga en TEMIS, incluyendo la creación de tickets, TDCs (Trabajos de Campo, con las coordenadas de los TRAFOS) y la asignación de técnicos.

## Estructura del Proyecto
```
proyecto/
│
├── config/                     # Configuraciones del sistema
│   ├── __init__.py                 # Indicar que un directorio debe ser tratado como un paquete de Python
│   └── settings.py                 # Configuraciones centralizadas
│
├── core/                       # Funcionalidad principal
│   ├── __init__.py                 # Indicar que un directorio debe ser tratado como un paquete de Python
│   ├── sharepoint_manager.py       # Gestión de SharePoint
│   └── temis_manager.py            # Integración con TEMIS
│
├── automation/                 # Módulos de automatización
│   ├── __init__.py                 # Indicar que un directorio debe ser tratado como un paquete de Python
│   ├── gui_automation.py           # Automatización de GUI
│   └── resources.py                # Gestión de recursos
│
├── data/                       # Procesamiento de datos
│   ├── __init__.py                 # Indicar que un directorio debe ser tratado como un paquete de Python
│   └── data_processor.py           # Procesamiento de datos
│
├── utils/                      # Utilidades
│   ├── __init__.py                 # Indicar que un directorio debe ser tratado como un paquete de Python
│   └── logger.py                   # Sistema de logging
│
├── __init__.py                 # Indicar que un directorio debe ser tratado como un paquete de Python
├── README.md                   # Documentación 
├── icono.png                   # Imagen icono del ejecutable 
├── GESI-TEMIS.spec             # El archivo .spec en PyInstaller se utiliza para personalizar el proceso de creación de un ejecutable
└── main.py                     # Punto de entrada principal
```

## Componentes Principales

### SharePoint Manager (`core/sharepoint_manager.py`)
Gestiona todas las interacciones con SharePoint, incluyendo:
- Obtención de configuraciones
- Carga y descarga de archivos
- Gestión de imágenes y recursos
- Carga de logs del sistema

Funciones principales:
- `get_config_file()`: Obtiene archivo de configuración desde SharePoint
- `get_image_config()`: Obtiene configuración de imágenes
- `get_trafo_data()`: Obtiene datos de transformadores
- `get_tecnicos_data()`: Obtiene datos de técnicos
- `upload_log()`: Sube logs a SharePoint
- `upload_system_log()`: Sube logs del sistema a SharePoint

### TEMIS Manager (`core/temis_manager.py`)
Maneja la integración con TEMIS, incluyendo:
- Consulta de tickets existentes
- Creación de nuevos tickets
- Creación y gestión de TDCs
- Asignación de técnicos

Funciones principales:
- `consultar_ticket()`: Verifica existencia de tickets
- `crear_ticket()`: Crea nuevos tickets en TEMIS
- `crear_tdc()`: Crea nuevos TDCs
- `asignar_tecnico_tdc()`: Asigna técnicos a TDCs
- `procesar_ticket_completo()`: Gestiona el proceso completo de un ticket

### GUI Automation (`automation/gui_automation.py`)
Automatiza la interacción con GESI, incluyendo:
- Navegación por la interfaz
- Extracción de datos
- Manejo de elementos GUI

Funciones principales:
- `click_element()`: Interactúa con elementos de la interfaz
- `extract_gesi_data()`: Extrae datos de GESI
- `process_clipboard_data()`: Copia los datos al portapapeles

### Data Processor (`data/data_processor.py`)
Procesa y transforma los datos copias en el portapapeles:
- Normalización de datos
- Mapeo de campos
- Validación de información
- Aplicar filtros

Funciones principales:
- `process_gesi_data()`: Procesa datos extraídos de GESI
- `extraer_telefono()`: Extrae números telefónicos de texto

### Logger System (`utils/logger.py`)
Sistema de logging personalizado que:
- Registra operaciones del sistema
- Maneja diferentes niveles de log
- Guarda logs en archivos y SharePoint

### Configuración
Procesa y transforma los datos copias en el portapapeles:
- Carga la configuración de rutas de SharePoint
- Carga la configuración para interactuar con GESI
- Carga la configuración de las API's de TEMIS

Funciones principales:
- `load_config()`: Carga la configuración desde SharePoint

### Requisitos del Sistema
- MAC autorizada: ejemplo, 51-EC-F7-D7-A3-D3
- Python 3.10 o superior
- Acceso a SharePoint
- Credenciales de TEMIS

## Archivos de configuración

### Archivo de Configuración del sistema, `config.json`
El sistema utiliza un archivo `config.json` en SharePoint que contiene:
- MAC autorizada
- Configuraciones de SharePoint
- Parámetros de GESI
- Configuración de TEMIS
- Rutas de recursos

### Archivo de Configuración para intereción con GESI, `gesi_config.xlsx`
El sistema utiliza un archivo `gesi_config.xlsx` en SharePoint para la interación  con las imagenes de GESI que contiene:
- Nombre de la imagen a configurar
- Porcentaje de confian para la busqueda de la imagen
- Posición del clic en X
- Posición del clic en Y
- Descripción de la imagen

### Archivo de Configuración para el ejecutable, `GESI-TEMIS.spec`
El sistema utiliza un archivo `GESI-TEMIS.spec` para la creación del ejecutable que contiene:
- Rutas de los recursos y archivos
- Agragar imagen para icono
- Toda la configuración necesaria para la creación del ejecutable

## Uso

### Ejecución
1. El sistema verifica la MAC del equipo
2. Carga configuraciones desde SharePoint
3. Inicia la automatización de GESI
4. Procesa los tickets encontrados
5. Crea/actualiza tickets en TEMIS
6. Genera logs de la operación

### Logs
El sistema genera dos tipos de logs:
1. Logs de carga (`log_carga_temis_[timestamp].xlsx`): Detalles de la carga en TEMIS
2. Logs del sistema (`gesi_temis_[timestamp].log`): Operaciones del sistema

## Seguridad
- Validación de MAC del equipo
- Manejo seguro de credenciales
- Logs detallados de operaciones
- Control de acceso por SharePoint

## Mantenimiento
- Los recursos se mantienen en SharePoint
- Configuración centralizada
- Logs automáticos
- Sistema modular para fácil actualización

## Errores Comunes y Soluciones
1. **Error de MAC no autorizada**
   - Verificar MAC del equipo
   - Confirmar autorización

2. **Error de conexión SharePoint**
   - Verificar credenciales
   - Comprobar conexión a internet

3. **Error en automatización GESI**
   - Verificar que GESI esté abierto
   - Comprobar recursos de imágenes

4. **Error en creación de tickets TEMIS**
   - Verificar credenciales TEMIS
   - Comprobar formato de datos

## Notas Importantes
- El sistema requiere conexión a internet estable
- GESI debe estar abierto y accesible
- Las credenciales deben estar actualizadas
- Los recursos deben estar en SharePoint

## Control de Versiones
El sistema se distribuye como ejecutable compilado con PyInstaller.
Para crear una nueva versión:
```bash
pyinstaller GESI-TEMIS.spec
```

## Soporte
Para soporte técnico o reportar problemas:
1. Verificar logs del sistema
2. Comprobar configuraciones
3. Contactar al equipo de soporte

# Contacto y Soporte
Para soporte técnico o consultas, contacte a:

## <span style="font-size:24px; font-weight:bold;">AUTOMA<span style="color:red;">TIC</span></span><br><span style="font-size:15px; font-weight:normal;">automatic@inmel.co</span>

