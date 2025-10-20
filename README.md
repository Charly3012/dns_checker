# DNS Checker

Personal project to automate DDNS configuration due to IP changes

---

## Features

- Check when a domain IP changes
- Notification via Microsoft Teams
- Telnet connection to update Dial-In IP for LAN-to-LAN VPNs

---

## Environmet variables 

| Variable         | Required | Default / Example                        | Description |
|------------------|----------|-----------------------------------------|-------------|
| `CHECK_INTERVAL` | optional | `20`                                     | Interval in seconds between DNS checks. |
| `DOMAIN_TYPE`    | optional | `A`                                      | Type of DNS record to check (`A`, `CNAME`, `AAAA`, etc.). |
| `DNS_NAMESERVER` | optional | `1.1.1.1`                                | DNS server to query. |
| `DOMAINS`        | yes      | `domain1.com,domain2.com,domain3.com`    | Comma-separated list of domains to check. |
| `DOMAINS_INDEX`  | yes      | `1,2,3`                                  | Comma-separated list of VPN's indexes corresponding to the domains. |
| `HOST_CHECK`     | yes      | `1,0,0`                                  | Comma-separated list of enable host dial in IP update for each domain (1 = yes, 0 = no). |
| `WEBHOOK_URL`    | yes      | `https://someurl.some`                   | URL for sending webhook Microsoft Teams notifications. |
| `HOST`           | yes      | `192.168.0.1`                            | Host IP to connect through Telnet. |
| `USER`           | yes      | `user`                                   | Username for authentication. |
| `PASSWORD`       | yes      | `password`                               | Password for authentication. |
| `READ_TIMEOUT`   | optional | `2`                                      | Timeout in seconds for reading responses. |

You can adjust these variables to customize container behavior.


---

## Docker

### Run with Docker CLI

```bash
# Pull the latest image
docker pull charly3012/dns-checker:latest

# Run the container
docker run --rm --env-file .env charly3012/dns-checker:latest

```

### Docker compose 

```yaml
services:
    dns_checker:
        image: charly3012/dns-checker:latest
        #build: .
        container_name: dns-checker
        restart: unless-stopped

        environment:
            - CHECK_INTERVAL=60 #Seconds
            - DOMAIN_TYPE=A
            - DNS_NAMESERVER=1.1.1.1 
            - DOMAINS=domain1.com, domain2.com, domain3.com
            - DOMAINS_INDEX=1,2,3
            - HOST_CHECK=1,0,0

            - WEBHOOK_URL=https://someurl.some

            - HOST=192.168.0.1
            - USER=user
            - PASSWORD=password
            - READ_TIMEUOT=2
```

And run it:

```bash
docker compose up -d 
```

---

## Changelog

See [CHANGELOG](CHANGELOG.md) for version history and changes.

## Notes

- The image is built for multi-architecture (amd64 and arm64).

