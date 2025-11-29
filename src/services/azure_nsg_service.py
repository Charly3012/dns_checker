from azure.identity import ClientSecretCredential
from azure.mgmt.network import NetworkManagementClient
from config.models import AzureNSGConfig

class AzureNsgService:
    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        self.credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )

    def update_rule_ip(self, nsg_config: AzureNSGConfig, old_ip: str, new_ip: str) -> bool:
        subscription_id = nsg_config.subscription_id
        resource_group = nsg_config.resource_group
        nsg_name = nsg_config.name
        rule_name = nsg_config.rule

        network = NetworkManagementClient(self.credential, subscription_id)

        #print(f"[AZURE] Obteniendo NSG {nsg_name}...")

        nsg = network.network_security_groups.get(resource_group, nsg_name)

        # Buscar la regla
        rule = None
        for r in nsg.security_rules:
            if r.name == rule_name:
                rule = r
                break

        if not rule:
            #print(f"[AZURE] Rule {nsg_config.name} not found")
            return False

        #print(f"[AZURE] IPs actuales: {rule.source_address_prefixes}")

        if old_ip in rule.source_address_prefixes:
            rule.source_address_prefixes.remove(old_ip)
            #print(f"[AZURE] Removiendo {old_ip}")
        #else:
            #print(f"[AZURE] La IP anterior {old_ip} no estaba en la regla")

        #print(f"[AZURE] Añadiendo {new_ip}")
        rule.source_address_prefixes.append(new_ip)

        #print(f"[AZURE] Guardando cambios en Azure...")

        try:
            poller = network.network_security_groups.begin_create_or_update(
                resource_group,
                nsg_name,
                nsg
            )
            poller.result()
            #print("[AZURE] ¡Regla actualizada!")
            return True

        except Exception as ex:
            #print(f"[AZURE] ERROR al actualizar la regla: {ex}")
            return False