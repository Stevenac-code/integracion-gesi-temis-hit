# utils/logger.py
import os
import sys
import logging
from datetime import datetime


class CustomLogger:
    def __init__(self, name):
        # Crear directorio de logs si no existe
        # self.log_dir = 'logs'
        self.log_dir = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'logs')
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # Configurar el logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Crear nombre de archivo con timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H')
        self.log_filename = f'gesi_temis_{timestamp}.log'
        self.log_filepath = os.path.join(self.log_dir, self.log_filename)

        # Configurar el manejador de archivo
        self.file_handler = logging.FileHandler(self.log_filepath, encoding='utf-8')
        self.file_handler.setLevel(logging.INFO)

        # Configurar el manejador de consola
        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(logging.INFO)

        # Crear formato
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(formatter)
        self.console_handler.setFormatter(formatter)

        # Agregar handlers
        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.console_handler)

    def get_log_file(self):
        """Retorna la ruta completa del archivo de log"""
        return self.log_filepath

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def warning(self, message):
        self.logger.warning(message)

    def debug(self, message):
        self.logger.debug(message)
