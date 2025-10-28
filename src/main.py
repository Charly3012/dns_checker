import time
from config import Config
from services.dns_service import DnsService
from services.draytek_service import DraytekService
from services.notifier_service import NotifierService
from app.checker import Checker

if __name__ == "__main__":
    try:
        config = Config()

        dns_service = DnsService(config.DNS_NAMESERVER, config.DOMAIN_TYPE)
        draytek_service = DraytekService(config.HOST, config.USER, config.PASSWORD)
        notifier = NotifierService(config.WEBHOOK_URL)

        app = Checker(dns_service, draytek_service, notifier, config)

        print("Starting DNS checker...\n")

        while True:
            app.check_all()
            time.sleep(config.INTERVAL)

    except KeyboardInterrupt:
        print("\n[X] Stopped by user.")
    except Exception as e:
        print(f"[X] Unexpected error: {e}")
        
