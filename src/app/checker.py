from datetime import datetime
from models.dns_record import DnsRecord
from services.dns_service import DnsService
from services.draytek_service import DraytekService
from services.notifier_service import NotifierService

class Checker:
    def __init__(self, dns_service: DnsService, draytek_service:DraytekService, notifier: NotifierService, config):
        self.dns_service = dns_service
        self.draytek_service = draytek_service
        self.notifier = notifier
        self.config = config
        self.records = self._load_records()

    def _load_records(self):
        domains = self.config.DOMAINS.replace(" ", "").split(",")
        checks = self.config.HOST_CHECK.replace(" ", "").split(",")
        indexes = self.config.DOMAINS_INDEX.replace(" ", "").split(",")

        if len(domains) != len(checks) or len(domains) != len(indexes):
            raise ValueError("Lists don't have same length")

        return [
            DnsRecord(
                domain=domains[i],
                index=indexes[i],
                hostCheck=bool(int(checks[i]))
            )
            for i in range(len(domains))
        ]

    def check_all(self):
        some_ip_changed: bool = False
        print(f"\n[{datetime.now()}] Checking DNS...") 

        for rec in self.records:
            try:
                new_ip = self.dns_service.resolve_ip(rec.domain)
                old_ip = rec.ip
                
                # First time
                if not old_ip:
                    some_ip_changed = True
                    rec.update_ip(new_ip)
                    print(f"[INIT] {rec.domain} → {new_ip}")
                    continue

                if new_ip != old_ip:
                    print(f"[CHANGE] {rec.domain}: {old_ip} → {new_ip}")
                    msg = f"{rec.domain}: {old_ip} → {new_ip}. "

                    if rec.hostCheck:
                        ok = self.draytek_service.update_dial_from_ip(rec.index, new_ip)
                        msg += "Actualizado en Draytek." if ok else "ERROR en Draytek."
                    else:
                        msg += "No se actualiza automáticamente en Draytek."

                    some_ip_changed = True
                    self.notifier.send(msg)

                rec.update_ip(new_ip)

            except Exception as e:
                print(f"[ERROR] {rec.domain}: {e}")

        if not some_ip_changed:
            print("[INFO] Ningúna IP cambio")
