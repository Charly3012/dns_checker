import dns.resolver

class DnsService:

    def __init__(self, nameservers: list[str] = ['1.1.1.1'], domain_type: str = "A"):
        self.resolver = dns.resolver.Resolver()
        self.resolver.nameservers = nameservers
        self.domain_type = domain_type

    def resolve_ip(self, domain):
        answers = self.resolver.resolve(domain, self.domain_type, tcp=True)
        return answers[0].to_text()
