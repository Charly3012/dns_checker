import os

class Config:
    INTERVAL = int(os.getenv("CHECK_INTERVAL", "20"))
    DOMAIN_TYPE = os.getenv("DOMAIN_TYPE", "A")
    DNS_NAMESERVER = os.getenv("DNS_NAMESERVER", "")

    #general config
    DOMAINS = os.getenv("DOMAINS", "")
    DOMAINS_INDEX = os.getenv("DOMAINS_INDEX", "")
    HOST_CHECK = os.getenv("HOST_CHECK", "")

    #Teams webhook url
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

    #Draytek
    HOST = os.getenv("HOST", "")
    USER = os.getenv("USER", "")
    PASSWORD = os.getenv("PASSWORD", "")
    READ_TIMEOUT = int(os.getenv("READ_TIMEOUT", "2"))