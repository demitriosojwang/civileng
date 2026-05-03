# CivilEng — AI-Powered Foundation & Structural Design Software

> Intelligent construction analysis platform that transforms site data into comprehensive foundation and structural design solutions, streamlining tendering and improving accuracy.

## Overview

CivilEng simplifies and improves the pre-tender site visit process by using structured digital data capture and codified engineering calculations to determine the most suitable foundation type and structural requirements for construction projects.

### Core Problem
Site engineers already know how to classify soil and select foundations — the knowledge exists in BS 8004, Eurocode 7, and every geotechnical textbook. What's missing is a fast, structured, digital way to apply that knowledge on-site and feed it directly into calculations and reports without retyping everything three times.

**That's a software problem, not an AI problem.**

### Strategy
1. **Build first** on codified engineering mathematics (no AI) — fully auditable from day one
2. **Acquire users** and accumulate real project outcome data
3. **Add AI later** trained on your proprietary dataset — making it genuinely defensible

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Python / FastAPI | Calculation engine + API |
| **Database** | PostgreSQL | Project, site, and design data |
| **Web Frontend** | Next.js / React | Dashboard & design interface |
| **Mobile** | React Native | On-site data capture |
| **Export** | ReportLab / python-docx | PDF & DOCX report generation |
| **CAD** | ezdxf / ifcopenshell | DXF & IFC interoperability |

## Project Phases

| Phase | Months | Focus |
|-------|--------|-------|
| **0** | 1-3 | Foundation & Validation |
| **1** | 4-7 | Core Calculation Engine |
| **2** | 8-11 | Digital Site Capture |
| **3** | 12-15 | Design Automation & Optimization |
| **4** | 16-19 | Integration & Interoperability |
| **5** | 20-23 | Beta Launch & Market Entry |
| **6** | 24-30 | AI Layer (Data Moat) |
| **7** | 31-36 | Scale & Expansion |

## Quick Start

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend setup
cd frontend
npm install
npm run dev

# Mobile setup
cd mobile
npm install
npx expo start
```

## Supported Standards

- BS 8004 — Code of practice for foundations
- BS 8110 — Structural use of concrete
- BS 5930 — Code of practice for ground investigations
- BS 6399 — Loading for buildings
- EN 1990-1997 — Eurocodes (EC0-EC7)
- ISO 14688 — Geotechnical identification and classification

## Target Users

- Quantity Surveyors
- Civil Engineers
- Structural Engineers
- Contractors
- Tendering Specialists
- Real Estate Developers

## License

Proprietary — All rights reserved.
