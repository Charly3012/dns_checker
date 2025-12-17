import json 
from pathlib import Path
from typing import Optional
from .models import AppConfig

class ConfigLoader: 
    _config: Optional[AppConfig] = None

    @staticmethod
    def load(path: str = "./config.json") -> AppConfig:
        if ConfigLoader._config is None:
            # Directorio raíz del proyecto
            base_dir = Path(__file__).resolve().parent.parent

            # Si path NO es absoluto
            config_path = Path(path)
            
            if not config_path.is_absolute():
                config_path = base_dir / path

            print(f"Buscando configuración en: {config_path.absolute()}")

            if not config_path.exists():
                raise FileNotFoundError(f"Config file not fount: {path}")
            
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)


            ConfigLoader._config = AppConfig(**data)


        return ConfigLoader._config