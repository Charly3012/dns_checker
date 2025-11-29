import logging
from datetime import datetime

class LogService:
    _mode = "stdout"   # stdout, file, both
    _file_path = "service.log"
    _file_handler = None

    @staticmethod
    def configure(mode="stdout", file_path="service.log"):
        LogService._mode = mode

        if mode in ("file", "both"):
            LogService._file_path = file_path

            # Configurar logging
            logging.basicConfig(
                filename=file_path,
                level=logging.INFO,
                format="%(asctime)s %(message)s",
                encoding="utf-8"
            )

    @staticmethod
    def log(message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}] {message}"

        if LogService._mode in ("stdout", "both"):
            print(formatted)

        if LogService._mode in ("file", "both"):
            logging.info(message)
