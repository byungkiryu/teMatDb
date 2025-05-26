## 👋 I am Byungki Ryu  
From the **ThermoElectric Physics and Science (TES)** Team at **KERI**, Changwon, Korea.

Although many papers have reported thermoelectric properties, the material space remains highly fragmented,  
making it difficult to develop a unified understanding of **thermoelectric transport**.

As a theoretical physicist, I have been deeply motivated by this challenge.

Over the past decade, I have worked to develop an **ultra-high-quality database for thermoelectric materials**.

This effort led to the creation of:

- 🧪 **teMatDb v1.1.6** — a full digitized TE database system  
- 🔎 **Self-consistent ZT filtering protocol** — to check ZT–TEP consistency  
- 🧪 **teMatDb272** — a curated, high-quality thermoelectric dataset

These tools have also been applied to the world's largest thermoelectric database, **Starrydata2**.

📢 The method and protocol behind this high-fidelity database and filtering approach will be published soon.

---

## 📁 Key data directories (internal file map)

### 🔸 teMatDb v1.1.6

- Metadata:  
  `./_tematdb_v1.1.6_metadata-20250514.xlsx`

- Raw Excel (digitized):  
  `./data_00_tematdb_raw_excel/tematdb_tep_excel_v1.1.6_{:05d}-{:05d}.xlsx`

- CSV converted:  
  `./data_10_tematdb_csv_converted/tematdb_v1.1.6_completeTEPset.csv`

- Extended TEP (2 K spacing):  
  `./data_30_tematdb_extTEP_csv/tematdb_v1.1.6_extendedTEPset_dT2K.csv`

- ZT error curves:  
  `./data_40_tematdb_ZT_error/ZT_error.csv`

- Human digitization error test:  
  `./data_90_human_digital_error_measure/digitized.xlsx`

---

### 🔸 Starrydata2 subset (processed version: 20250501)

Located in:  
`./postprocessed_Starrydata2_20250501/`

- Raw TEPs (feather):  
  `100_teps/20250501_rawdata_{TEPS}.feather`

- Extended TEPs (4 K grid):  
  `300_extended_teps/extendedZTset_4K.feather`

- ZT error:  
  `400_ZT_error/ZT_error_table.csv`

- Filter results (Classical and Sc-ZT):  
  `500_filter_table_classical_and_scZT/crieria_02_02_02_02_04_04_results_filtered_scZT.csv`

- Metadata:  
  `999_Starrydata2_rawdata_meta/starrydata_dataset_250501-0300_meta_samples-scZT_clas_filteres-20250515_232713.xlsx`

---

## 📦 teMatDb272: Published Dataset (2025) — *submitted to arXiv*, to be submitted to *Scientific Data*

This is the curated dataset used in the manuscript:

📄 *teMatDb: A High-Quality Thermoelectric Material Database with Self-Consistent ZT Filtering*  
📅 Submitted: May 2025  
🔗 DOI: *(to be updated after acceptance)*  
🌐 Streamlit Viewer: https://tematdb.streamlit.app/  
🧩 Source code: [GitHub repository](https://github.com/byungkiryu/teMatDb)

### 🔹 Files in `./tematdb272_publication/teMatDb272_dataset_20250515/`:

| File                          | Description |
|-------------------------------|-------------|
| `teMatDb_samples.csv`         | Sample metadata: `sample_id`, year, DOI, composition, group, dimension, etc. |
| `teMatDb_rawTEPs.csv`         | Raw digitized TEP values (`α`, `ρ`, `κ`, `ZT`) with temperature |
| `teMatDb_collocatedTEPs.csv`  | Interpolated TEPs at 2 K intervals for Sc-ZT error evaluation |
| `z_teMatDb_report.txt`        | DB statistics and filtering criteria |

---

### 🧠 What is Sc-ZT Filtering?

The **Self-consistent ZT filtering protocol** compares:

- `ZT_fig` (from original figure)  
- `ZT_TEP` (recalculated from digitized α(T), ρ(T), κ(T))

This enables detection of:

- Digitization noise  
- Fitting-induced bias  
- Publication or extrapolation error

> 💡 ZT error is computed as:  
> `δ(ZT) = ZT_fig − ZT_TEP`

---

### 📊 Included Datasets

| Dataset         | Samples | Description | Location |
|-----------------|---------|-------------|----------|
| `teMatDb272`     | 272     | Final filtered dataset (default criteria: `0.1, 0.1, 0.1, 0.1, 0.2, 0.2`) | Here |
| `starryz10840`   | 10,840  | Sc-ZT filtered Starrydata2 | figshare.com |
| `starryz15053`   | 15,053  | Classical filtered version | figshare.com |
| `starryz15532`   | 15,532  | Unfiltered raw subset | figshare.com |


📎 **Download all starryz datasets from Figshare**:  
https://figshare.com/s/50a78a58d6a84a5b6302

📎 See Table 3 and Supporting Table S3 in the manuscript for full statistics.

---

### 🧭 What’s Next?

We are currently developing **`teMatDb_expt`**,  
a structured repository for experimental thermoelectric data,  
designed to support multi-lab, multi-device integration and benchmarking.

---

### 💡 How to Cite

When citing this dataset, please refer to:

> **Byungki Ryu et al.**,  
> *teMatDb: A High-Quality Thermoelectric Material Database with Self-Consistent ZT Filtering*,  
> Journal name *(to be added)* (2025), DOI: *(to be added)*

---

## 📄 License

- Code (excluding `pykeri`): [MIT License](LICENSE)
- Data (`teMatDb272.csv` and other TEP curves): © 2025 Byungki Ryu, distributed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- `pykeri` module: Licensed separately; see [pykeri repository](## 📄 License

- Code (excluding `pykeri`): [MIT License](LICENSE)
- Data (`teMatDb272.csv` and other TEP curves): © 2025 Byungki Ryu, distributed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- `pykeri` module: Licensed separately; see [pykeri repository](https://github.com/byungkiryu/teMatDb/tree/main/pykeri) for terms

