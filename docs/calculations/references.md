# Calculation References

## Standards Implemented

| Standard | Title | Module | Status |
|----------|-------|--------|--------|
| BS 8004:2015 | Code of practice for foundations | Foundation | Phase 1 |
| BS 8110:1997 | Structural use of concrete | Structural | Phase 1 |
| BS 5930:2015 | Ground investigations | Soil | Phase 1 |
| BS 6399:1996 | Loading for buildings | Load Combinations | Phase 1 |
| EN 1990:2002 | Basis of structural design | Load Combinations | Phase 1 |
| EN 1992-1-1:2004 | Design of concrete structures | Structural | Phase 1 |
| EN 1997-1:2004 | Geotechnical design | Foundation | Phase 1 |
| ISO 14688 | Soil identification & classification | Soil | Phase 1 |

## Calculation Methods

### Bearing Capacity
- **Terzaghi (1943)** — Classical method, widely used, conservative
- **Meyerhof (1963)** — General equation with shape and depth factors
- **Vesic (1973)** — Modified factors, commonly used in Eurocode practice

### Foundation Selection
Decision tree based on:
1. Soil category (rock/granular/clay/organic)
2. Bearing capacity (kPa)
3. Building loads (kN)
4. Number of stories
5. Water table depth
6. Slope angle
7. Expansive soil flag

### Structural Design
- Beam: BS 8110 Cl.3.4.4 (bending), Cl.3.4.5 (shear), Cl.3.4.6 (deflection)
- Column: BS 8110 Cl.3.8.4 (short braced), Cl.3.12.5 (reinforcement)
- Load combinations: EN 1990 Eq.6.10

### Pile Capacity
- Shaft friction (clay): Alpha method — alpha * cu * As
- Shaft friction (sand): Beta method — K * sigma_v' * tan(delta) * As
- End bearing (clay): Nc * cu * Ab (Nc = 9)
- End bearing (sand): Meyerhof SPT correlation

## Textbook References
- Craig's Soil Mechanics (8th ed.) — Bearing capacity theory
- Tomlinson's Foundation Design & Construction — Foundation selection
- Tomlinson's Pile Design & Construction Practice — Pile capacity
- Reynolds's Reinforced Concrete Designer's Handbook — BS 8110 design
- Mosley, Bungey & Hulse — Reinforced Concrete Design to BS 8110
