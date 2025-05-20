# core/sharepoint_manager.py
import io
import os
import requests
import pandas as pd
from PIL import Image
from shareplum import Office365
from utils.logger import CustomLogger


class SharePointManager:
    def __init__(self, config):
        self.config = config
        self._auth_cookie = None
        self._session = None
        self.logger = CustomLogger('SharePointManager')
        
    def connect(self):
        """Establece la conexión con SharePoint"""
        try:
            self.logger.info("Iniciando conexión con SharePoint...")
            authcookie = Office365(
                self.config['sp_base_url'],
                username=self.config['sp_username'],
                password=self.config['sp_password']
            ).GetCookies()
            
            session = requests.Session()
            session.cookies = authcookie
            session.headers.update({
                'user-agent': 'python_bite/v1',
                'accept': 'application/json;odata=verbose'
            })
            
            self._session = session
            self._auth_cookie = authcookie
            self.logger.info("Conexión establecida exitosamente con SharePoint")
            return True
            
        except Exception as e:
            self.logger.error(f"Error conectando a SharePoint: {str(e)}")
            return False


    def get_coords_config(self):
        """Obtiene la configuración de coordenadas desde SharePoint"""
        try:
            config_path = f"{self.config['sp_configs_folder']}/gesi_config_coords.xlsx"
            response = self._session.get(f"{self.config['sp_base_url']}/sites/{self.config['sp_site_name']}/_api/web/GetFileByServerRelativeUrl('{config_path}')/\$value")
            
            if response.status_code == 200:
                df = pd.read_excel(io.BytesIO(response.content), sheet_name="Coordenadas")
                # Convertir a diccionario
                return df.set_index('element_name').to_dict(orient='index')
            return None
        except Exception as e:
            self.logger.error(f"Error obteniendo configuración de coordenadas: {str(e)}")
            return None

    def get_times_config(self):
        """Obtiene la configuración de tiempos desde SharePoint"""
        try:
            config_path = f"{self.config['sp_configs_folder']}/gesi_config_coords.xlsx"
            response = self._session.get(f"{self.config['sp_base_url']}/sites/{self.config['sp_site_name']}/_api/web/GetFileByServerRelativeUrl('{config_path}')/\$value")
            
            if response.status_code == 200:
                df = pd.read_excel(io.BytesIO(response.content), sheet_name="Tiempos")
                # Convertir a diccionario
                return df.set_index('action').to_dict(orient='index')
            return None
        except Exception as e:
            self.logger.error(f"Error obteniendo configuración de tiempos: {str(e)}")
            return None
        
    def get_areas_of_interest(self):
        """Obtiene la configuración de áreas desde SharePoint"""
        try:
            config_path = f"{self.config['sp_configs_folder']}/gesi_config_coords.xlsx"
            response = self._session.get(f"{self.config['sp_base_url']}/sites/{self.config['sp_site_name']}/_api/web/GetFileByServerRelativeUrl('{config_path}')/\$value")
            
            if response.status_code == 200:
                df = pd.read_excel(io.BytesIO(response.content), sheet_name="Areas")
                # Convertir a lista la columna 'areas_of_interest'
                return df['areas_of_interest'].tolist()
            return None
        except Exception as e:
            self.logger.error(f"Error obteniendo lista de áreas: {str(e)}")
            return None

    def get_trafo_data(self):
        """Lee el archivo de transformadores desde SharePoint"""
        if not self._session:
            if not self.connect():
                return None
        try:
            self.logger.info("Obteniendo datos de transformadores desde SharePoint")
            ruta_archivo = f"{self.config['sp_resources_folder']}/Trafos.xlsx"
            
            response = self._session.get(
                f"{self.config['sp_base_url']}/sites/{self.config['sp_site_name']}/_api/web/GetFileByServerRelativeUrl('{ruta_archivo}')/\$value"
            )
            
            if response.status_code == 200:
                contenido_archivo = io.BytesIO(response.content)
                df_transformadores = pd.read_excel(contenido_archivo)
                self.logger.info(f"Datos de transformadores cargados exitosamente. {len(df_transformadores)} registros obtenidos")
                return df_transformadores
            else:
                self.logger.error(f"Error al obtener archivo de transformadores. Status code: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error procesando archivo de transformadores: {str(e)}")
            return None

    def get_tecnicos_data(self):
        """Lee el archivo de técnicos desde SharePoint"""
        if not self._session:
            if not self.connect():
                return None
        try:
            self.logger.info("Obteniendo datos de técnicos desde SharePoint")
            ruta_archivo = f"{self.config['sp_resources_folder']}/Tecnicos.xlsx"
            
            response = self._session.get(
                f"{self.config['sp_base_url']}/sites/{self.config['sp_site_name']}/_api/web/GetFileByServerRelativeUrl('{ruta_archivo}')/\$value"
            )
            
            if response.status_code == 200:
                contenido_archivo = io.BytesIO(response.content)
                df_tecnicos = pd.read_excel(contenido_archivo)
                self.logger.info(f"Datos de técnicos cargados exitosamente. {len(df_tecnicos)} registros obtenidos")
                return df_tecnicos
            else:
                self.logger.error(f"Error al obtener archivo de técnicos. Status code: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error procesando archivo de técnicos: {str(e)}")
            return None

    def get_neighborhoods(self):
        """Obtiene la configuración de barrios desde SharePoint"""
        try:
            config_path = f"{self.config['sp_configs_folder']}/gesi_config_coords.xlsx"
            response = self._session.get(f"{self.config['sp_base_url']}/sites/{self.config['sp_site_name']}/_api/web/GetFileByServerRelativeUrl('{config_path}')/\$value")
            
            if response.status_code == 200:
                df = pd.read_excel(io.BytesIO(response.content), sheet_name="Barrios")
                # Convertir a lista la columna 'areas_of_interest'
                return df['neighborhoods'].tolist()
            return None
        except Exception as e:
            self.logger.error(f"Error obteniendo lista de barrios: {str(e)}")
            return None

    def upload_log(self, df_log, file_name):
        """Sube un DataFrame como archivo Excel a SharePoint"""
        try:
            self.logger.info(f"Subiendo archivo de log: {file_name}")
            # Convertir DataFrame a bytes
            excel_buffer = io.BytesIO()
            df_log.to_excel(excel_buffer, index=False)
            excel_buffer.seek(0)
            
            # Obtener el token X-RequestDigest
            digest_url = f"{self.config['sp_base_url']}/sites/{self.config['sp_site_name']}/_api/contextinfo"
            digest_response = self._session.post(digest_url)
            if digest_response.status_code != 200:
                self.logger.error("No se pudo obtener el token")
                return False
                
            form_digest_value = digest_response.json()['d']['GetContextWebInformation']['FormDigestValue']
            
            # Actualizar headers con el token
            self._session.headers.update({
                'X-RequestDigest': form_digest_value,
                'accept': 'application/json;odata=verbose',
                'content-type': 'application/json;odata=verbose'
            })

            # Construir URL para subir archivo
            url = f"{self.config['sp_base_url']}/sites/{self.config['sp_site_name']}/_api/web/GetFolderByServerRelativeUrl('{self.config['sp_temis_load_logs_folder']}')/Files/add(url='{file_name}',overwrite=true)"
            
            response = self._session.post(
                url,
                data=excel_buffer.getvalue(),
                headers={'content-type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}
            )
            
            if response.status_code == 200:
                self.logger.info(f"Log {file_name} subido exitosamente")
                return True
            else:
                self.logger.error(f"Error subiendo log. Status code: {response.status_code}")
                if response.text:
                    self.logger.error(f"Detalles del error: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error en la carga del log: {str(e)}")
            return False
        


    def get_config_file(self, filename):
        """Obtiene el archivo de configuración desde SharePoint"""
        try:
            self.logger.info(f"Obteniendo archivo de configuración: {filename}")
            config_path = f"{self.config['sp_resources_folder']}/{filename}"
            
            if not self._session:
                if not self.connect():
                    return None

            response = self._session.get(
                f"{self.config['sp_base_url']}/sites/{self.config['sp_site_name']}/_api/web/GetFileByServerRelativeUrl('{config_path}')/\$value"
            )
            
            if response.status_code == 200:
                self.logger.info("Configuración cargada exitosamente")
                return response.text
            else:
                self.logger.error(f"Error obteniendo configuración. Status: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error leyendo archivo de configuración: {str(e)}")
            return None
        

    
    def upload_system_log(self, log_filepath):
        """Sube el archivo de log del sistema a SharePoint"""
        try:
            if not self._session:
                if not self.connect():
                    return False

            log_filename = os.path.basename(log_filepath)
            self.logger.info(f"Subiendo log del sistema: {log_filename}")
            
            # Obtener el request digest
            digest_url = f"{self.config['sp_base_url']}/sites/{self.config['sp_site_name']}/_api/contextinfo"
            digest_response = self._session.post(digest_url)
            if digest_response.status_code == 200:
                request_digest = digest_response.json()['d']['GetContextWebInformation']['FormDigestValue']
                self._session.headers.update({'X-RequestDigest': request_digest})
            
            with open(log_filepath, 'rb') as file:
                log_content = file.read()
                
            url = f"{self.config['sp_base_url']}/sites/{self.config['sp_site_name']}/_api/web/GetFolderByServerRelativeUrl('{self.config['sp_system_logs_folder']}')/Files/add(url='{log_filename}',overwrite=true)"
            
            response = self._session.post(url, data=log_content)
            
            if response.status_code == 200:
                self.logger.info(f"Log del sistema {log_filename} subido exitosamente")
                return True
            else:
                self.logger.error(f"Error subiendo log del sistema. Status code: {response.status_code}")
                self.logger.error(f"Respuesta: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error en la carga del log del sistema: {str(e)}")
            return False