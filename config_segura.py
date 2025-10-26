"""
Módulo para manejo seguro de configuración
"""

import json
from pathlib import Path
from cryptography.fernet import Fernet
import base64
import hashlib


class ConfigSegura:
    def __init__(self):
        self.config_dir = Path.home() / '.extractor_bancario'
        self.config_dir.mkdir(exist_ok=True)
        
        self.config_file = self.config_dir / 'config.enc'
        self.key_file = self.config_dir / 'key.key'
        
        # Generar o cargar clave de encriptación
        if not self.key_file.exists():
            self._generar_clave()
        
        self.cipher = self._cargar_cipher()
    
    def _generar_clave(self):
        """Genera una clave de encriptación única para este equipo"""
        # Usar una combinación del usuario y un salt fijo para generar la clave
        import os
        usuario = os.getenv('USER', 'default')
        salt = b'extractor_bancario_v1'
        
        # Generar clave derivada
        kdf_key = hashlib.pbkdf2_hmac('sha256', usuario.encode(), salt, 100000)
        key = base64.urlsafe_b64encode(kdf_key)
        
        # Guardar clave
        self.key_file.write_bytes(key)
        # Hacer el archivo solo lectura para el usuario
        self.key_file.chmod(0o600)
    
    def _cargar_cipher(self):
        """Carga el cipher para encriptar/desencriptar"""
        key = self.key_file.read_bytes()
        return Fernet(key)
    
    def guardar(self, api_key, password, carpeta):
        """Guarda la configuración encriptada"""
        config = {
            'api_key': api_key,
            'password': password,
            'carpeta': carpeta
        }
        
        # Convertir a JSON y encriptar
        json_data = json.dumps(config).encode()
        encrypted = self.cipher.encrypt(json_data)
        
        # Guardar
        self.config_file.write_bytes(encrypted)
        self.config_file.chmod(0o600)
        
        return True
    
    def cargar(self):
        """Carga la configuración encriptada"""
        if not self.config_file.exists():
            return None
        
        try:
            # Leer y desencriptar
            encrypted = self.config_file.read_bytes()
            json_data = self.cipher.decrypt(encrypted)
            config = json.loads(json_data.decode())
            
            return config
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            return None
    
    def existe_config(self):
        """Verifica si existe configuración guardada"""
        return self.config_file.exists()
    
    def eliminar(self):
        """Elimina la configuración guardada"""
        if self.config_file.exists():
            self.config_file.unlink()
        return True
    
    def get_ubicacion(self):
        """Retorna la ubicación del archivo de configuración"""
        return str(self.config_dir)

