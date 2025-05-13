### 👋 I am Byungki Ryu  
From the **ThermoElectric Science (TES)** group at **KERI**, Changwon, Korea.

Although many papers have reported thermoelectric properties,  the material space remains highly fragmented, making it difficult to develop a unified understanding of **thermoelectric transport**. 

As a **theoretical physicist**, I have been deeply motivated by this challenge. 

Over the past decade, I have worked to develop an  **ultra-high-quality database for thermoelectric materials**. 

This effort led to the creation of:
- 🔎 **Self-consistent ZT filter**  
- 🧪 **teMatDb**

These tools have also been applied to the world's largest thermoelectric database, **Starrydata2**.

📢 The **method and protocol** behind this high-fidelity database and filtering approach will be **published soon**.

---

### Key data set for teMatDb v1.1.6
0) metadata for digitized TEP sets:      ./_tematdb_metadata_v1.1.6-20250224.xlsx
1) raw excel file containing TEP pairs digitized from literature:      ./data_00_tematdb_raw_excel/_tematdb_tep_excel_v1.1.6_{:05d}-{:05d}.xlsx
2) formatted single csv file from excels:      ./data_10_tematdb_csv_converted/tematdb_v1.1.6_completeTEPset.csv
3) extended TEP at every 2K (extended and formatted TEP sets, interpolated, extrapolated at every 2K):      ./data_30_tematdb_extTEP_csv/tematdb_v1.1.6_extendedTEPset_dT2K.csv
4) ZT errors over temperature ranges:      ./data_40_tematdb_ZT_error/ZT_error.csv
5) human error uncertainty measure:      ./data_90_human_digital_error_measure/digitized.xlsx

### Key data set for Starrydata2 (20250201_rawdata) in [./postprocessed_Starrydata2_20250210_rawdata__analyzed20250507/]
0) metadata:      999_Starrydata2_rawdata_meta/_Starrydata2_20250201_rawdata_meta_ZTfilterable_.xlsx 
1) tep files in feather format:      100_teps/20250201_rawdata_{TEPS}.feather
2) extended TEPs at every 4K:      300_extended_teps/extendedZTset_4K.feather
3) ZT errors over temperature ranges: :      400_ZT_error/ZT_error_table.csv

---

### 🔜 What’s Next?

I am now developing a data structure for thermoelectric experimental data,  
under the name: **`teMatDb_expt`**


