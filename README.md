# DNS Checker

![Docker Pulls](https://img.shields.io/docker/pulls/charly3012/dns-checker)
![Docker Image Size](https://img.shields.io/docker/image-size/charly3012/dns-checker/latest)
![Architecture](https://img.shields.io/badge/arch-amd64%20%7C%20arm64-blue)
![Python](https://img.shields.io/badge/python-3.11+-yellow)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/build-passing-brightgreen)

Automated dynamic DNS monitor with optional DrayTek and Azure NSG integration

**NOTE: Project with the sole purpose of personal use.** If the entire application or the code is useful to you, go ahead.

---

## Overview

DNS Checker is a lightweight automation tool designed to detect DNS IP changes and trigger optional corrective actions such as:

- Sending notifications (Microsoft Teams)
- Updating Dial-In IP in DrayTek routers via Telnet
- Updating IP-based rules in Azure Network Security Groups (NSG)

The application now uses a single JSON configuration file, eliminating the need for environment variables and improving clarity, portability, and version control.

---

## Features

- Monitors DNS records and detects IP changes
- Sends notifications via Microsoft Teams Webhook
- Optional automatic update of:
  - DrayTek VPN "Dial-In IP"
  - Azure NSG security rules
- Multi-domain support
- Multiple retry attempts for critical operations
- Configurable nameservers and DNS record types
- JSON-based configuration (no environment variables needed)

---

## Configuration

All settings are defined in a single JSON file such as `config.json` you can see the reference in [config-example.json](./src/config-example.json)

```json
{
    "general": {
        "interval": 20,
        "loggin_mode": "console",
        "tries": 3
    },
    "notifier": {
        "teams_webhook_url": ""
    },
    "dns_resolver": {
        "domain_type": "A",
        "nameservers": ["1.1.1.1"]
    },
    "draytek": {
        "host": "192.168.0.1",
        "user": "admin",
        "password": "your-password-here",
        "read_timeout": 2
    },
    "azure": {
        "tenant_id": "your-tenant-id",
        "client_id": "your-client-id",
        "client_secret": "your-client-secret",
        "nsgs": [
            {
                "subscription_id": "your-subscription-id",
                "resource_group": "your-resource-group",
                "name": "your-nsg-name",
                "rule": "your-rule-name"
            }
        ]
    },
    "records": [
        {
            "domain": "example.com",
            "ip": "",
            "draytek_index": 1,
            "change_in_draytek": false,
            "change_in_azure": false
        }
    ]
}
```

### Configuration reference 

**general**
| Field         | Default   | Description                                                  |
| ------------- | --------- | ------------------------------------------------------------ |
| `interval`    | `20`      | Interval (seconds) between DNS checks.                       |
| `loggin_mode` | `console` | Reserved for future logging output modes (e.g., file, JSON). |
| `tries`       | `2`       | Number of retry attempts for operations (DrayTek or NSG).    |


**notifier**
| Field               | Required | Description                                                        |
| ------------------- | -------- | ------------------------------------------------------------------ |
| `teams_webhook_url` | Optional | Microsoft Teams Webhook URL. Leave empty to disable notifications. |


**dns_resolver**
| Field         | Default       | Description                                           |
| ------------- | ------------- | ----------------------------------------------------- |
| `domain_type` | `"A"`         | DNS record type to resolve (`A`, `AAAA`, `CNAME`, …). |
| `nameservers` | `["1.1.1.1"]` | List of DNS nameservers to use for resolution.        |


**draytek** (optional)
Required only if any domain has `"change_in_draytek": true`.
| Field          | Required | Description                         |
| -------------- | -------- | ----------------------------------- |
| `host`         | Yes      | DrayTek router IP.                  |
| `user`         | Yes      | Telnet username.                    |
| `password`     | Yes      | Telnet password.                    |
| `read_timeout` | `2`      | Read timeout for Telnet operations. |

**azure** (optional)
Required only if any domain has `"change_in_azure": true`.
| Field           | Required | Description                      |
| --------------- | -------- | -------------------------------- |
| `tenant_id`     | Yes      | Azure tenant ID.                 |
| `client_id`     | Yes      | Azure application client ID.     |
| `client_secret` | Yes      | Azure application secret.        |
| `nsgs`          | Yes      | List of NSGs to update rules on. |


Each NSG entry includes: 
| Field             | Description                      |
| ----------------- | -------------------------------- |
| `subscription_id` | Subscription containing the NSG. |
| `resource_group`  | Resource group name.             |
| `name`            | NSG name.                        |
| `rule`            | Name of the rule to update.      |


**records**
A list of records configurations. Each record includes:
| Field               | Default      | Description                                                       |
| ------------------- | ------------ | ----------------------------------------------------------------- |
| `domain`              | **required** | Domain to monitor.                                                |
| `ip`                | empty        | Last known IP. If empty, first resolved IP becomes initial state. |
| `draytek_index`     | optional     | VPN profile index in DrayTek (only required if updating).         |
| `change_in_draytek` | `false`      | Whether to update DrayTek when IP changes.                        |
| `change_in_azure`   | `false`      | Whether to update Azure NSG rules when IP changes.                |


---

## Docker

### Run with Docker CLI

```bash
# Pull the latest image
docker pull charly3012/dns-checker:latest

# Run the container
docker run --rm \
    -v ./config.json:/app/config.json \
    charly3012/dns-checker:latest

```

### Docker compose 

```yaml
services:
    dns_checker:
        image: charly3012/dns-checker:latest
        #build: .
        container_name: dns-checker
        restart: unless-stopped

        volumes:
            - ./path/to/config.json:/app/config.json #See config-example.json to configure application

```

And run it:

```bash
docker compose up -d 
```

---

## Changelog

See [CHANGELOG](CHANGELOG.md) for version history and changes.

## Notes

- The image supports amd64 and arm64 architectures.
- The draytek and azure sections can be omitted if not used.
- Optional fields fall back to internal defaults when not provided.

