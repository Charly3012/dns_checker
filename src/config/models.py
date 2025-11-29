# config/models.py
from pydantic import BaseModel
from typing import List
from models.dns_record import DnsRecord


class GeneralConfig(BaseModel):
    interval: int
    loggin_mode: str
    tries: int


class NotifierConfig(BaseModel):
    teams_webhook_url: str

class DNSResolverConfig(BaseModel):
    domain_type: str
    nameservers: List[str]


class DraytekConfig(BaseModel):
    host: str
    user: str
    password: str
    read_timeout: int


class AzureNSGConfig(BaseModel):
    subscription_id: str
    resource_group: str
    name: str
    rule: str


class AzureConfig(BaseModel):
    tenant_id: str
    client_id: str
    client_secret: str
    nsgs: List[AzureNSGConfig]


class DomainConfig(BaseModel):
    host: str
    draytek_index: int
    change_in_draytek: bool
    change_in_azure: bool 


class AppConfig(BaseModel):
    general: GeneralConfig
    notifier: NotifierConfig
    dns_resolver: DNSResolverConfig
    draytek: DraytekConfig
    azure: AzureConfig
    records: List[DnsRecord]
