# AuraLearn — End-to-End Deployment Report

**Project:** AuraLearn — Emotion-Aware Adaptive Learning Platform  
**Group Reference:** R26-SE-022  
**Deployment Date:** 6 September 2026  
**Deployed By:** R26-SE-022 Team  
**Report Generated:** 2026-09-06  

---

## 1. Executive Summary

AuraLearn is a full-stack, AI-powered adaptive learning platform composed of five independent microservices and a Next.js frontend. The system was successfully deployed to an Oracle Cloud Infrastructure (OCI) virtual machine and is accessible at:

> 🌐 **https://www.auralearn.tech**

All services are running, SSL is configured with automatic renewal, and the application is fully operational.

---

## 2. Cloud Infrastructure

### 2.1 Virtual Machine Specifications

| Property | Value |
|----------|-------|
| **Cloud Provider** | Oracle Cloud Infrastructure (OCI) |
| **Instance Type** | VM.Standard.A1.Flex (ARM-based / aarch64) |
| **Operating System** | Oracle Linux Server 9.8 |
| **Architecture** | ARM64 (aarch64) |
| **vCPUs** | 2 |
| **RAM** | 10 GB |
| **Disk** | 30 GB (19 GB used / 12 GB free) |
| **Public IP Address** | `129.146.71.78` |
| **Region** | Oracle Cloud (US East) |

### 2.2 Domain & DNS Configuration

| Record Type | Name | Value |
|-------------|------|-------|
| A Record | `www.auralearn.tech` | `129.146.71.78` |
| Redirect | `auralearn.tech` | → `www.auralearn.tech` (via Nginx) |

### 2.3 Firewall Configuration

**Oracle Cloud VCN Security List — Ingress Rules:**

| Protocol | Port | Purpose |
|----------|------|---------|
| TCP | 22 | SSH Access |
| TCP | 80 | HTTP (redirects to HTTPS) |
| TCP | 443 | HTTPS (main application) |
| TCP | 3000 | Next.js (internal) |
| TCP | 8000 | Summarizer API (internal) |
| TCP | 8001 | Reminder/Auth API (internal) |
| TCP | 8002 | LLM Tutor API (internal) |
| TCP | 8004 | Emotion Detection API (internal) |

**OS-level Firewall (`firewalld`) — Allowed Ports:**
`80, 443, 3000, 8000, 8001, 8002, 8004, 5432, 6333, 6379, 9000, 9001`

---

## 3. System Architecture

```
                        Internet
                           │
              ┌────────────▼────────────┐
              │     www.auralearn.tech  │
              │       (Port 80/443)     │
              └────────────┬────────────┘
                           │ HTTPS (TLS 1.2/1.3)
              ┌────────────▼────────────┐
              │     Nginx 1.20.1        │
              │   Reverse Proxy / SSL   │
              └──┬───┬───┬───┬───┬─────┘
                 │   │   │   │   │
        /        │   │   │   │   │  Path-based routing
   ─────────┐    │   │   │   │   │
  Frontend  │  /rem/ /sum/ /tut/ /emo/
  Next.js   │    │   │   │   │
  :3000     │    ▼   ▼   ▼   ▼
            │ :8001 :8000 :8002 :8004
            │   │   │   │   │
   ─────────┘   │   │   │   │
                │   │   │   │
        ┌───────▼───▼───▼───▼──────┐
        │    PM2 Process Manager   │
        │  (Auto-restart on crash) │
        └──────────────────────────┘
                     │
         ┌───────────▼──────────────┐
         │     Docker Services      │
         │  PostgreSQL · Redis      │
         │  Qdrant · MinIO          │
         └──────────────────────────┘
```

---

## 4. Technology Stack

### 4.1 Runtime Versions

| Technology | Version |
|-----------|---------|
| Node.js | v20.20.2 |
| npm | 10.8.2 |
| Python | 3.9.25 |
| Next.js | 16.2.4 |
| Nginx | 1.20.1 |
| Docker | (current stable) |

### 4.2 Key Libraries & Frameworks

