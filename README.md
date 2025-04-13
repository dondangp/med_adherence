# 💊 Medication Adherence Tracker

## 📘 Overview

The **Medication Adherence Tracker** is a web-based healthcare application that empowers patients to manage their medications, log daily intake, and receive timely reminders. Through adherence insights and visual analytics, the system helps identify gaps in medication routines and encourages consistent usage—crucial for managing chronic conditions.

---

## 🌟 Features

- 🔐 **Secure Login & Authentication**
- 👤 **User Profile Management** (FHIR-compatible patient resource updates)
- 💊 **Medication Management**
  - Add/edit medications
  - Active/inactive status handling
- ☑️ **Daily Medication Checklist**
  - Track medications taken each day
  - Store `MedicationAdministration` records to NDJSON
- 📧 **Email Reminders**
  - Sent automatically at **7 AM, 2 PM, and 7 PM**
  - Includes only *unchecked* daily medications
- 📊 **Analytics & Insights**
  - Daily / Weekly / Monthly adherence rates
  - 30-day individual medication adherence
  - Weekly patterns by day of the week
- 🧠 **AI Medication Insights (Optional)**
  - GPT-powered drug interaction detection
  - Medication info summaries

---

## 🧰 Tech Stack

### 📦 Frontend
- [Streamlit](https://streamlit.io/) – UI framework for real-time interaction

### 🧠 Backend
- **Python** – Core language
- `uuid`, `json`, `datetime`, `smtplib` – for file handling, email, and scheduling

### 🗃 Data Storage
- Local NDJSON files:
  - `Patient.ndjson`
  - `MedicationRequest.ndjson`
  - `MedicationAdministration.ndjson`
  - `AllergyIntolerance.ndjson`, `Condition.ndjson`, `Immunization.ndjson`

### 🔁 Scheduling & Automation
- Custom Python scheduler thread running inside Streamlit app
- Sends **email reminders** using **SMTP (Gmail)**

### 📧 Email Delivery
- Gmail App Password for SMTP
- `email.message.EmailMessage`

---
