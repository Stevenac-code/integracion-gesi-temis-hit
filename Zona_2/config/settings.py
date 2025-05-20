# config/settings.py
import json
from core.sharepoint_manager import SharePointManager

def load_config():
    """Carga la configuración desde SharePoint"""
    # Configuración mínima para conectar a SharePoint
    BASE_CONFIG = {
        'sp_base_url': 'https://inmelingenieria.sharepoint.com',
        'sp_site_name': 'Analytics-0018-TICPrincipal',
        'sp_resources_folder': '/sites/Analytics-0018-TICPrincipal/Documentos compartidos/0018 - TIC Principal/GESI/PC_Zona_2/Configuraciones',
        'sp_username': 'bi.admin@inmel.co',
        'sp_password': 'tFC+Bqig.b47M'
    }

    sp_manager = SharePointManager(BASE_CONFIG)
    config_content = sp_manager.get_config_file('config.json')
    
    if not config_content:
        raise Exception("No se pudo cargar la configuración desde SharePoint")
        
    config = json.loads(config_content)
    # Agregar credenciales a la configuración de SharePoint
    config['sharepoint']['sp_username'] = BASE_CONFIG['sp_username']
    config['sharepoint']['sp_password'] = BASE_CONFIG['sp_password']
    
    return {
        'SHAREPOINT_CONFIG': config['sharepoint'],
        'GESI_CONFIG': config['gesi'],
        'TEMIS_CONFIG': config['temis'],
        'SECURITY_CONFIG': config['security']
    }

# Cargar configuración
config = load_config()

# Exportar configuraciones
SHAREPOINT_CONFIG = config['SHAREPOINT_CONFIG']
GESI_CONFIG = config['GESI_CONFIG']
TEMIS_CONFIG = config['TEMIS_CONFIG']
SECURITY_CONFIG = config['SECURITY_CONFIG']