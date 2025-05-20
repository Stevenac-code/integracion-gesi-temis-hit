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
       self.times_config = resource_manager.sp_manager.get_times_config()
       # Definir tiempos de espera
       self.page_load = float(self.times_config['page_load']['wait_time'])
       self.between_actions = float(self.times_config['between_actions']['wait_time'])
       self.after_refresh = float(self.times_config['after_refresh']['wait_time'])
       self.between_areas = float(self.times_config['between_areas']['wait_time'])
       # Definir lista de áreas
       self.areas_of_interest = self.resource_manager.sp_manager.get_areas_of_interest()
       self.logger = CustomLogger('GesiAutomation')

   def click_element(self, element_name, description=""):
       """Click en un elemento usando coordenadas configuradas"""
       try:
           self.logger.info(f"Intentando click en {description or element_name}")
           
           if element_name not in self.coords_config:
               raise Exception(f"No se encontró configuración para {element_name}")
               
           config = self.coords_config[element_name]
           pyautogui.click(x=config['coord_x'], y=config['coord_y'])
           self.logger.info(f"Click exitoso en {description or element_name}")
           return True
               
       except Exception as e:
           self.logger.error(f"Error al hacer click en {description or element_name}: {str(e)}")
           return False
       
   def double_click_element(self, element_name, description=""):
       """Doble click en un elemento usando coordenadas configuradas"""
       try:
           self.logger.info(f"Intentando click en {description or element_name}")
           
           if element_name not in self.coords_config:
               raise Exception(f"No se encontró configuración para {element_name}")
               
           config = self.coords_config[element_name]
           pyautogui.doubleClick(x=config['coord_x'], y=config['coord_y'])
           self.logger.info(f"Doble click exitoso en {description or element_name}")
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
       
   def write_element_text(self, element_name, value_key='valor', description=""):
        """
        Escribe el texto configurado en el elemento especificado.
        value_key: clave del valor a escribir en la config (por defecto 'valor')
        """
        try:
            if element_name not in self.coords_config:
                raise Exception(f"No se encontró configuración para {element_name}")
            config = self.coords_config[element_name]
            valor = config.get(value_key)
            if valor is None:
                raise Exception(f"No se encontró el valor '{value_key}' en la configuración de {element_name}")
            self.logger.info(f"Escribiendo '{valor}' en {description or element_name}")
            pyautogui.write(str(valor))
            self.logger.info(f"Texto '{valor}' escrito correctamente en {description or element_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error al escribir texto en {description or element_name}: {str(e)}")
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

            # Paso 1: Click inicial
            self.logger.info("Haciendo click en el costado de la página")
            self.click_element("clic_lateral", "Costado de la página")
            time.sleep(self.between_actions)
            
            # Paso 2: Refrescar la página
            self.logger.info("Actualizando página")
            keyboard.press_and_release('F5')
            time.sleep(self.page_load)

            # Paso 3: Enviar clic al filtro de hora
            if not self.click_element("filtrar_hora", "Enviar clic filtro de hora"):
                raise Exception("Falló click en filtro de hora")
            time.sleep(self.between_actions)

            # Paso 4: Click en el campo de hora
            if not self.double_click_element("hora", "Enviar clic a hora"):
                raise Exception("Falló click en hora")
            time.sleep(self.between_actions)

            # Paso 5: Escribir 00 en el campo de hora
            try:
                self.logger.info("Escribiendo 00 en filtro hora")
                # pyautogui.write("00")
                if not self.write_element_text("hora", value_key="value", description="filtro hora"):
                    raise Exception("Fallo al escribir valor en filtro de hora")
                time.sleep(self.between_actions)
            except Exception as e:
                self.logger.error(f"Fallo al escribir 00 en filtro hora: {e}")
                raise Exception("Fallo al escribir 00 en filtro de hora") from e
            
            # Paso 6: Enviar clic al filtro de minuto            
            if not self.double_click_element("minuto", "Enviar clic a minuto"):
                raise Exception("Falló click en minuto")
            time.sleep(self.between_actions)

            # Paso 7: Escribir 00 en el campo de minuto
            try:
                self.logger.info("Escribiendo 00 en filtro minuto")
                if not self.write_element_text("minuto", value_key="value", description="filtro minuto"):
                    raise Exception("Fallo al escribir valor en filtro de minuto")
                time.sleep(self.between_actions)
            except Exception as e:
                self.logger.error(f"Fallo al escribir 00 en filtro minuto: {e}")
                raise Exception("Fallo al escribir 00 en filtro minuto") from e            

            # Paso 8: Click en la flechita de Áreas Competencia
            if not self.click_element("buscar_area", "Filtro de búsqueda"):
                raise Exception("Falló click en filtro")
            time.sleep(self.between_actions)

            # Paso 9: Escribir texto en el campo de búsqueda
            self.logger.info(f"Áres de interés a buscar: {self.areas_of_interest}")
            for area in self.areas_of_interest:
                # Click en el campo de búsqueda
                if not self.double_click_element("busqueda", f"Campo de texto búsqueda, Área: {area}"):
                    raise Exception("Falló click en campo de texto búsqueda")
                # time.sleep(0.5)
                if not self.click_element("busqueda", f"Campo de texto búsqueda, Área: {area}"):
                    raise Exception("Falló click en campo de texto búsqueda")                
                # Borrar texto
                pyautogui.press('backspace')
                # Escriber el área de interés
                pyautogui.write(area)
                time.sleep(self.between_areas)
                # Click en el área de interés
                if not self.click_element("seleccionar_area", f"Seleccionar area especifica para filtrar, Área: {area}"):
                    raise Exception("Falló click en seleccionar area especifica para filtrar")
            
            # Paso 10: Click en el primer botón de actualizar
            if not self.click_element("actualizar_1", "Primer botón Actualizar"):
                raise Exception("Falló primer actualizar")
            time.sleep(self.after_refresh)

            # Paso 11: Preparación herramientas desarrollador, click costado de la página
            self.click_element("clic_lateral", "Costado de la página")
            time.sleep(self.between_actions)

            # Paso 12: Abrir herramientas de desarrollo            
            self.logger.info("Abriendo herramientas de desarrollo")
            keyboard.press_and_release('F12')
            time.sleep(self.page_load)

            # Paso 13: Secuencia Network, click en consola
            if not self.click_element("console", "Botón de consola"):
                raise Exception("Falló click en consola")
            time.sleep(self.between_actions)

            # Paso 14: Click en la pestaña Network
            if not self.click_element_with_fallback("network_b", "network_g", "Pestaña Network"):
                raise Exception("Falló click en network")
            time.sleep(self.between_actions)

            # Paso 15: Click en el segundo botón de Actualizar
            if not self.click_element("actualizar_2", "Segundo botón Actualizar"):
                raise Exception("Falló segundo actualizar")
            time.sleep(self.after_refresh)

            # Paso 16: Obtener datos, click derecho en pagination
            if not self.right_click_element("pagination", "Botón de paginación"):
                raise Exception("Falló click derecho en pagination")
            time.sleep(self.between_actions)

            # Paso 17: Click en Copy
            if not self.click_element("copy", "Botón Copiar"):
                raise Exception("Falló click en copiar")
            time.sleep(self.between_actions)

            # Paso 18: Click en el botón de copy_response
            if not self.click_element("copy_response", "Botón Copiar Respuesta"):
                raise Exception("Falló click en copiar respuesta")
            time.sleep(self.between_actions)

            # Paso 19: Finalización, cerrar herramientas de desarrollo
            self.logger.info("Cerrando herramientas de desarrollo")
            keyboard.press_and_release('F12')
            time.sleep(self.between_actions)
            
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