| Component | Stack |
|-----------|-------|
| Frontend | Next.js 16, React, Tailwind CSS |
| Backend APIs | FastAPI, Uvicorn, Pydantic v2 |
| ML / AI | PyTorch 2.8.0, MediaPipe 1.0.1, scikit-learn |
| Computer Vision | OpenCV 5.0.0 (headless) |
| Database | PostgreSQL 16, MongoDB Atlas |
| Cache / Queue | Redis 7 |
| Vector DB | Qdrant v1.13.2 |
| Object Storage | MinIO |
| Process Manager | PM2 |
| SSL | Let's Encrypt (Certbot 3.1.0) |

---

## 5. Microservices Deployment

### 5.1 Service Overview

| # | Service | Technology | Port | PM2 Name | Status |
|---|---------|-----------|------|----------|--------|
| 1 | **Frontend** | Next.js 16 | 3000 | `frontend` | ✅ Online |
| 2 | **Summarizer Backend** | FastAPI + Celery | 8000 | `summarizer-backend` | ✅ Online |
| 3 | **Adaptive Reminder / Auth** | FastAPI | 8001 | `adaptive-reminder-backend` | ✅ Online |
| 4 | **LLM Tutor Backend** | FastAPI | 8002 | `llm-tutor-backend` | ✅ Online |
| 5 | **Emotion Detection Backend** | FastAPI + PyTorch | 8004 | `emotion-backend` | ✅ Online |
| 6 | **Summarizer Celery Worker** | Celery | — | `summarizer-celery` | ✅ Online |

### 5.2 Service Details

#### 5.2.1 Frontend (Next.js)
- **Path:** `/home/opc/R26-SE-022/Frontend`
- **Build Command:** `npm run build`
- **Start Command:** `next start -p 3000`
- **Build Output:** `.next/` (21 MB)
- **Features:** Server-side rendering, static generation, emotion-aware UI, adaptive study sessions, tutor chat, materials upload

#### 5.2.2 Summarizer Backend
- **Path:** `/home/opc/R26-SE-022/summarizer-backend`
- **Framework:** FastAPI + Uvicorn + Celery
- **Database:** PostgreSQL (Docker) + MinIO (object storage)
- **Disk Usage:** 1.5 GB (includes ML models)
- **Key Routes:** `/api/v1/documents/upload`, `/api/v1/modules`, `/api/v1/summaries`

#### 5.2.3 Adaptive Reminder / Auth Backend
- **Path:** `/home/opc/R26-SE-022/adaptive-reminder-system/backend`
- **Framework:** FastAPI + Uvicorn
- **Database:** MongoDB Atlas (cloud)
- **Disk Usage:** 448 MB
- **Key Routes:** `/api/v1/auth/login`, `/api/v1/auth/signup`, `/api/v1/reminders`, `/api/v1/scheduler/decide`

#### 5.2.4 LLM Tutor Backend
- **Path:** `/home/opc/R26-SE-022/llm-tutor-backend`
- **Framework:** FastAPI + Uvicorn
- **Database:** Qdrant (vector DB), MinIO
- **Disk Usage:** 1.1 GB
- **Key Routes:** `/api/chat`, `/api/ingest`, `/api/retrieve`, `/api/analytics`

#### 5.2.5 Emotion Detection Backend
- **Path:** `/home/opc/R26-SE-022/Backend`
- **Framework:** FastAPI + Uvicorn
- **ML Stack:** PyTorch 2.8.0 (CPU), MediaPipe 1.0.1, OpenCV 5.0.0, scikit-learn Random Forest
- **Disk Usage:** 1.2 GB (includes face_landmarker.task model)
- **Key Routes:** `/api/detect-emotion`, `/api/health`
- **Dependencies Installed:** libEGL, libGLES (Mesa) for headless MediaPipe support

---

## 6. Infrastructure Services (Docker)

| Container | Image | Status | Ports |
|-----------|-------|--------|-------|
| `loa-ess-postgres` | `postgres:16-alpine` | ✅ Healthy | 5432 |
| `loa-ess-redis` | `redis:7-alpine` | ✅ Healthy | 6379 |
| `loa-ess-qdrant` | `qdrant/qdrant:v1.13.2` | ✅ Running | 6333–6334 |
| `loa-ess-minio` | `minio/minio:latest` | ✅ Healthy | 9000–9001 |

