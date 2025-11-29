from datetime import datetime
from models.dns_record import DnsRecord
from services.dns_service import DnsService
from services.draytek_service import DraytekService
from services.notifier_service import NotifierService
from services.azure_nsg_service import AzureNsgService
from config.models import AzureNSGConfig



class Checker:
    def __init__(self, dns_service: DnsService, draytek_service:DraytekService, nsg_service: AzureNsgService, notifier: NotifierService, records: list[DnsRecord], nsgs: list[AzureNSGConfig] , tries: int = 2):
        self.dns_service = dns_service
        self.draytek_service = draytek_service
        self.notifier = notifier
        self.nsg_service = nsg_service
        self.records = records
        self.nsgs = nsgs
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
                    msg += "<br>Actualizado en Draytek."
                else:
                    msg += "<br>ERROR al actualizar en el Draytek."
            else:
                msg += "<br>No se actualiza automáticamente en Draytek."


            if rec.change_in_azure:
                nsg_success = self.try_change_nsgs(old_ip, new_ip)

                if nsg_success:
                    msg += "<br>Actualizado en NSGs de Azure. "
                else:
                    msg += "<br>ERROR al actualizar NSGs de Azure. "

            else:
                msg += "<br>No se actualiza en NSGs Azure. "
            
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
                print(f"[TRY ERROR] Draytek fallo intento {attempt}: {e}")

        return False
    
    def try_change_nsgs(self, old_ip: str, new_ip: str):
        all_success = True  

        for nsg in self.nsgs:
            #print(f"\n[NSG] Modificando regla en: {nsg.name}")

            success_for_this_nsg = False

            for attempt in range(1, self.tries + 1):
                try:
                    success = self.nsg_service.update_rule_ip(
                        nsg_config=nsg,
                        old_ip=old_ip,
                        new_ip=new_ip
                    )

                    if success:
                        #print(f"[OK] NSG '{nsg.name}' actualizada correctamente")
                        success_for_this_nsg = True
                        break

                    print(f"[TRY FAILED] Intento fallido {attempt}/{self.tries}")

                except Exception as e:
                    print(f"[TRY ERROR] NSG '{nsg.name}' intento {attempt}: {e}")

            if not success_for_this_nsg:
                #print(f"[NSG] No se pudo actualizar la NSG '{nsg.name}' después de {self.tries} intentos")
                all_success = False

        return all_success




