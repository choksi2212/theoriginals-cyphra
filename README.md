# CYPHRA

**Real-Time AI-Powered Threat Detection · Autonomous Response · Military-Grade Secure Communications**

---

## Overview

CYPHRA is a production-grade cybersecurity platform combining real-time network threat detection, autonomous response, and end-to-end encrypted communications.

## Core Capabilities

- **Security Operations Center (SOC)** — Live packet capture, 6-model ML ensemble (98.83% accuracy), autonomous firewall blocking
- **Defence Operations Center (DOC)** — Signal integrity monitoring, EW threat detection, tamper-evident audit logging
- **Ghost Messenger** — AES-256-GCM encrypted messaging, self-destructing messages, cross-platform (Web + Android + iOS)

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | React 18, Vite, TailwindCSS, Zustand, Three.js |
| Backend | Node.js, Express, WebSocket |
| ML Service | Python, FastAPI, LightGBM, XGBoost, CatBoost, Scapy |
| Crypto (WASM) | Rust, AES-256-GCM, X25519, Ed25519, HKDF-SHA256 |
| Crypto (Native) | Rust, Kyber-1024, libsodium, BLAKE3, X3DH Protocol |
| Database | VedDB (custom Rust encrypted key-value store) |
| Mobile | Kotlin + Jetpack Compose (Android), PWA (iOS) |

## Quick Start

```bash
# 1. Start database
veddb-server.exe

# 2. Start ML service (as Administrator)
cd machine_learning/inference_service
python main.py

# 3. Start backend
cd web-app/backend
node server.js

# 4. Start frontend
cd web-app
npm install && npm run dev
```

## License

Proprietary
