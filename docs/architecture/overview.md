# CivilEng Architecture Overview

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Mobile App    │    │   Web Dashboard │    │   API Clients   │
│  (React Native) │    │   (Next.js)     │    │  (ETABS/CAD)    │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │    FastAPI Backend     │
                    │   (Python Engine)      │
                    │                        │
                    │  ┌──────────────────┐  │
                    │  │  Calculation      │  │
                    │  │  Engine           │  │
                    │  │  - Foundation     │  │
                    │  │  - Structural     │  │
                    │  │  - Soil           │  │
                    │  │  - Materials      │  │
                    │  └──────────────────┘  │
                    │                        │
                    │  ┌──────────────────┐  │
                    │  │  Report Engine    │  │
                    │  │  - PDF/DOCX gen  │  │
                    │  │  - DXF export    │  │
                    │  └──────────────────┘  │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │    PostgreSQL DB       │
                    │  - Projects           │
                    │  - Site data          │
                    │  - Design results     │
                    └───────────────────────┘
```

## Calculation Engine Design Principles

1. **Every calculation is traceable to a code clause** — BS 8004, BS 8110, EN 1997, etc.
2. **Intermediate steps are always returned** — any engineer can verify the math
3. **Pass/fail criteria are explicit** — no ambiguity
4. **Conservative defaults** — when in doubt, round down capacity, round up loads
5. **No AI in the calculation path** — pure codified mathematics, 100% auditable

## API Design

All calculation endpoints follow the same pattern:
- **POST** with JSON input → JSON output
- Output includes: result, intermediate_steps, code_reference, pass/fail status
- Every number can be traced back to a specific standard clause

## Data Model

```
Project
  ├── Site (location, coordinates, terrain)
  │     └── SoilProfile (layers, parameters)
  │           └── SoilClassification
  ├── FoundationDesign
  │     ├── BearingCapacity
  │     ├── FoundationType (selected)
  │     └── FoundationSizing
  ├── StructuralDesign
  │     ├── LoadCombinations
  │     ├── BeamDesign (multiple)
  │     ├── ColumnDesign (multiple)
  │     └── SlabDesign (multiple)
  ├── MaterialQuantities (BOQ)
  └── Reports (PDF/DOCX generated)
```