---

## 7. Nginx Configuration

Nginx acts as the single entry point for all traffic, handling SSL termination, HTTP→HTTPS redirection, and path-based API routing.

### 7.1 Routing Rules

| Path | Proxies To | Purpose |
|------|-----------|---------|
| `https://www.auralearn.tech/` | `http://localhost:3000` | Next.js Frontend |
| `https://www.auralearn.tech/reminder/` | `http://localhost:8001` | Auth & Reminder API |
| `https://www.auralearn.tech/summarizer/` | `http://localhost:8000` | Summarizer API |
| `https://www.auralearn.tech/tutor/` | `http://localhost:8002` | LLM Tutor API |
| `https://www.auralearn.tech/emotion/` | `http://localhost:8004` | Emotion Detection API |
| `http://auralearn.tech/*` | → `https://www.auralearn.tech` | Apex redirect |
| `http://www.auralearn.tech/*` | → `https://www.auralearn.tech` | HTTP → HTTPS |

### 7.2 Cache Policy
| Asset Type | Cache Behaviour |
|------------|----------------|
| `/_next/static/*` | `Cache-Control: public, immutable` (1 year) |
| HTML / JSON pages | `Cache-Control: no-store` (always fresh) |

---

## 8. SSL / TLS Configuration

| Property | Value |
|----------|-------|
| **Certificate Authority** | Let's Encrypt (ISRG) |
| **Certificate Type** | ECDSA |
| **Domain Covered** | `www.auralearn.tech` |
| **Issue Date** | 2026-09-06 |
| **Expiry Date** | 2026-12-05 |
| **Validity Period** | 89 days (standard Let's Encrypt) |
| **Auto-Renewal** | ✅ Configured via `certbot-renew` cron |
| **Protocols** | TLS 1.2, TLS 1.3 |
| **HTTP → HTTPS** | ✅ 301 Redirect active |

---

## 9. Environment Configuration

### 9.1 Frontend Environment Variables (`.env.local`)

```env
NEXT_PUBLIC_SUMMARIZER_API_URL=https://www.auralearn.tech/summarizer
NEXT_PUBLIC_API_URL=https://www.auralearn.tech/reminder
NEXT_PUBLIC_TUTOR_API_URL=https://www.auralearn.tech/tutor
NEXT_PUBLIC_EMOTION_API_URL=https://www.auralearn.tech/emotion
```

> All API calls from the browser go through Nginx over HTTPS, eliminating mixed-content and CORS issues.

### 9.2 CORS Policy
All backend services are configured to accept requests from `https://www.auralearn.tech`.

---

## 10. End-to-End Health Verification

All endpoints were verified live immediately after deployment:

| Endpoint | Method | Expected | Result |
|----------|--------|----------|--------|
| `https://www.auralearn.tech/` | GET | 200 OK | ✅ 200 OK |
| `https://www.auralearn.tech/reminder/api/v1/auth/login` | POST | 401 (no creds) | ✅ 401 Unauthorized |
| `https://www.auralearn.tech/reminder/api/v1/auth/signup` | POST | 200 + token | ✅ 200 OK |
| `https://www.auralearn.tech/summarizer/health` | GET | 200 OK | ✅ 200 OK |
| `https://www.auralearn.tech/tutor/health` | GET | 200 OK | ✅ 200 OK |
| `https://www.auralearn.tech/emotion/api/health` | GET | 200 OK | ✅ 200 OK |

> **Note:** The 401 on the login endpoint is the expected response when no credentials are provided. A valid login returns a JWT bearer token (`200 OK`).

---

## 11. Deployment Challenges & Resolutions

| # | Challenge | Root Cause | Resolution |
|---|-----------|-----------|------------|
| 1 | **Port 80/443 unreachable externally** | Oracle Cloud VCN Security List blocked ports (separate from OS firewall) | Added ingress rules in OCI Console for ports 80, 443, 3000–9001 |
| 2 | **CORS blocked on sign-in** | Backend CORS config only allowed `localhost` | Updated `CORS_ORIGINS` in all backend `.env` files to include the VM's public IP and domain |
| 3 | **Nginx failed to start (port 8444)** | Previous config tried to bind privileged port 8444 without SELinux permissions | Rewrote config to use only standard ports 80/443 with path-based routing |
| 4 | **SELinux blocked Nginx→Backend proxying** | `httpd_can_network_connect` SELinux boolean was `off` | `sudo setsebool -P httpd_can_network_connect 1` |
| 5 | **MediaPipe `libEGL.so.1` missing** | Oracle Linux 9 headless server lacks OpenGL ES libraries | Installed `libglvnd-egl`, `mesa-libEGL`, `libglvnd-gles` via DNF |
| 6 | **Certbot not available via snap/default EPEL** | snapd not supported on Oracle Linux ARM | Enabled `oracle-epel-release-el9`, installed certbot via DNF |
| 7 | **ChunkLoadError after frontend rebuild** | Browser cached old HTML referencing old hashed JS chunk filenames | Hard refresh (Cmd+Shift+R); added `Cache-Control: no-store` header in Nginx for HTML |
| 8 | **numpy version conflict (sklearn vs mediapipe)** | mediapipe 1.0.1 upgraded numpy to 2.0.2; scikit-learn 1.4.0 requires `numpy<2.0` | Pinned `numpy<2.0` for scikit-learn compatibility |

---

## 12. Process Management (PM2)

All services are managed by PM2 with:
- ✅ **Auto-restart** on crash
- ✅ **Startup persistence** — `pm2 save` + startup hook configured (survives VM reboot)
- ✅ **Log management** at `/home/opc/.pm2/logs/`

### PM2 Process Summary at Submission

| PM2 ID | Name | Status | Uptime | Memory | Restarts |
|--------|------|--------|--------|--------|----------|
| 4 | `frontend` | ✅ online | 11 min* | 70.7 MB | 2 |
| 5 | `summarizer-backend` | ✅ online | 2 days | 37.6 MB | 1 |
| 6 | `summarizer-celery` | ✅ online | — | 35.7 MB | 543 |
| 7 | `llm-tutor-backend` | ✅ online | 2 days | 35.0 MB | 0 |
| 8 | `adaptive-reminder-backend` | ✅ online | 2 days | 35.5 MB | 3 |
| 9 | `emotion-backend` | ✅ online | 20 min* | 288.5 MB | 70** |

> *Restarted during final rebuild / HTTPS migration  
> **emotion-backend restarts occurred during dependency resolution (libEGL/libGLES installation); stable post-fix

---

## 13. Security Summary

| Measure | Status |
|---------|--------|
| HTTPS enforced (TLS 1.2/1.3) | ✅ |
| HTTP → HTTPS redirect | ✅ |
| SSL auto-renewal | ✅ |
| Secrets in `.env` files (not in code) | ✅ |
| SELinux enforcing mode | ✅ |
| OS firewall (firewalld) | ✅ |
| OCI VCN Security List | ✅ |
| JWT-based authentication | ✅ |
| No root services (running as `opc`) | ✅ |

---

## 14. Access Information

| Resource | URL |
|----------|-----|
| 🌐 **Live Application** | https://www.auralearn.tech |
| 📄 Summarizer API Docs | https://www.auralearn.tech/summarizer/docs |
| 🔔 Reminder API Docs | https://www.auralearn.tech/reminder/docs |
| 🤖 LLM Tutor API Docs | https://www.auralearn.tech/tutor/docs |
| 😊 Emotion API Docs | https://www.auralearn.tech/emotion/docs |
| 🗄️ MinIO Console | http://129.146.71.78:9001 |

### Demo Account
| Field | Value |
|-------|-------|
| Email | `demo@auralearn.tech` |
| Password | `Demo1234!` |

---

## 15. Conclusion

The AuraLearn platform was successfully deployed end-to-end on Oracle Cloud Infrastructure. All five microservices are operational, served securely over HTTPS through a unified Nginx reverse proxy at `https://www.auralearn.tech`. The system handles authentication, AI-powered summarization, adaptive reminders, LLM-based tutoring, and real-time emotion detection — all running on a single cost-effective ARM64 cloud instance.

---

*Report prepared for academic submission — R26-SE-022*
