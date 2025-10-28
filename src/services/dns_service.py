import dns.resolver

class DnsService:

    def __init__(self, nameserver, domain_type="A"):
        self.resolver = dns.resolver.Resolver()
        self.resolver.nameservers = [nameserver, '1.1.1.1']
        self.domain_type = domain_type

    def resolve_ip(self, domain):
        answers = self.resolver.resolve(domain, self.domain_type, tcp=True)
        return answers[0].to_text()
