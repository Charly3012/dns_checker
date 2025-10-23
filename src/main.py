import os
import time
import socket
import requests
import json
from datetime import datetime
import dns.resolver
import telnetlib3 as telnetlib

#Domains
INTERVAL = int(os.getenv("CHECK_INTERVAL", "20"))
DOMAIN_TYPE = str(os.getenv("DOMAIN_TYPE", "A"))
DNS_NAMESERVER = str(os.getenv("DNS_NAMESERVER", "1.1.1.1"))
DOMAINS = str(os.getenv("DOMAINS", ""))
DOMAINS_INDEX = os.getenv("DOMAINS_INDEX", "")
HOST_CHECK = os.getenv("HOST_CHECK", "")

#Notifications
WEBHOOK_URL = str(os.getenv("WEBHOOK_URL", ""))

#To update Dial from (IP)
HOST = os.getenv("HOST", "")
USER = os.getenv("USER", "")
PASSWORD = os.getenv("PASSWORD","")
READ_TIMEOUT = int(os.getenv("READ_TIMEOUT", "2"))



def login(tn: telnetlib.Telnet, user: str, password: str):
    account = tn.read_until(b"Account: ", timeout=3)
    if b"Account:" not in account:
        #print("[-] No se detectó prompt de Account.")
        return False
    tn.write(user.encode('ascii') + b"\n")

    passwo = tn.read_until(b"Password: ", timeout=3)
    if b"Password:" not in passwo:
            #print("[-] No se detectó prompt de password.")
            return False
    tn.write(password.encode('ascii') + b"\n")

    time.sleep(0.5)
    out = tn.read_until(b"DrayTek> ", timeout=3)
    decoded = out.decode(errors="ignore")
    
    if "DrayTek>" not in decoded:
        #print("[-] No se detectó prompt 'DrayTek>' después del login. Salida:\n", decoded)
        return False
    return True


def change_dial_from_ip(profileIndex, newIp):
    try:
            tn = telnetlib.Telnet(HOST, timeout=10)
            if not login(tn, USER, PASSWORD):
                #print("[x] Falla en el inicio de sesion")
                tn.close
                return False
            
            # send command to change Allow Dial-in from 
            tn.write(f"vpn option {profileIndex} peer={newIp}\n".encode('ascii'))

            # Read exit promt
            out = tn.read_until(b"DrayTek>", timeout=3).decode('ascii')

            flag: bool 
            if f"% Allow dial from (IP) : {newIp}" in out:
                #print("[OK] Dial from (IP) updated")
                flag = True
            else:
                #print("[KO] Dial from (IP) has not been updated")
                flag = False

            tn.write(b"exit\n")
            tn.close
            return flag

    except Exception as e:
        print("[x] Error general:", e)
        tn.close()
        return False

# Check DDNS
class DnsRecord:
    def __init__(self, domain, index, ip=None, hostCheck=False):
        self.domain = domain
        self.ip = ip
        self.hostCheck = hostCheck
        self.index = index

    def changeIp(self, ip):
        self.ip = ip

def init_records(domainsStr: str, hostCheckStr: str, indexStr) -> list:
    """
    Craate a DnsRecord list from domains and hostCheck strings
    
    domains: ['nasatizi.ddns.net', 'nasavall.ddns.net', 'nasamty.ddns.net']
    hostCheck: [0, 1, 1]
    index: 
    """

    domains = domainsStr.replace(' ', '').split(',')
    hostChecks = hostCheckStr.replace(' ', '').split(',')
    indexs = indexStr.replace(' ', '').split(',')

    if len(domains) != len(hostChecks) or len(domains) != len(indexs):
        raise ValueError("Lists don't have same length")

    dns_list = []
    for i, domain in enumerate(domains):
        hc = bool(hostChecks[i])
        record = DnsRecord(domain, hostCheck=hc, index=indexs[i])
        dns_list.append(record)

    return dns_list


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
        print("\nTeams message notification sent successfully\n")

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
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [DNS_NAMESERVER]
            resolver.lifetime = 10 
            resolver.timeout = 5 
            answers = resolver.resolve(record.domain, DOMAIN_TYPE, tcp=True)
            ip = answers[0].to_text()
            oldIp = record.ip

            if oldIp is None:
                print(f"[-] First check! - {record.domain} → {ip}")

            # Ip changed 
            elif oldIp != ip:
                print(f"[!] {record.domain} changed: {oldIp} → {ip}")
                message = f"{record.domain} ha cambiado: {oldIp} → {ip}. "

                if record.hostCheck:
                    success = change_dial_from_ip(record.index, ip)

                    if success:
                        message += "IP Cambiada exitosamente en el Draytek"
                    else:
                        message += "Error cambiando la IP en el Draytek"

                send_teams_message(message)

            else:
                print(f"[-] {record.domain} unchanged: {ip}")
            
            record.changeIp(ip)

        except socket.gaierror as e:
            print(f" {record.domain} → Error: {e}")


if __name__ == "__main__":
    try:
        dns_list = init_records(DOMAINS, HOST_CHECK, DOMAINS_INDEX)

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

        print(f"Starting DNS checker... (interval = {INTERVAL}s)")

        while True:
            check_domains()
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("\n[X] Script stopped by user.")
    except Exception as e:
        print(f"[X] Unexpected error: {e}")