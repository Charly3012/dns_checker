# Changelog

Format is based to [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
and [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]
### Added

### Fixed

---

## [0.1.0] - 2025-10-19
### Added
- Support to change DNS Nameserver
- Support multiple domains with a list in environments
- Notifications through Microsoft Teams with Webhook

### Fixed
- Avoid cache system

---

## [0.2.0] - 2025-10-19
### Added
- Support connect througt telnet to update dial in IP in Draytek
- Support check domains without change dial IP at Draytek

### Fixed

---

## [0.2.1] - 2025-10-21
### Added

### Fixed
- Add missing dependency 'telnetlib3'

---

## [0.2.2] - 2025-10-23
### Added

### Fixed
- Hot fix when the flag 'host_check' in a domain is false the teams message were not sent

---

## [0.2.3] - 2025-10-27
### Added

### Fixed
- Hot fix in 'HostCheck' flag, bad parse to bool

---

## [1.0.0] Stable version - 2025-11-29
### Added
- Support to change ip rules in NSG
- New method to configure variables in application via json 
- Support for multiple attempts in change operations in Azure NSG and DrayTek

### Fixed
- 

---

## [1.1.0] Windows service version - 2025-12-17
### Added
- Multiple ways to log (stdout, log file)
- Allow run as windows service with NSSM

### Fixed
- Quit conflictive characters

---