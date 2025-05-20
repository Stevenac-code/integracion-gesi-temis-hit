# automation/gui_automation.py
import time
import json
import keyboard
import pyautogui
import pyperclip
import pandas as pd
from utils.logger import CustomLogger
from config.settings import GESI_CONFIG

class GesiAutomation:
   def __init__(self, resource_manager):
       self.resource_manager = resource_manager
       self.coords_config = resource_manager.sp_manager.get_coords_config()
       self.logger = CustomLogger('GesiAutomation')
       self.wait_time = GESI_CONFIG['wait_time']

   def click_element(self, element_name, description=""):
       """Click en un elemento usando coordenadas configuradas"""
       try:
           self.logger.info(f"Intentando click en {description or element_name}")
           
           if element_name not in self.coords_config:
               raise Exception(f"No se encontró configuración para {element_name}")
               
           config = self.coords_config[element_name]
           pyautogui.click(x=config['coord_x'], y=config['coord_y'])
           time.sleep(self.wait_time['between_actions'])
           self.logger.info(f"Click exitoso en {description or element_name}")
           return True
               
       except Exception as e:
           self.logger.error(f"Error al hacer click en {description or element_name}: {str(e)}")
           return False

   def right_click_element(self, element_name, description=""):
       """Click derecho en un elemento usando coordenadas configuradas"""
       try:
           self.logger.info(f"Intentando click derecho en {description or element_name}")
           
           if element_name not in self.coords_config:
               raise Exception(f"No se encontró configuración para {element_name}")
               
           config = self.coords_config[element_name]
           pyautogui.rightClick(x=config['coord_x'], y=config['coord_y'])
           self.logger.info(f"Click derecho exitoso en {description or element_name}")
           return True
               
       except Exception as e:
           self.logger.error(f"Error al hacer click derecho en {description or element_name}: {str(e)}")
           return False

   def click_element_with_fallback(self, primary_element, fallback_element, description=""):
       """Intenta click con elemento principal, si falla usa elemento de respaldo"""
       if self.click_element(primary_element, description):
           return True
       return self.click_element(fallback_element, description)

   def extract_gesi_data(self):
        """Extrae los datos de GESI siguiendo el flujo de automatización"""
        try:
            self.logger.info("Iniciando extracción de datos de GESI")
            
            # Paso 1: Click inicial y refresh
            self.logger.info("Haciendo click en el costado de la página")
            self.click_element("clic_lateral", "Costado de la página")
            time.sleep(0.5)
            
            self.logger.info("Actualizando página")
            keyboard.press_and_release('F5')
            time.sleep(self.wait_time['page_load'])
            
            # Paso 2: Secuencia inicial
            if not self.click_element("buscar_area", "Filtro de búsqueda"):
                raise Exception("Falló click en filtro")
            time.sleep(self.wait_time['between_actions'])
                
            if not self.click_element("seleccionar_todos", "Botón Seleccionar Todos"):
                raise Exception("Falló click en seleccionar todo")
            time.sleep(self.wait_time['between_actions'])
                
            if not self.click_element("actualizar_1", "Primer botón Actualizar"):
                raise Exception("Falló primer actualizar")
            time.sleep(self.wait_time['after_refresh'])

            # Paso 3: Preparación herramientas desarrollador
            self.click_element("clic_lateral", "Costado de la página")
            time.sleep(self.wait_time['between_actions'])
            
            self.logger.info("Abriendo herramientas de desarrollo")
            keyboard.press_and_release('F12')
            time.sleep(self.wait_time['page_load'])

            # Paso 4: Secuencia Network
            if not self.click_element("console", "Botón de consola"):
                raise Exception("Falló click en consola")
            time.sleep(self.wait_time['between_actions'])

            if not self.click_element_with_fallback("network_b", "network_g", "Pestaña Network"):
                raise Exception("Falló click en network")
            time.sleep(self.wait_time['between_actions'])

            if not self.click_element("actualizar_2", "Segundo botón Actualizar"):
                raise Exception("Falló segundo actualizar")
            time.sleep(self.wait_time['after_refresh'])

            # Paso 5: Obtener datos 
            # Click derecho en pagination
            if not self.right_click_element("pagination", "Botón de paginación"):
                raise Exception("Falló click derecho en pagination")
            time.sleep(self.wait_time['between_actions'])

            if not self.click_element("copy", "Botón Copiar"):
                raise Exception("Falló click en copiar")
            time.sleep(self.wait_time['between_actions'])

            if not self.click_element("copy_response", "Botón Copiar Respuesta"):
                raise Exception("Falló click en copiar respuesta")
            time.sleep(self.wait_time['between_actions'])

            # Paso 6: Finalización
            self.logger.info("Cerrando herramientas de desarrollo")
            keyboard.press_and_release('F12')
            time.sleep(self.wait_time['between_actions'])
            
            return self._process_clipboard_data()

        except Exception as e:
            self.logger.error(f"Error en la extracción de datos: {str(e)}")
            return None
        

   def _process_clipboard_data(self):
        """Procesa los datos del portapapeles"""
        self.logger.info("Procesando datos del portapapeles")
        clipboard_content = pyperclip.paste()
        
        try:
            data = json.loads(clipboard_content)
            self.logger.info("JSON leído exitosamente")
            documento_GESI = pd.json_normalize(data['data'])
            self.logger.info(f"DataFrame creado con {len(documento_GESI)} registros")
            return documento_GESI
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Error al parsear el JSON: {str(e)}")
            return None