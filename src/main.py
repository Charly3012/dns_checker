import time
from config.loader import ConfigLoader
from config.models import AppConfig
from services.dns_service import DnsService
from services.draytek_service import DraytekService
from services.notifier_service import NotifierService
from services.azure_nsg_service import AzureNsgService
from app.checker import Checker

if __name__ == "__main__":
    try:
        #Load configuration 
        config: AppConfig = ConfigLoader.load()

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

        print("Starting DNS checker...\n")

        while True:
            app.check_all()
            time.sleep(config.general.interval)

    except KeyboardInterrupt:
        print("\n[X] Stopped by user.")
    except Exception as e:
        print(f"[X] Unexpected error: {e}")
        raise e
        
