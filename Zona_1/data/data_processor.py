# data/data_processor.py
import re
import pytz
import numpy as np
import pandas as pd
from datetime import datetime
from utils.logger import CustomLogger


class GesiDataProcessor:
   def __init__(self, sharepoint_manager):
       self.sp_manager = sharepoint_manager
       self.barrios = self.sp_manager.get_neighborhoods()
       self.logger = CustomLogger('DataProcessor')

   def extraer_telefono(self, text):
       """Extrae números telefónicos del texto"""
       pattern = r'\b3\d{9}\b'  # Busca números que empiezan con 3 seguidos de 9 dígitos
       matches = re.findall(pattern, str(text))
       return matches[0] if matches else None
       
   def process_gesi_data(self, documento_GESI, trafo_coordenadas, codigo_tecnicos):
       """Procesa los datos extraídos de GESI con la información de trafos y técnicos"""
       try:
           self.logger.info("Iniciando procesamiento de datos de GESI")
           
           # Preparar datos para el cruce
           self.logger.info("Preparando datos para cruce con transformadores")
           trafo_coordenadas['network.cd.description'] = trafo_coordenadas['network.cd.description'].astype(str)
           documento_GESI['network.cd.description'] = documento_GESI['network.cd.description'].astype(str)
           
           # Cruce con coordenadas de transformadores
           self.logger.info("Realizando cruce con coordenadas de transformadores")
           resultado = pd.merge(
               documento_GESI, 
               trafo_coordenadas[['network.cd.description', 'Coordenadas']], 
               on='network.cd.description', 
               how='left'
           )
           
           # Procesar coordenadas
           resultado[['LatitudOrigen', 'LongitudOrigen']] = resultado['Coordenadas'].str.split(',', expand=True)
           resultado[['LatitudOrigen', 'LongitudOrigen']] = resultado[['LatitudOrigen', 'LongitudOrigen']].replace([None, ''], np.nan)
           resultado[['LatitudOrigen', 'LongitudOrigen']] = resultado[['LatitudOrigen', 'LongitudOrigen']].fillna(1)
           
           self.logger.info("Coordenadas de transformadores procesadas")
           
           # Cruce con códigos de técnicos
           self.logger.info("Realizando cruce con códigos de técnicos")
           codigo_tecnicos['workGroupCod'] = codigo_tecnicos['workGroupCod'].astype(str)
           resultado['workGroupCod'] = resultado['workGroupCod'].astype(str)
           
           resultado = pd.merge(
               resultado, 
               codigo_tecnicos[['workGroupCod', 'IdBodegaOrigen', 'CodigoSubBodega']], 
               on='workGroupCod', 
               how='left'
           )
           
           self.logger.info("Códigos de técnicos procesados")

           # Procesar fechas y zonas horarias
           self.logger.info("Procesando fechas y zonas horarias")
           
           # Hora UTC
           resultado['FECHA_HORA_TICKET_UTC'] = pd.to_datetime(resultado['startDate'], unit='ms', utc=True)
           resultado['FECHA_EVENTO_UTC'] = resultado['FECHA_HORA_TICKET_UTC'].dt.date
           resultado['FECHA_EVENTO_UTC'] = resultado['FECHA_EVENTO_UTC'].apply(
               lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else None
           )
           resultado['HORA_EVENTO_UTC'] = resultado['FECHA_HORA_TICKET_UTC'].dt.time
           resultado['FechaCreacion'] = resultado['FECHA_EVENTO_UTC'] + ' ' + resultado['HORA_EVENTO_UTC'].astype(str)

           # Hora zona horaria local
           desired_tz = pytz.timezone('America/Bogota')
           resultado['FECHA_HORA_TICKET_ZH'] = pd.to_datetime(resultado['startDate'], unit='ms', utc=True).dt.tz_convert(desired_tz).dt.tz_localize(None)
           resultado['FECHA_EVENTO_ZH'] = resultado['FECHA_HORA_TICKET_ZH'].dt.date
           resultado['FECHA_EVENTO_ZH'] = resultado['FECHA_HORA_TICKET_ZH'].apply(
               lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else None
           )
           resultado['HORA_EVENTO_ZH'] = resultado['FECHA_HORA_TICKET_ZH'].dt.time
           resultado['FECHA_EVENTO_ZH'] = resultado['FECHA_EVENTO_ZH'].astype(str)
           resultado['HORA_EVENTO_ZH'] = resultado['HORA_EVENTO_ZH'].astype(str)
           resultado['FechaDocumento'] = resultado['FECHA_EVENTO_ZH'] + ' ' + resultado['HORA_EVENTO_ZH']

           self.logger.info("Fechas y zonas horarias procesadas")

           # Aplicar filtros específicos
           self.logger.info("Aplicando filtros específicos")
           resultado['cft'] = resultado['cft'].str.replace(r'^[^.]*\.', '', regex=True)
           
           self.logger.info(f"Barrios de interés a filtrar: {self.barrios}")
           resultado = resultado[resultado['cft'].str.contains('|'.join(self.barrios), case=False, na=False)]
           
           # Filtrar por tensión BT
           resultado_filtrado = resultado[resultado['tensionLevel.shortDescription'] == 'BT']

           # Procesar teléfonos
           self.logger.info("Procesando números telefónicos")
           # Obtener fecha y hora actual
           fecha_hora_actual = datetime.now()
           # Extraer cada componente
           # anio = f"{fecha_hora_actual.year}"
           mes = f"{fecha_hora_actual.month:02d}"
           dia = f"{fecha_hora_actual.day:02d}"
           hora = f"{fecha_hora_actual.hour:02d}"
           minuto = f"{fecha_hora_actual.minute:02d}"
           segundo = f"{fecha_hora_actual.second:02d}"
           # milesimas = f"{fecha_hora_actual.microsecond:06d}"
           # Construir el ID de numero telefonico vacio
           id_numero_telefonico_vacio = f"{mes}{dia}{hora}{minuto}{segundo}"
           resultado_filtrado['commentCc'] = resultado_filtrado['commentCc'].astype(str)
           resultado_filtrado['Atributo159'] = resultado_filtrado['commentCc'].apply(self.extraer_telefono)
           resultado_filtrado['Atributo159'] = resultado_filtrado['Atributo159'].replace([None, ''], np.nan)
           # resultado_filtrado['Atributo159'] = resultado_filtrado['Atributo159'].fillna(1)
           resultado_filtrado['Atributo159'] = resultado_filtrado['Atributo159'].fillna(id_numero_telefonico_vacio)

           # Agregar columnas adicionales
           resultado_filtrado['Atributo167'] = 'CLIENTE'
           resultado_filtrado['Atributo346'] = 'NOTA'
           resultado_filtrado['FechaCarga'] = resultado_filtrado['FechaDocumento']
           resultado_filtrado['FechaFinalEjecucion'] = resultado_filtrado['FechaDocumento']
           resultado_filtrado['numTicket_2'] = resultado_filtrado['numTicket']
           resultado_filtrado['tdc'] = resultado_filtrado['tdc'].fillna("")
           resultado_filtrado['workGroupCod'] = resultado_filtrado['workGroupCod'].astype(str)
           resultado_filtrado['IdBodegaOrigen'] = resultado_filtrado['IdBodegaOrigen'].fillna(0).astype(int)

           # Renombrar columnas
           self.logger.info("Renombrando columnas")
           nuevo_nombres = {
               'numTicket': 'NroDocumento',
               'ticketType.shortDescription': 'Atributo158',
               'cft': 'Atributo160',
               'numTicket_2': 'Atributo99',
               'network.cd.description': 'Atributo165',
               'network.line.description': 'Atributo119',
               'localAdress': 'Atributo125',
               'commentCc': 'Atributo161'
           }
           resultado_filtrado = resultado_filtrado.rename(columns=nuevo_nombres)

           # Procesamiento final de columnas
           resultado_filtrado['Atributo165'] = resultado_filtrado['Atributo165'].fillna('NA')
           resultado_filtrado['Atributo119'] = resultado_filtrado['Atributo119'].replace([None, ''], np.nan)
           resultado_filtrado['Atributo119'] = resultado_filtrado['Atributo119'].fillna('NA')

           # Seleccionar columnas finales
           columnas_finales = [
               'NroDocumento', 'tdc', 'workGroupCod', 'IdBodegaOrigen',
               'FechaCreacion', 'FechaDocumento', 'Atributo158', 'Atributo160',
               'Atributo99', 'Atributo165', 'Atributo119', 'Atributo125',
               'Atributo167', 'Atributo159', 'Atributo346', 'Atributo161',
               'FechaCarga', 'FechaFinalEjecucion', 'LatitudOrigen', 'LongitudOrigen'
           ]

           resultado_final = resultado_filtrado[columnas_finales]
           self.logger.info(f"Procesamiento completado. Registros finales: {len(resultado_final)}")
           
           return resultado_final
           
       except Exception as e:
           self.logger.error(f"Error en el procesamiento de datos: {str(e)}")
           return None