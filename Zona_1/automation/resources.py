# src/automation/resources.py
import os
import tempfile


class ResourceManager:
    def __init__(self, sharepoint_manager):
        self.sp_manager = sharepoint_manager
        self.temp_dir = tempfile.mkdtemp()
        self.resources = {}

    def get_resource_path(self, resource_name):
        """Obtiene la ruta temporal de un recurso"""
        return self.resources.get(resource_name)
    

    def cleanup(self):
        """Limpia los archivos temporales"""
        for path in self.resources.values():
            if os.path.exists(path):
                os.remove(path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)