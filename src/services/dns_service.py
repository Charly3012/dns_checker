import dns.resolver
from services.log_service import LogService

class DnsService:

    def __init__(self, nameservers: list[str] = ['1.1.1.1'], domain_type: str = "A"):
        self.resolver = dns.resolver.Resolver()
        self.resolver.nameservers = nameservers
        self.domain_type = domain_type

    def resolve_ip(self, domain):
        try:

            answers = self.resolver.resolve(domain, self.domain_type, tcp=True)
            return answers[0].to_text()
        except Exception as e:
            LogService.log(f"[X] DnsService.Error: {e}")
            return "x.x.x.x"
