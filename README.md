# MaternalMate – AI-Based Maternal Care Monitoring System

MaternalMate is an AI-powered maternal healthcare monitoring platform that assists pregnant women by predicting pregnancy-related health risks and analyzing medical reports using Machine Learning and Generative AI.

The system classifies maternal health risks into **Low Risk**, **Medium Risk**, and **High Risk** categories based on vital health parameters such as blood pressure, blood glucose, body temperature, heart rate, and age. Additionally, it integrates **Google Gemini AI** to analyze uploaded medical reports and ultrasound reports and generate simplified patient-friendly summaries.

---

## Features

### Maternal Health Risk Prediction

* Predicts maternal health risk levels in real-time.
* Classifies patients into:

  * Low Risk
  * Medium Risk
  * High Risk
* Supports early detection of pregnancy-related complications.

### 📊 Health Monitoring Dashboard

* Pregnancy journey tracking.
* Health status monitoring.
* Blood pressure trend visualization.
* Radar chart comparison with normal ranges.

### 📄 AI-Based Medical Report Analysis

* Upload reports in PDF, JPG format.
* AI-powered report interpretation using Gemini API.
* Extraction of key medical parameters.
* Simplified summaries for easier understanding.

### Secure User Authentication

* User registration and login.
* Personalized health records.
* Secure data management.

### 📈 Data Visualization

* Interactive health analytics dashboard.
* Graphical representation of vital signs.
* Trend monitoring and health insights.

---

## System Architecture

```text
User Dashboard
│
├── Log Health Vitals
│   ├── Data Validation
│   ├── Data Preprocessing
│   ├── Machine Learning Model
│   └── Risk Prediction
│
├── Upload Medical Report
│   ├── Report Processing
│   ├── Gemini AI Analysis
│   └── Summary Generation
│
└── Results Dashboard
    ├── Risk Classification
    ├── Health Analytics
    └── AI Report Summary
```

---

##  Machine Learning Model Used

The system evaluates supervised learning algorithm Random Forest

Model performance is evaluated using:

* Accuracy
* Precision
* Recall
* F1-Score

---


### Dataset Source

* Maternal Health Risk Dataset (Kaggle)

---

## Tech Stack

### Frontend

* HTML5
* CSS3
* Tailwind CSS


### Backend

* Django
* Python

### Machine Learning

* Scikit-Learn
* Pandas
* NumPy

### Database

* PostgreSQL

### Visualization

* Matplotlib
* Seaborn
* Chart.js

### Generative AI

* Google Gemini API

---

## Project Modules

### Dashboard

* Pregnancy Journey Tracking
* Health Status Monitoring
* Health Analytics

### Health Vitals Module

* Age
* Blood Pressure
* Blood Glucose
* Body Temperature
* Heart Rate

### Risk Prediction Module

* AI-based risk classification
* Health insights

### Report Analysis Module

* PDF/Image upload
* AI-generated summaries
* Abnormality detection

---
