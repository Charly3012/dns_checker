import time
import os
from config.loader import ConfigLoader
from config.models import AppConfig
from services.dns_service import DnsService
from services.draytek_service import DraytekService
from services.notifier_service import NotifierService
from services.azure_nsg_service import AzureNsgService
from app.checker import Checker
from services.log_service import LogService


def main():
    #Load configuration 
    config: AppConfig = ConfigLoader.load()

    #Loggin config
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LOG_PATH = os.path.join(BASE_DIR, "service.log")

    LogService.configure(mode=config.general.loggin_mode, file_path=LOG_PATH)

    dns_service = DnsService(
        config.dns_resolver.nameservers, 
        config.dns_resolver.domain_type
        )
    
    draytek_service = DraytekService(
        config.draytek.host, 
        config.draytek.user, 
        config.draytek.password
        )
    
    nsg_service = AzureNsgService(
        config.azure.tenant_id, 
        config.azure.client_id,
        config.azure.client_secret
    )

    notifier = NotifierService(
        config.notifier.teams_webhook_url
        )

    app = Checker(
        dns_service, 
        draytek_service, 
        nsg_service,
        notifier, 
        config.records, 
        config.azure.nsgs,
        config.general.tries
        )

    LogService.log("[INIT] Starting DNS checker...\n")

    while True:
        app.check_all()
        time.sleep(config.general.interval)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        LogService.log("[X] Stopped by user. \n")
    except Exception as e:
        LogService.log(f"[X] Unexpected error: {e}\n")
        raise e
        


