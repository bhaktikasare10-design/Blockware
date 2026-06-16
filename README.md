# 🔐 BlockWare
### Decentralized Firmware Updates for IoT — Circuit Wizards

> **Major Project 2025-26 | Electronics & Telecommunication Engineering**
> Vivekanand Education Society's Institute of Technology (VESIT), Mumbai

---

## 📌 Problem Statement
Conventional IoT firmware update methods use centralized systems, prone to security weaknesses, single-point failures, and poor transparency. Insecure firmware distribution can lead to device hijacking, installation of malicious firmware, and violation of user privacy. Large-scale IoT environments require a secure, decentralized, and easily verifiable firmware update framework.

---

## 🎯 Objectives
- Build a safe and reliable firmware update system for IoT devices using blockchain
- Ensure firmware updates come from trusted sources and are not altered during transfer
- Eliminate single-point-of-failure risk from centralized servers
- Support multiple IoT device types from different manufacturers
- Maintain clear, traceable, auditable records of all firmware updates on-chain

---

## 🏗️ System Architecture

```
[Firmware Developer / Manufacturer PC]
  └─ Compiles ESP32 firmware
  └─ Generates hash + digital signature
          ↓
[Firmware Storage — Cloud/Local Server]
  └─ Stores firmware binary (.bin)
  └─ Provides firmware download URL
          ↓
[Lightweight Blockchain Network — Private]        [Monitoring Dashboard]
  └─ Smart contracts store:                         └─ Live device status
       firmware version, hash,                      └─ OTA success/failure
       device type, signature                       └─ Blockchain logs
          ↓ Verification                            └─ Security alerts
[Raspberry Pi Gateway]
  └─ Acts as blockchain light node
  └─ Fetches + verifies firmware metadata
  └─ Downloads and checks hash + signature
  └─ Manages secure OTA updates
          ↓
[IoT Device — ESP32]
  └─ Secure boot enabled
  └─ Receives OTA update over Wi-Fi
  └─ Verifies firmware signature
  └─ Installs only trusted firmware ✅
```

---

## ⚙️ Tech Stack

| Layer           | Technology                                       | 
|-----------------|--------------------------------------------------|
| Blockchain      | Solidity, Ganache, Ethereum (private)            |
| Smart Contracts | Firmware version, hash, signature storage        |
| Firmware Broker | Raspberry Pi 3B                                  |
| Gateway         | Laptop-simulated Pi Zero (light node)            |
| End Device      | ESP32 with I2C LCD display                       |
| Communication   | OTA (Wi-Fi), I2C, UART                           |
| Security        | SHA-256 hashing, digital signatures, secure boot |

---

## 🔒 Security Features
- SHA-256 firmware hash verification before any update is applied
- Digital signature validation — only manufacturer-signed firmware accepted
- On-chain immutable record — tampered firmware automatically rejected
- Secure boot on ESP32 — prevents unauthorized firmware execution
- Decentralized architecture — no single point of attack or failure

---

## ✅ Project Status

- [x] Smart contract deployed on local Ethereum (Ganache)
- [x] Firmware hash registered and verified on-chain
- [x] Raspberry Pi gateway fetches and verifies metadata
- [x] OTA update pushed successfully (v1.0.0 → v1.0.3)
- [x] ESP32 LCD confirms version update
- [x] End-to-end working demo complete
- [ ] Monitoring dashboard (in progress)
- [ ] Research paper — under review

---

## 🌍 UN Sustainable Development Goals
- **SDG 9** — Industry, Innovation and Infrastructure
- **SDG 11** — Sustainable Cities and Communities
- **SDG 16** — Peace, Justice and Strong Institutions

---

## 👥 Team — Circuit Wizards

| Name
| Saurabh Maurya
| Gopinath Sasmal
| Bhakti Kasare

**Supervisor:** Mrs. Arti Sawant, VESIT

---

## 📄 Research Publication
- Paper based on BlockWare — currently being written
- Target journal: IJARSCT / IEEE (TBD)

