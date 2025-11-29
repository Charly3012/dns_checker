from pydantic import BaseModel

class DnsRecord(BaseModel):
    domain: str
    ip: str | None = None
    draytek_index: int
    change_in_draytek: bool = False
    change_in_azure: bool = False

    def update_ip(self, new_ip):
        self.ip = new_ip
