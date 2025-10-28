class DnsRecord:
    def __init__(self, domain, index, ip=None, hostCheck=False):
        self.domain = domain
        self.index = index
        self.hostCheck = hostCheck
        self.ip = ip

    def update_ip(self, new_ip):
        self.ip = new_ip
