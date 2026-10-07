from models.dns_record import DnsRecord
from services.dns_service import DnsService
from services.draytek_service import DraytekService
from services.notifier_service import NotifierService
from services.azure_nsg_service import AzureNsgService
from config.models import AzureNSGConfig
from services.log_service import LogService



class Checker:
    def __init__(self, dns_service: DnsService, draytek_service:DraytekService, nsg_service: AzureNsgService, notifier: NotifierService, records: list[DnsRecord], nsgs: list[AzureNSGConfig] , tries: int = 2):
        self.dns_service = dns_service
        self.draytek_service = draytek_service
        self.notifier = notifier
        self.nsg_service = nsg_service
        self.records = records
        self.nsgs = nsgs
        self.tries = tries
        # IPs viejas que siguen en los NSG porque fallo la actualizacion; se reintenta cada ciclo
        self.pending_nsg_removals: dict[str, set[str]] = {}

    def check_all(self):
        changed_flag = False
        LogService.log("[CHECK] Checking DNS resolutions...\n")

        for rec in self.records:

            new_ip = self.dns_service.resolve_ip(rec.domain)
            old_ip = rec.ip

            if new_ip == "x.x.x.x":
                changed_flag = True
                self.notifier.send(f"DnsService.Error: Some wrong with dns resolution/service to {rec.domain}, check log for more information")
                continue;
            
            # First time
            if not old_ip:
                changed_flag = True
                rec.update_ip(new_ip)
                LogService.log(f"[INIT] {rec.domain} -> {new_ip}")
                continue

            if new_ip == old_ip:
                if self.pending_nsg_removals.get(rec.domain):
                    changed_flag = True
                    self.retry_pending_nsgs(rec)
                continue

            changed_flag = True
            LogService.log(f"[CHANGE] {rec.domain}: {old_ip} -> {new_ip}")
            msg = f"{rec.domain}: {old_ip} -> {new_ip}. "
            rec.update_ip(new_ip)

            if rec.change_in_draytek:
                if self.try_change_draytek(rec.draytek_index, new_ip):
                    msg += "<br>Actualizado en Draytek."
                else:
                    msg += "<br>ERROR al actualizar en el Draytek."
            else:
                msg += "<br>No se actualiza automáticamente en Draytek."


            if rec.change_in_azure:
                self.pending_nsg_removals.setdefault(rec.domain, set()).add(old_ip)
                nsg_success = self.try_change_nsgs(self.pending_nsg_removals[rec.domain], new_ip)

                if nsg_success:
                    self.pending_nsg_removals.pop(rec.domain, None)
                    msg += "<br>Actualizado en NSGs de Azure. "
                else:
                    msg += "<br>ERROR al actualizar NSGs de Azure, se reintentará en cada ciclo. "

            else:
                msg += "<br>No se actualiza en NSGs Azure. "

            self.notifier.send(msg)
        

        if not changed_flag:
            LogService.log("[INFO] Ningúna IP cambio")


    def try_change_draytek(self, draytek_index: int, ip: str):
        for attempt in range(1, self.tries + 1):
            try:
                success = self.draytek_service.update_dial_from_ip(draytek_index, ip)
                if success:
                    return True
                LogService.log(f"[TRY FAILED] Draytek update index:{draytek_index} ip:{ip} try:{attempt}/{self.tries}")
            except Exception as e:
                LogService.log(f"[TRY ERROR] Draytek fallo intento {attempt}: {e}")

        return False
    
    def retry_pending_nsgs(self, rec: DnsRecord):
        pending = self.pending_nsg_removals[rec.domain]
        LogService.log(f"[RETRY] {rec.domain}: quitando {sorted(pending)} de NSGs, asegurando {rec.ip}")

        if self.try_change_nsgs(pending, rec.ip):
            self.pending_nsg_removals.pop(rec.domain, None)
            self.notifier.send(f"{rec.domain}: NSGs de Azure sincronizados con {rec.ip} tras reintento.")

    def try_change_nsgs(self, old_ips: set[str], new_ip: str):
        all_success = True  

        for nsg in self.nsgs:
            #LogService.log(f"\n[NSG] Modificando regla en: {nsg.name}")

            success_for_this_nsg = False

            for attempt in range(1, self.tries + 1):
                try:
                    success = self.nsg_service.sync_rule_ips(
                        nsg_config=nsg,
                        remove_ips=self.removable_ips(old_ips),
                        add_ip=new_ip
                    )

                    if success:
                        #LogService.log(f"[OK] NSG '{nsg.name}' actualizada correctamente")
                        success_for_this_nsg = True
                        break

                    LogService.log(f"[TRY FAILED] Intento fallido {attempt}/{self.tries}")

                except Exception as e:
                    LogService.log(f"[TRY ERROR] NSG '{nsg.name}' intento {attempt}: {e}")

            if not success_for_this_nsg:
                #LogService.log(f"[NSG] No se pudo actualizar la NSG '{nsg.name}' después de {self.tries} intentos")
                all_success = False

        return all_success

    def removable_ips(self, ips: set[str]) -> set[str]:
        # No quitar una IP que otro dominio con change_in_azure sigue usando
        in_use = {r.ip for r in self.records if r.change_in_azure and r.ip}
        return ips - in_use
