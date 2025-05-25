# teMatDb272: High-Quality Thermoelectric Material Dataset with Self-Consistent ZT Filtering

This repository contains curated temperature-dependent thermoelectric property data (TEPs) including Seebeck coefficient (α), electrical resistivity (ρ), thermal conductivity (κ), and figure of merit (ZT), collected and digitized from the literature.

The Sc-ZT filtering protocol is applied to remove inconsistencies between reported ZT values and those recalculated from digitized TEPs.

🔗 [Streamlit Viewer](https://tematdb.streamlit.app/)  
📄 [Publication (link to be added)]()  
📁 Version: `teMatDb272` | DB Release Date: `2025-05-15`

---

## Contents
- `teMatDb_samples.csv` — Sample metadata
- `teMatDb_rawTEPs.csv` — Raw digitized TEP data
- `teMatDb_collocatedTEPs.csv` — Interpolated TEP data (2K grid)
- `z_teMatDb_report.txt` — DB statistics and filtering log
- `filter/` — Python scripts for Sc-ZT filtering
- `collocate/` — Temperature collocation code



### 📚 DB Publication Records

| DB Publication ID | # of TEP Sets | Mother DB       | Timestamp           | sc-ZT Filter Criteria       |
|-------------------|---------------|------------------|----------------------|-----------------------------|
| teMatDb272        | 272           | teMatDb v1.1.6   | 20250515_134730      | criteria_10_10_10_10_20_20  |
