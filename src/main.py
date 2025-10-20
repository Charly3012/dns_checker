import os
import time
import socket
import requests
import json
from datetime import datetime
import dns.resolver

INTERVAL = int(os.getenv("CHECK_INTERVAL", "20"))
DOMAIN_TYPE = str(os.getenv("DOMAIN_TYPE", "A"))
DNS_NAMESERVER = str(os.getenv("DNS_NAMESERVER", "1.1.1.1"))
DOMAINS = str(os.getenv("DOMAINS", ""))
WEBHOOK_URL = str(os.getenv("WEBHOOK_URL", ""))

class DnsRecord:
    def __init__(self, domain, ip=None):
        self.domain = domain
        self.ip = ip

    def changeIp(self, ip):
        self.ip = ip

def send_teams_message(message: str):
    try:
        payload = {
            "message" : message
        }
        headers = {
            "Content-Type" : "application/json"
        }

        response = requests.post(
            WEBHOOK_URL, 
            headers=headers, 
            data=json.dumps(payload),
            timeout=10
        )

        response.raise_for_status()
        print("\n[-] +Teams message notification sent successfully\n")

    except requests.exceptions.HTTPError as http_err:
        print(f"[X] HTTP error: {http_err} (status code: {response.status_code})")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"[X] Connection error: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"[X] Timeout: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"[X] An error ocurred: {req_err}")

def check_domains():
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking DNS resolutions...")
    for record in dns_list:
        try:
            answers = resolver.resolve(record.domain, DOMAIN_TYPE)
            ip = answers[0].to_text()
            oldIp = record.ip

            if oldIp is None:
                print(f"[-] First check! - {record.domain} → {ip}")
            elif oldIp != ip:
                print(f"[-] {record.domain} changed: {oldIp} → {ip}")
                send_teams_message(f" {record.domain} ha cambiado: {oldIp} → {ip}, cambie inmediatamente en la VPN y en las reglas de base de datos.")
            else:
                print(f"[-] {record.domain} unchanged: {ip}")
            
            record.changeIp(ip)

        except socket.gaierror as e:
            print(f"[X] {record.domain} → Error: {e}")


if __name__ == "__main__":
    try:
        dns_list = [DnsRecord(domain.strip()) for domain in DOMAINS.split(",") if domain.strip()]

        while not dns_list:
            print("[X] Domain list is empty...")
            time.sleep(INTERVAL)

        while not WEBHOOK_URL:
            print("[X] Webhook url is empty")
            time.sleep(INTERVAL)
            
        print("########## CONFIGURATIONS ##########\n")
        print(f"Interval check: {INTERVAL} (seconds)")
        print(f"DNS Nameserver: {DNS_NAMESERVER}")
        print(f"Domain type: {DOMAIN_TYPE}\n")
        print("########## CONFIGURATIONS ##########\n")

        resolver = dns.resolver.Resolver()
        resolver.nameservers = [DNS_NAMESERVER]

        print(f"Starting DNS checker... (interval = {INTERVAL}s)")

        while True:
            check_domains()
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("\n[X] Script stopped by user.")