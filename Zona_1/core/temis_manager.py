# core/temis_manager.py
import json
import urllib3
import requests
from datetime import datetime
from utils.logger import CustomLogger


class TemisManager:
    def __init__(self, config):
        self.config = config
        self.logger = CustomLogger('TemisManager')
        # Desactivar advertencias SSL
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
    def consultar_ticket(self, numero_ticket):
        """Consulta si un ticket existe en TEMIS"""
        try:
            self.logger.info(f"Consultando ticket {numero_ticket} en TEMIS")
            self.config['data_consulta']["fromUri"] = f"?numeroOrdenServicio={numero_ticket}&innerObjects=true&idTipoDocumento=5&innerFiles=true&searchAsLike=false"
            
            response = requests.post(
                self.config['url_consulta'], 
                json=self.config['data_consulta'], 
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                self.logger.info(f"Consulta exitosa para ticket {numero_ticket}")
                return data
            elif response.status_code == 400:
                # 400 = No encontrado, lo interpretamos como que no existe el ticket
                self.logger.warning(f"Ticket {numero_ticket} no encontrado en TEMIS (status 400).")
                return {"data": None}
            else:
                self.logger.error(f"Error consultando ticket {numero_ticket}. Status code: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error en consulta de ticket {numero_ticket}: {str(e)}")
            return None
        

    def crear_ticket(self, datos_ticket):
        """Crea un nuevo ticket en TEMIS"""
        try:
            self.logger.info(f"Creando ticket {datos_ticket['NroDocumento']} en TEMIS")
            
            data_carga = self.config['data_carga'].copy()
            data_carga["dataRequest"].update({
                "NroDocumento": datos_ticket['NroDocumento'],
                "FechaCreacion": datos_ticket['FechaCreacion'],
                "FechaDocumento": datos_ticket['FechaDocumento'],
                "Observaciones": f"Orden Rapida => Generada por el integrador GESI-TEMIS {datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}",
                "CamposAdicionales": {
                    "Atributo158": datos_ticket['Atributo158'],
                    "Atributo160": datos_ticket['Atributo160'],
                    "Atributo99": datos_ticket['Atributo99'],
                    "Atributo165": datos_ticket['Atributo165'],
                    "Atributo119": datos_ticket['Atributo119'],
                    "Atributo125": datos_ticket['Atributo125'],
                    "Atributo167": datos_ticket['Atributo167'],
                    "Atributo159": datos_ticket['Atributo159'],
                    "Atributo346": datos_ticket['Atributo346'],
                    "Atributo161": datos_ticket['Atributo161']
                },
                "FechaCarga": datos_ticket['FechaCarga'],
                "LatitudOrigen": datos_ticket['LatitudOrigen'],
                "LongitudOrigen": datos_ticket['LongitudOrigen']
            })

            # Log del payload
            self.logger.info(f"Payload ticket: {json.dumps(data_carga, indent=2)}")

            response = requests.post(
                self.config['url_carga'],
                json=data_carga,
                verify=False
            )

            response_data = response.json()
            # Log de la respuesta
            self.logger.info(f"Respuesta creación ticket: {json.dumps(response_data, indent=2)}")

            if response.status_code == 200 and response_data.get('succeeded', False):
                self.logger.info(f"Ticket {datos_ticket['NroDocumento']} creado exitosamente")
                return True
            else:
                self.logger.error(f"Error creando ticket. Status: {response.status_code}, Detalle: {response_data}")
                return False

        except Exception as e:
            self.logger.error(f"Error en creación de ticket {datos_ticket['NroDocumento']}: {str(e)}")
            return False
        

    def crear_tdc(self, datos_tdc):
        """Crea una nueva TDC en TEMIS"""
        try:
            self.logger.info(f"Creando TDC {datos_tdc['tdc']} para ticket {datos_tdc['NroDocumento']}")
            
            data_carga = self.config['data_carga'].copy()
            data_carga["dataRequest"].update({
                "NroDocumento": datos_tdc['tdc'],
                "FechaCreacion": datos_tdc['FechaCreacion'],
                "FechaDocumento": datos_tdc['FechaDocumento'],
                "Observaciones": f"Orden Rapida => Generada por el integrador GESI-TEMIS {datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}",
                "CamposAdicionales": {
                    "Atributo158": datos_tdc['Atributo158'],
                    "Atributo160": datos_tdc['Atributo160'],
                    "Atributo99": datos_tdc['NroDocumento'],  # Ticket original
                    "Atributo165": datos_tdc['Atributo165'],
                    "Atributo119": datos_tdc['Atributo119'],
                    "Atributo125": datos_tdc['Atributo125'],
                    "Atributo167": datos_tdc['Atributo167'],
                    "Atributo159": datos_tdc['Atributo159'],
                    "Atributo346": datos_tdc['Atributo346'],
                    "Atributo161": datos_tdc['Atributo161']
                },
                "FechaCarga": datos_tdc['FechaCarga'],
                "LatitudOrigen": datos_tdc['LatitudOrigen'],
                "LongitudOrigen": datos_tdc['LongitudOrigen']
            })

            # Log del payload
            self.logger.info(f"Payload TDC: {json.dumps(data_carga, indent=2)}")

            response = requests.post(
                self.config['url_carga'],
                json=data_carga,
                verify=False
            )

            response_data = response.json()
            # Log de la respuesta
            self.logger.info(f"Respuesta creación TDC: {json.dumps(response_data, indent=2)}")

            if response.status_code == 200 and response_data.get('succeeded', False):
                self.logger.info(f"TDC {datos_tdc['tdc']} creada exitosamente")
                return True
            else:
                self.logger.error(f"Error creando TDC. Status: {response.status_code}, Detalle: {response_data}")
                return False

        except Exception as e:
            self.logger.error(f"Error en creación de TDC {datos_tdc['tdc']}: {str(e)}")
            return False
        

    def asignar_tecnico_tdc(self, datos_tdc):
        """Asigna un técnico a una TDC existente manteniendo todos los datos originales"""
        try:
            self.logger.info(f"Asignando técnico {datos_tdc['IdBodegaOrigen']} a TDC {datos_tdc['tdc']}")
            
            # Primero obtener los datos actuales del TDC
            tdc_actual = self.consultar_ticket(datos_tdc['tdc'])
            
            if not tdc_actual or not tdc_actual.get('data'):
                self.logger.error(f"Error obteniendo datos actuales de TDC {datos_tdc['tdc']}")
                return False
                
            # Copiar todos los datos existentes
            data_carga = self.config['data_carga'].copy()
            
            # Mantener todos los datos originales
            data_carga["dataRequest"] = tdc_actual['data'].copy()
            
            # Solo modificar el campo IdBodegaOrigen
            data_carga["dataRequest"]["IdBodegaOrigen"] = datos_tdc['IdBodegaOrigen']

            # Agregar parametros en SubBodega
            subbodega = {
                "IdDocumento": tdc_actual['data'].get('IdDocumento', 0),
                "IdSubBodega": datos_tdc.get('IdBodegaOrigen', 0),
                "CodigoSubBodega": datos_tdc.get('CodigoSubBodega', ""),
                "FechaPersona": datos_tdc.get('FechaDocumento', "")
            }
            data_carga["dataRequest"]["SubBodegas"] = [subbodega]

            # Log del payload
            self.logger.info(f"Payload asignación: {json.dumps(data_carga, indent=2)}")

            response = requests.post(
                self.config['url_carga'],
                json=data_carga,
                verify=False
            )

            response_data = response.json()
            # Log de la respuesta
            self.logger.info(f"Respuesta asignación: {json.dumps(response_data, indent=2)}")

            if response.status_code == 200 and response_data.get('succeeded', False):
                self.logger.info(f"Técnico asignado exitosamente a TDC {datos_tdc['tdc']}")
                return True
            else:
                self.logger.error(f"Error asignando técnico. Status: {response.status_code}, Detalle: {response_data}")
                return False

        except Exception as e:
            self.logger.error(f"Error en asignación de técnico a TDC {datos_tdc['tdc']}: {str(e)}")
            return False
    

    def procesar_ticket_completo(self, datos):
        """Procesa un ticket completo: verifica, crea y asigna TDC si es necesario"""
        try:
            ticket = datos['NroDocumento']
            self.logger.info(f"Procesando ticket completo: {ticket}")

            # Consultar si existe el ticket
            respuesta_consulta = self.consultar_ticket(ticket)
            
            if respuesta_consulta.get('data') is None:
                self.logger.info(f"Ticket {ticket} no existe en TEMIS. Creando...")
                if not self.crear_ticket(datos):
                    return False
                # Actualizar respuesta_consulta después de crear el ticket
                respuesta_consulta = self.consultar_ticket(ticket)
            else:
                self.logger.info(f"Ticket {ticket} ya existe en TEMIS. Verificando TDCs...")

            # Obtener lista de TDCs para este ticket
            tdcs = datos.get('tdc')
            if tdcs and str(tdcs).strip():
                # Si hay TDCs para procesar
                tdcs_list = [str(tdcs).split('.')[0]]  # Por ahora solo uno, ajustar según necesidad
                
                for tdc in tdcs_list:
                    self.logger.info(f"Procesando TDC {tdc} para ticket {ticket}")
                    
                    # Verificar que el ticket padre exista
                    if respuesta_consulta.get('data') is None:
                        self.logger.error(f"No se puede crear TDC {tdc} - Ticket padre {ticket} no existe")
                        return False

                    # Validar campos requeridos
                    campos_requeridos = [
                        'NroDocumento', 'FechaCreacion', 'FechaDocumento', 
                        'Atributo158', 'Atributo160', 'Atributo165'
                    ]
                    
                    campos_faltantes = [campo for campo in campos_requeridos 
                                        if not datos.get(campo)]
                    
                    if campos_faltantes:
                        self.logger.error(f"Faltan campos requeridos para TDC {tdc}: {campos_faltantes}")
                        return False
                        
                    respuesta_consulta_tdc = self.consultar_ticket(tdc)
                    
                    if respuesta_consulta_tdc.get('data') is None:
                        self.logger.info(f"TDC {tdc} no existe. Creando...")
                        datos_tdc = datos.copy()
                        datos_tdc['tdc'] = tdc
                        if not self.crear_tdc(datos_tdc):
                            self.logger.error(f"Error al crear TDC {tdc}")
                            return False
                        self.logger.info(f"TDC {tdc} creada exitosamente")
                    
                    # Verificar asignación de técnico
                    respuesta_consulta_tdc = self.consultar_ticket(tdc)  # Actualizar datos TDC
                    if respuesta_consulta_tdc.get('data'):
                        # Verificar si tiene IdBodegaOrigen = 13556 o 13574 (Técnicos quemados) 13556	HIT y 13574	ANALISTA COC
                        # if respuesta_consulta_tdc['data'].get('IdBodegaOrigen') == 13380: # CUANDO ESTABA 10C ESTE ERA EL TECNICO QUEMADO
                        if respuesta_consulta_tdc['data'].get('IdBodegaOrigen') == 13556 or respuesta_consulta_tdc['data'].get('IdBodegaOrigen') == 13574:
                            self.logger.info(f"TDC {tdc} tiene IdBodegaOrigen = {respuesta_consulta_tdc['data'].get('IdBodegaOrigen')}. Se procederá a reasignar.")
                            # Borrar asignación actual
                            datos_tdc = datos.copy()
                            datos_tdc['tdc'] = tdc
                            # datos_tdc['IdBodegaOrigen'] = ""  # Borrar asignación
                            if not self.asignar_tecnico_tdc(datos_tdc):
                                return False

                        # Continuar con la verificación normal
                        if 'IdBodegaOrigen' not in respuesta_consulta_tdc['data'] or respuesta_consulta_tdc['data'].get('IdBodegaOrigen') == "":
                            codigo_tecnico = datos.get('IdBodegaOrigen', '')
                            
                            # Validar que el código comience con INMEL
                            if not str(codigo_tecnico).startswith("INMEL"):
                                self.logger.info(f"Código de técnico {codigo_tecnico} no válido para TDC {tdc}")
                                codigo_tecnico = ""
                            
                            datos_tdc = datos.copy()
                            datos_tdc['tdc'] = tdc
                            datos_tdc['IdBodegaOrigen'] = codigo_tecnico
                                
                            self.logger.info(f"Asignando técnico {codigo_tecnico} a TDC {tdc}")
                            if not self.asignar_tecnico_tdc(datos_tdc):
                                return False
                        else:
                            self.logger.info(f"TDC {tdc} ya tiene técnico asignado")
            else:
                self.logger.info(f"No hay TDCs para procesar en ticket {ticket}")

            return True

        except Exception as e:
            self.logger.error(f"Error en procesamiento del ticket {ticket}: {str(e)}")
            return False
        
        
    def procesar_lote_tickets(self, df_tickets):
        try:
            self.logger.info(f"Iniciando procesamiento de lote de {len(df_tickets)} tickets")
            
            df_log = df_tickets.copy()
            df_log['hora_proceso'] = ''
            df_log['estado_proceso'] = ''
            df_log['detalle_proceso'] = ''

            for index, row in df_tickets.iterrows():
                try:
                    hora_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    self.logger.info(f"Procesando registro {index + 1} de {len(df_tickets)}")
                    
                    ticket = row['NroDocumento']
                    tdc = str(row.get('tdc', '')).split('.')[0] if row.get('tdc') else ''

                    # Procesar el ticket
                    resultado = self.procesar_ticket_completo(row)
                    
                    df_log.at[index, 'hora_proceso'] = hora_actual
                    if resultado:
                        if tdc:
                            df_log.at[index, 'estado_proceso'] = 'EXITOSO'
                            df_log.at[index, 'detalle_proceso'] = f'Ticket {ticket} y TDC {tdc} procesados correctamente'
                        else:
                            df_log.at[index, 'estado_proceso'] = 'EXITOSO'
                            df_log.at[index, 'detalle_proceso'] = f'Ticket {ticket} procesado correctamente'
                    else:
                        respuesta_consulta = self.consultar_ticket(ticket)
                        if respuesta_consulta.get('data') is None:
                            df_log.at[index, 'estado_proceso'] = 'FALLIDO'
                            df_log.at[index, 'detalle_proceso'] = f'Error creando ticket {ticket}'
                        else:
                            df_log.at[index, 'estado_proceso'] = 'FALLIDO'
                            df_log.at[index, 'detalle_proceso'] = f'Error procesando TDC {tdc}'

                except Exception as e:
                    df_log.at[index, 'hora_proceso'] = hora_actual
                    df_log.at[index, 'estado_proceso'] = 'ERROR'
                    df_log.at[index, 'detalle_proceso'] = f'Error: {str(e)}'
                    self.logger.error(f"Error procesando registro {index + 1}: {str(e)}")

            # Resumen del procesamiento
            self._log_resumen_procesamiento(df_log, len(df_tickets))
            return df_log

        except Exception as e:
            self.logger.error(f"Error en el procesamiento del lote: {str(e)}")
            return None

    def _log_resumen_procesamiento(self, df_log, total_tickets):
        """Genera el resumen del procesamiento"""
        total_exitosos = len(df_log[df_log['estado_proceso'] == 'EXITOSO'])
        total_fallidos = len(df_log[df_log['estado_proceso'] == 'FALLIDO'])
        total_errores = len(df_log[df_log['estado_proceso'] == 'ERROR'])

        self.logger.info("Procesamiento de lote finalizado:")
        self.logger.info(f"Total procesados: {total_tickets}")
        self.logger.info(f"Exitosos: {total_exitosos}")
        self.logger.info(f"Fallidos: {total_fallidos}")
        self.logger.info(f"Errores: {total_errores}")