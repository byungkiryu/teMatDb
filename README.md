### 👋 I am Byungki Ryu  
From the **ThermoElectric Physics and Science (TES)** Team at **KERI**, Changwon, Korea.

Although many papers have reported thermoelectric properties,  the material space remains highly fragmented, making it difficult to develop a unified understanding of **thermoelectric transport**. 

As a **theoretical physicist**, I have been deeply motivated by this challenge. 

Over the past decade, I have worked to develop an  **ultra-high-quality database for thermoelectric materials**. 

This effort led to the creation of:
- 🧪 **teMatDb v1.1.6**, a whole DB system
- 🔎 **Self-consistent ZT filtering protocol**, developed filters for data self-consistency  
- 🧪 **teMatDb272**, an ultra-high quality TE dataset

These tools have also been applied to the world's largest thermoelectric database, **Starrydata2**.

📢 The **method and protocol** behind this high-fidelity database and filtering approach will be **published soon**.

---

### Key data set for teMatDb v1.1.6
0) metadata for digitized TEP sets:      ./_tematdb_v1.1.6_metadata-20250514.xlsx
1) raw excel file containing TEP pairs digitized from literature:      ./data_00_tematdb_raw_excel/_tematdb_tep_excel_v1.1.6_{:05d}-{:05d}.xlsx
2) formatted single csv file from excels:      ./data_10_tematdb_csv_converted/tematdb_v1.1.6_completeTEPset.csv
3) extended TEP at every 2K (extended and formatted TEP sets, interpolated, extrapolated at every 2K):      ./data_30_tematdb_extTEP_csv/tematdb_v1.1.6_extendedTEPset_dT2K.csv
4) ZT errors over temperature ranges:      ./data_40_tematdb_ZT_error/ZT_error.csv
5) human error uncertainty measure:      ./data_90_human_digital_error_measure/digitized.xlsx

### Key data set for Starrydata2 (20250201_rawdata) in [postprocessed_Starrydata2_20250501/]
1) tep files in feather format:      100_teps/20250501_rawdata_{TEPS}.feather
2) extended TEPs at every 4K:      300_extended_teps/extendedZTset_4K.feather
3) ZT errors over temperature ranges: :      400_ZT_error/ZT_error_table.csv
4) Sc-ZT and classical filtering tables: :      500_filter_table_classical_and_scZT/crieria_02_02_02_02_04_04_results_filtered_scZT.csv
9) metadata:      999_Starrydata2_rawdata_meta/starrydata_dataset_250501-0300_meta_samples-scZT_clas_filteres-20250515_232713.xlsx 


---

### 📦 teMatDb272: Published Dataset (2025) — to be submitted in a journal*

This is the curated dataset used in the manuscript:

📄 *teMatDb: A High-Quality Thermoelectric Material Database with Self-Consistent ZT Filtering*  
📅 Submitted: May 2025 
🔗 DOI: *(to be updated after acceptance)*  
🌐 Streamlit Viewer: https://tematdb.streamlit.app/  
🧩 Source code: [GitHub repository](https://github.com/byungkiryu/teMatDb)

#### Files included in `./tematdb272_publication/`:

| File                          | Description |
|-------------------------------|-------------|
| `teMatDb_samples.csv`         | Sample metadata: `sample_id`, year, DOI, composition, group, dimension, etc. |
| `teMatDb_rawTEPs.csv`         | Digitized raw TEP values (`α`, `ρ`, `κ`, `ZT`) with temperature |
| `teMatDb_collocatedTEPs.csv`  | Interpolated TEPs at 2 K intervals for Sc-ZT error evaluation |
| `z_teMatDb_report.txt`        | DB summary and filtering criteria |

---

### 🧠 What is Sc-ZT Filtering?

The **self-consistent ZT (Sc-ZT) filtering protocol** compares:
- Reported `ZT_fig` from figures  
- Recalculated `ZT_TEP` from digitized α(T), ρ(T), κ(T)

This enables detection of:
- Digitization noise  
- Fitting-induced bias  
- Publication/extrapolation errors

ZT error is computed as:  
`δ(ZT) = ZT_fig − ZT_TEP`

---

### 📊 Included Datasets

| Dataset         | Samples | Description |
|-----------------|---------|-------------|
| `teMatDb272`     | 272     | Final filtered data (default: `0.1, 0.1, 0.1, 0.1, 0.2, 0.2`) |
| `starryz10840`   | 10,840  | Sc-ZT filtered *Starrydata2* |
| `starryz15053`   | 15,053  | Classical filtered version |
| `starryz15532`   | 15,532  | Unfiltered raw subset |

📎 Download all `starryz` datasets from Figshare:  
**[https://figshare.com/s/50a78a58d6a84a5b6302](https://figshare.com/s/50a78a58d6a84a5b6302)**

📎 See `Supporting Table S3` for full statistics.

---

### 🧭 What’s Next?

We are currently developing **`teMatDb_expt`**,  
a structured repository for experimental thermoelectric data,  
designed to support multi-lab, multi-device integration and benchmarking.

---

### 💡 Citation

When citing this dataset, please refer to:

> **Byungki Ryu et al.**,  
> *teMatDb: A High-Quality Thermoelectric Material Database with Self-Consistent ZT Filtering*,  
> Scientific Data (2025), DOI: *(to be added)*

---
