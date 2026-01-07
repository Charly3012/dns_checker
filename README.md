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
        "loggin_mode": "stdout",
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
| `loggin_mode` | `stdout` | Mode to show logs (stdout, file, both). |
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
            - ./path/to/service.log:/app/service.log #Optional to see system logs if `loggin_mode` is file or both

```

And run it:

```bash
docker compose up -d 
```

---

## Windows service deploy

This section guides you through the process of setting up the DNS Checker as a native Windows Service using **NSSM** (Non-Sucking Service Manager). This ensures the script runs in the background and starts automatically with the system.

> **IMPORTANT:** 
> Before proceeding, ensure you have already configured your `config.json` file. The service will look for this file to load your domain settings and API credentials.

### Prerequisites
1.  **Python:** Must be installed on the host machine. Version 3.10+ recommended.
2.  **Admin Privileges:** You must run the installation scripts with Administrator rights.

### Installation steps
1.  **Download NSSM:**
    * Download the official `.zip` from [nssm.cc/download](https://nssm.cc/download).
    * Extract `nssm.exe` (use the version inside the `win64` folder).
    * Place it inside the `service_setup/` folder.
    * **Note:** The executable must be named exactly `nssm.exe`.
  
2.  **Run the Installer:**
    Open a terminal (PowerShell or CMD) **as Administrator** at the root of the repository and execute the `install.ps1`:

    **Option A (recommended):** Auto-detection Python instance. If Python is in your system PATH, simply run:

    ```powershell
    .\service_setup\install.ps1
    ```

    **Option B**: Manual Python path. If you have multiple Python versions or it's not in your PATH, provide the absolute path:

    ```powershell
    .\service_setup\install.ps1 -PYTHON_EXE "C:\Users\<User>\AppData\Local\Programs\Python\Python314\python.exe"
    ```

3.  **Verify the Service:**
    * Open the Windows Services Manager (`services.msc`).
    * Look for the service named **DnsChecker**.
    * Confirm the status is **Running**.

### Updating the service
Use this script when you pull new code from the repository. It ensures the service is updated without losing your local configuration.

**Option A (recommended):** Auto-detection Python instance. If Python is in your system PATH, simply run:

```powershell
.\service_setup\update.ps1
```

**Option B**: Manual Python path. If you have multiple Python versions or it's not in your PATH, provide the absolute path:

```powershell
.\service_setup\update.ps1 -PYTHON_EXE "C:\Users\<User>\AppData\Local\Programs\Python\Python314\python.exe"
```

**Note:** Asks for confirmation, clears local .py changes (git restore), pulls the latest code, refreshes dependencies, and restarts the service.

### Uninstallation

To remove the service from your system, you have two options:

**Full Clean (Default):** Removes the service and deletes all log folders/files.
```powershell
.\service_setup\uninstall.ps1
```

**Preserve Logs:** Removes the service but keeps the log files for auditing.
```powershell
.\service_setup\uninstall.ps1 -PreserveLogs
```


### Monitoring and Troubleshooting

If the service starts but stops unexpectedly, or if you need to monitor its behavior, check the following locations:

* **Service Manager:** Open services.msc and look for DnsChecker.
* **Standard Logs:** Found in service_setup/logs/nssm_out.log.
* **Error Logs:** If the service fails to start, check service_setup/logs/nssm_errors.log for Python tracebacks.
* **Service Status:** You can check the real-time status using NSSM:
    ```PowerShell
    .\service_setup\nssm.exe status DnsChecker
    ```

## Changelog

See [CHANGELOG](CHANGELOG.md) for version history and changes.

## Notes

- The image supports amd64 and arm64 architectures.
- The draytek and azure sections can be omitted if not used.
- Optional fields fall back to internal defaults when not provided.

