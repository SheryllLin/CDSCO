# 🚀 CDSCO AI Regulatory Workflow Automation

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green?logo=fastapi)
![Status](https://img.shields.io/badge/Status-Production--Ready-success)
![License](https://img.shields.io/badge/License-MIT-yellow)
![AI](https://img.shields.io/badge/AI-NLP%20Pipeline-purple)

---

<p align="center">
  <img src="https://media.giphy.com/media/3o7TKMt1VVNkHV2PaE/giphy.gif" width="500"/>
</p>

<p align="center">
  <b>AI-powered regulatory workflow engine for CDSCO-style drug review systems</b><br>
  Transforming raw submissions → structured intelligence → human-readable reports
</p>

---

## 🧠 What This Project Does

This system simulates **CDSCO regulatory workflows** (like SUGAM / MD Online) and enhances them with AI.

> ⚠️ Supports decision-making — does NOT replace regulatory authority

---

## ✨ Features

### 🔐 Data Anonymisation Engine
- Token-based pseudonymisation
- Irreversible anonymisation
- DPDP Act aligned design

---

### 🧾 Document Intelligence
- SAE narrative summarisation  
- Clinical text extraction  
- Inspection notes processing  

---

### ✅ Validation Engine
- Completeness scoring  
- Missing field detection  
- Cross-check form vs text  

---

### ⚠️ Severity Classification
- Mild / Moderate / Severe / Fatal  
- Upgrade-ready ML pipeline  

---

### 🔁 Duplicate Detection
- Fuzzy similarity matching  
- Future: SBERT embeddings  

---

### 📊 Document Comparison
- Version difference detection  
- Change tracking  

---

### 📄 Automated Report Generation
- Regulatory evaluation reports  
- Inspection summaries  
- Non-technical output  

---

## 🏗️ Architecture Diagram

```mermaid
flowchart TD

A[User Input] --> B[API Layer - FastAPI]

B --> C1[Anonymisation Service]
B --> C2[Summarisation Engine]
B --> C3[Validation Engine]
B --> C4[Classification Engine]
B --> C5[Deduplication Engine]
B --> C6[Comparison Engine]

C1 --> D[Pipeline Orchestrator]
C2 --> D
C3 --> D
C4 --> D
C5 --> D
C6 --> D

D --> E[Report Generator]

E --> F[Final Regulatory Report PDF]
