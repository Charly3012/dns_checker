from datetime import datetime
from models.dns_record import DnsRecord
from services.dns_service import DnsService
from services.draytek_service import DraytekService
from services.notifier_service import NotifierService

class Checker:
    def __init__(self, dns_service: DnsService, draytek_service:DraytekService, notifier: NotifierService, records: list[DnsRecord], tries: int = 2):
        self.dns_service = dns_service
        self.draytek_service = draytek_service
        self.notifier = notifier
        self.records = records
        self.tries = tries

    def check_all(self):
        changed_flag = False
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking DNS resolutions...")

        for rec in self.records:

            new_ip = self.dns_service.resolve_ip(rec.domain)
            old_ip = rec.ip
            
            # First time
            if not old_ip:
                changed_flag = True
                rec.update_ip(new_ip)
                print(f"[INIT] {rec.domain} → {new_ip}")
                continue

            if new_ip == old_ip:
                continue

            changed_flag = True
            print(f"[CHANGE] {rec.domain}: {old_ip} → {new_ip}")
            msg = f"{rec.domain}: {old_ip} → {new_ip}. "

            if rec.change_in_draytek:
                if self.try_change_draytek(rec.draytek_index, new_ip):
                    msg += "Actualizado en Draytek."
                else:
                    msg += "ERROR al actualizar en el Draytek."
            else:
                msg += "No se actualiza automáticamente en Draytek."
            
            rec.update_ip(new_ip)
            self.notifier.send(msg)
        

        if not changed_flag:
            print("[INFO] Ningúna IP cambio")


    def try_change_draytek(self, draytek_index: int, ip: str):
        for attempt in range(1, self.tries + 1):
            try:
                success = self.draytek_service.update_dial_from_ip(draytek_index, ip)
                if success:
                    return True
                print(f"[TRY FAILED] Draytek update index:{draytek_index} ip:{ip} try:{attempt}/{self.tries}")
            except Exception as e:
                print(f"[ERROR] Draytek fallo intento {attempt}: {e}")

        return False


