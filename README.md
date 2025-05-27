## 👋 I am Byungki Ryu  
From the **ThermoElectric Physics and Science (TES)** Team at **KERI**, Changwon, Korea.
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15518036.svg)](https://doi.org/10.5281/zenodo.15518036)


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

## 📦 teMatDb272: Published Dataset (2025) — *Published on arXiv*, to be submitted to *Scientific Data*

This is the curated dataset used in the following manuscript:

📄 *teMatDb: A High-Quality Thermoelectric Material Database with Self-Consistent ZT Filtering*  
📅 Submitted: 25 May 2025  
📚 [arXiv:2505.19150](https://doi.org/10.48550/arXiv.2505.19150)

---

## 📁 Key data directories (internal file map)

### 🔸 teMatDb v1.1.6

- Metadata:  
  `./_tematdb_v1.1.6_metadata-20250514.xlsx`

- Raw Excel (digitized):  
  `./data_000_tematdb_raw_excel/tematdb_tep_excel_v1.1.6_{:05d}-{:05d}.xlsx`

- Raw CSV converted in a single file:  
  `./data_100_tematdb_csv_converted/tematdb_v1.1.6_completeTEPset.csv`

- Extended TEP (2 K spacing), it is also called as collocatedTEP:  
  `./data_300_tematdb_extTEP_csv/tematdb_v1.1.6_extendedTEPset_dT2K.csv`

- ZT error curves:  
  `./data_400_tematdb_ZT_error/ZT_error.csv`

- Human digitization error test:  
  `./data_080_human_digital_error_measure/digitized.xlsx`

- Published teMatDb272:  
  `./teMatDb_publication/teMatDb272_dataset_20250515/*`
---


### 🔸 Starrydata2 subset (processed version: 20250501)

Located in:  
`./postprocessed_Starrydata2_20250501/`

- Raw TEPs (feather):  
  `100_teps/20250501_rawdata_{TEPS}.feather`

- Extended TEPs (4 K grid) (owing to size limit, only ZT shown):  
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
https://figshare.com/s/50a78a58d6a84a5b6302 (to be updated later as a persistent doi and link)

📎 See Table 3 and Supporting Table S3 in the manuscript for full statistics.

---

### 🧭 What’s Next?

We are currently developing **`teMatDb_expt`**,  
a structured repository for experimental thermoelectric data,  
designed to support multi-lab, multi-device integration and benchmarking.

---

### 💡 How to Cite

When citing this dataset or the related paper, please refer to:

> **Byungki Ryu, Ji Hui Son, Sungjin Park, Jaywan Chung, Hye-Jin Lim, SuJi Park, Yujeong Do, SuDong Park**,  
> *teMatDb: A High-Quality Thermoelectric Material Database with Self-Consistent ZT Filtering*,  
> arXiv:2505.19150 [cond-mat.mtrl-sci] (2025).  
> [https://doi.org/10.48550/arXiv.2505.19150](https://doi.org/10.48550/arXiv.2505.19150)  
>  
> DOI for dataset: [https://doi.org/10.5281/zenodo.15518036](https://doi.org/10.5281/zenodo.15518036)

---

## 📄 License

- Code in this repository (excluding the [`pykeri`](https://github.com/byungkiryu/teMatDb/tree/main/pykeri) subdirectory):  
  Licensed under the [MIT License](LICENSE)
- Data files (e.g., `teMatDb272.csv` and other TEP curve sets):  
  © 2025 Byungki Ryu, distributed under the [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)
- The [`pykeri`](https://github.com/byungkiryu/teMatDb/tree/main/pykeri) module is developed and maintained separately, and is subject to its own license.

