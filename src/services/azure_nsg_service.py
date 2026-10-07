import ipaddress
from typing import Iterable
from azure.identity import ClientSecretCredential
from azure.mgmt.network import NetworkManagementClient
from config.models import AzureNSGConfig
from services.log_service import LogService

class AzureNsgService:
    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        self.credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )

    @staticmethod
    def _normalize(prefix: str) -> str:
        # "1.2.3.4/32" y "1.2.3.4" son la misma IP para la regla
        try:
            net = ipaddress.ip_network(prefix.strip(), strict=False)
        except ValueError:
            return prefix.strip()
        if net.num_addresses == 1:
            return str(net.network_address)
        return str(net)

    def sync_rule_ips(self, nsg_config: AzureNSGConfig, remove_ips: Iterable[str], add_ip: str) -> bool:
        """
        Quita remove_ips y asegura add_ip en el origen de la regla.
        Solo lee/escribe la regla (securityRules/read y securityRules/write), no el NSG completo.
        """
        network = NetworkManagementClient(self.credential, nsg_config.subscription_id)
        rg, nsg_name, rule_name = nsg_config.resource_group, nsg_config.name, nsg_config.rule

        rule = network.security_rules.get(rg, nsg_name, rule_name)

        # Azure guarda una sola IP en source_address_prefix y varias en source_address_prefixes
        current = list(rule.source_address_prefixes or [])
        if rule.source_address_prefix:
            # "*", "Internet", service tags... no se pueden mezclar con IPs
            if not self._is_ip(rule.source_address_prefix):
                LogService.log(f"[AZURE] Regla '{rule_name}' en '{nsg_name}' usa origen '{rule.source_address_prefix}', no se modifica")
                return False
            current.append(rule.source_address_prefix)

        add_norm = self._normalize(add_ip)
        to_remove = {self._normalize(ip) for ip in remove_ips if ip} - {add_norm}

        updated = [p for p in current if self._normalize(p) not in to_remove]
        if add_norm not in {self._normalize(p) for p in updated}:
            updated.append(add_ip)

        # Quitar duplicados conservando el orden; Azure rechaza prefijos repetidos
        seen = set()
        updated = [p for p in updated if not (self._normalize(p) in seen or seen.add(self._normalize(p)))]

        if updated == current and not rule.source_address_prefix:
            return True

        rule.source_address_prefix = None
        rule.source_address_prefixes = updated

        LogService.log(f"[AZURE] '{nsg_name}/{rule_name}': {current} -> {updated}")
        network.security_rules.begin_create_or_update(rg, nsg_name, rule_name, rule).result()
        return True

    @staticmethod
    def _is_ip(prefix: str) -> bool:
        try:
            ipaddress.ip_network(prefix.strip(), strict=False)
            return True
        except ValueError:
            return False
