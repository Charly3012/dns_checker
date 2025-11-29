import telnetlib3

class DraytekService:
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password

    def login(self, tn):
        acc = tn.read_until(b"Account: ", timeout=3)
        if b"Account:" not in acc:
            return False
        tn.write(self.user.encode() + b"\n")

        pwd = tn.read_until(b"Password: ", timeout=3)
        if b"Password:" not in pwd:
            return False
        tn.write(self.password.encode() + b"\n")

        out = tn.read_until(b"DrayTek> ", timeout=3).decode(errors="ignore")
        return "DrayTek>" in out

    def update_dial_from_ip(self, profile_index, new_ip):
        try:
            tn = telnetlib3.Telnet(self.host, timeout=10)

            if not self.login(tn):
                tn.close()
                return False

            tn.write(f"vpn option {profile_index} peer={new_ip}\n".encode())
            out = tn.read_until(b"DrayTek>", timeout=3).decode()

            tn.write(b"exit\n")
            tn.close()

            return f"% Allow dial from (IP) : {new_ip}" in out

        except Exception:
            return False
