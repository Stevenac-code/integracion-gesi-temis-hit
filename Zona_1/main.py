# main.py
import os
import sys
import psutil
from datetime import datetime
from utils.logger import CustomLogger
from core.temis_manager import TemisManager
from automation.resources import ResourceManager
from data.data_processor import GesiDataProcessor
from automation.gui_automation import GesiAutomation
from core.sharepoint_manager import SharePointManager
from config.settings import SHAREPOINT_CONFIG, TEMIS_CONFIG, SECURITY_CONFIG


# OBTENER RUTA RELATIVA
def obtener_ruta_recursos(ruta_relativa):
    """ Obtener la ruta absoluta al recurso, funciona para desarrolladores y para PyInstaller """
    try:
        # PyInstaller crea una carpeta temporal y almacena la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, ruta_relativa)


def obtener_mac_ethernet():
    """Obtiene la MAC del adaptador de Ethernet"""
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == psutil.AF_LINK:
                if "Ethernet" in interface:
                    return addr.address
    return None


def main():

    logger = CustomLogger('Main')
    
    try:

        # Inicio del programa
        logger.info("Iniciando programa de automatización GESI")

        # Inicializar SharePoint
        logger.info("Inicializando conexión con SharePoint")
        sp_manager = SharePointManager(SHAREPOINT_CONFIG)

         # Verificar MAC
        mac_address = obtener_mac_ethernet()
        logger.info(f"Verificando autorización del equipo: {mac_address}")
        if mac_address != SECURITY_CONFIG['authorized_mac']:
            logger.error("Acceso denegado: MAC no autorizada")
            raise Exception("Este equipo no está autorizado para ejecutar el programa")
        logger.info("MAC autorizada. Continuando proceso...")

        # Cargar datos maestros
        logger.info("Cargando datos maestros")
        trafo_data = sp_manager.get_trafo_data()
        tecnicos_data = sp_manager.get_tecnicos_data()

        if trafo_data is None or tecnicos_data is None:
            raise Exception("Error cargando datos maestros")

        # Inicializar Resource Manager
        logger.info("Inicializando Resource Manager")
        resource_manager = ResourceManager(sp_manager)

        # Iniciar automatización GUI
        logger.info("Iniciando automatización de GESI")
        gesi_automation = GesiAutomation(resource_manager)

        # Extraer datos de GESI
        logger.info("Comenzando extracción de datos")
        gesi_data = gesi_automation.extract_gesi_data()
        
        if gesi_data is None:
            raise Exception("Error en la extracción de datos de GESI")
            
        # Procesar datos
        logger.info("Procesando datos extraídos")
        data_processor = GesiDataProcessor(sp_manager)
        processed_data = data_processor.process_gesi_data(gesi_data, trafo_data, tecnicos_data)
        logger.info(f"Datos procesados\n{processed_data}")

        if processed_data is None or processed_data.empty:
            raise Exception("Error en el procesamiento de datos")
            
        # Inicializar manager de TEMIS
        logger.info("Iniciando integración con TEMIS")
        temis_manager = TemisManager(TEMIS_CONFIG)

        # Procesar lote de tickets
        logger.info("Procesando tickets en TEMIS")
        results_log = temis_manager.procesar_lote_tickets(processed_data)

        if results_log is not None:
            # Generar nombre para el archivo de log
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_filename = f'log_carga_temis_{timestamp}.xlsx'
            
            # Guardar log en SharePoint
            sp_manager.upload_log(results_log, log_filename)
            logger.info("Proceso completado exitosamente")
        else:
            logger.error("Error en el procesamiento de tickets")
                
    except Exception as e:
        logger.error(f"Error en la ejecución principal: {str(e)}")
        
    finally:
        try:
            # Cerrar los handlers del logger
            logger.file_handler.close()
            logger.logger.removeHandler(logger.file_handler)
            
            # Subir el log
            log_filepath = logger.get_log_file()
            if 'sp_manager' in locals():
                sp_manager.upload_system_log(log_filepath)

            # Limpiar recursos temporales
            if 'resource_manager' in locals():
                resource_manager.cleanup()
                
        except Exception as e:
            logger.error(f"Error en la finalización: {str(e)}")

if __name__ == "__main__":
   main()