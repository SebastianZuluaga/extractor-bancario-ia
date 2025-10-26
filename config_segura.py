"""Gestión segura de la configuración sensible del usuario.

El módulo proporciona una capa de abstracción para almacenar, recuperar y
rotar credenciales de forma cifrada utilizando :mod:`cryptography`.  Se intenta
usar el llavero del sistema operativo cuando está disponible; en caso
contrario, se guarda la clave de cifrado en disco con permisos estrictos.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional

from cryptography.fernet import Fernet, InvalidToken

try:  # pragma: no-cover - dependencias opcionales
    import keyring  # type: ignore

    KEYRING_AVAILABLE = True
except Exception:  # pragma: no-cover - keyring no disponible
    keyring = None
    KEYRING_AVAILABLE = False


from logging_utils import configurar_logger


logger, _ = configurar_logger("app.config")


class ConfigSegura:
    """Gestiona el almacenamiento cifrado de credenciales sensibles."""

    SERVICE_NAME = "ExtractorBancarioIA"

    def __init__(self) -> None:
        self.config_dir = Path.home() / ".extractor_bancario"
        self.config_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        try:
            # Reforzar permisos: solo el usuario actual puede leer/escribir.
            self.config_dir.chmod(0o700)
        except PermissionError:
            logger.warning("No fue posible establecer permisos 700 en %s", self.config_dir)

        self.config_file = self.config_dir / "config.enc"
        self.key_file = self.config_dir / "key.key"

        self._cipher = self._obtener_cipher()

    # ------------------------------------------------------------------
    # Gestión de claves
    # ------------------------------------------------------------------
    def _obtener_cipher(self) -> Fernet:
        key_bytes = self._cargar_clave()
        return Fernet(key_bytes)

    def _cargar_clave(self) -> bytes:
        """Recupera la clave de cifrado, generándola si es necesario."""

        if KEYRING_AVAILABLE:
            try:
                username = os.getlogin()
            except OSError:
                username = os.getenv("USER", "default")

            try:
                secret = keyring.get_password(self.SERVICE_NAME, username)
            except Exception as exc:  # pragma: no-cover - depende del OS
                logger.warning("No fue posible leer la clave desde el llavero: %s", exc)
                secret = None

            if secret:
                return secret.encode()

        if not self.key_file.exists():
            self._generar_clave()

        return self.key_file.read_bytes().strip()

    def _generar_clave(self, force: bool = False) -> None:
        """Genera y almacena una nueva clave Fernet."""

        if self.key_file.exists() and not force:
            return

        key = Fernet.generate_key()

        if KEYRING_AVAILABLE:
            try:
                username = os.getlogin()
            except OSError:
                username = os.getenv("USER", "default")

            try:  # pragma: no-cover - depende del OS
                keyring.set_password(self.SERVICE_NAME, username, key.decode())
                logger.info("Clave almacenada en el llavero del sistema para el usuario %s", username)
                return
            except Exception as exc:
                logger.warning("Fallo al guardar la clave en el llavero: %s. Se usará almacenamiento local.", exc)

        self.key_file.write_bytes(key)
        try:
            self.key_file.chmod(0o600)
        except PermissionError:
            logger.warning("No fue posible establecer permisos 600 en %s", self.key_file)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------
    def guardar(self, api_key: str, password: str, carpeta: str) -> bool:
        """Guarda de forma cifrada la configuración sensible del usuario."""

        datos = {
            "api_key": api_key.strip(),
            "password": password.strip(),
            "carpeta": carpeta.strip(),
        }

        json_data = json.dumps(datos, ensure_ascii=False).encode()
        encrypted = self._cipher.encrypt(json_data)

        self.config_file.write_bytes(encrypted)
        try:
            self.config_file.chmod(0o600)
        except PermissionError:
            logger.warning("No fue posible establecer permisos 600 en %s", self.config_file)

        logger.info("Configuración cifrada guardada correctamente en %s", self.config_file)
        return True

    def cargar(self) -> Optional[Dict[str, str]]:
        """Recupera la configuración cifrada si existe."""

        if not self.config_file.exists():
            return None

        try:
            encrypted = self.config_file.read_bytes()
            json_data = self._cipher.decrypt(encrypted)
            config = json.loads(json_data.decode())
            if not isinstance(config, dict):
                raise ValueError("Formato de configuración inválido")
            return config
        except InvalidToken:
            logger.error("La configuración cifrada no pudo desencriptarse. La clave podría haber cambiado.")
        except Exception as exc:
            logger.error("Error cargando configuración cifrada: %s", exc)

        return None

    def existe_config(self) -> bool:
        """Indica si existe un archivo de configuración cifrada."""

        return self.config_file.exists()

    def eliminar(self) -> bool:
        """Elimina la configuración almacenada."""

        if self.config_file.exists():
            self.config_file.unlink()
            logger.info("Archivo de configuración eliminado")
        return True

    def rotar_clave(self) -> bool:
        """Genera una nueva clave de cifrado y re-encripta la configuración."""

        datos = self.cargar()
        self._generar_clave(force=True)
        self._cipher = self._obtener_cipher()

        if datos:
            self.guardar(datos.get("api_key", ""), datos.get("password", ""), datos.get("carpeta", ""))
        logger.info("Clave de cifrado rotada exitosamente")
        return True

    def get_ubicacion(self) -> str:
        """Devuelve la ruta del directorio seguro utilizado por la aplicación."""

        return str(self.config_dir)


