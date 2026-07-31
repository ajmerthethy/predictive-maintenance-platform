# Predictive Maintenance Platform

An AI-powered industrial predictive maintenance system that helps organizations monitor equipment health, detect potential failures before downtime occurs, and optimize maintenance workflows.

## 🚀 Overview

Industrial equipment failures can cause significant downtime, production losses, and unexpected maintenance costs.

This platform uses machine learning and sensor analytics to predict equipment failure risk, provide explainable insights, generate alerts, and manage maintenance actions through an integrated dashboard.

The goal is to enable proactive maintenance decisions by transforming equipment sensor data into actionable intelligence.

---

# ✨ Features

## 🏭 Asset Monitoring

* Multi-machine fleet management
* Individual asset health profiles
* Machine operating status tracking
* Sensor history visualization

Supported equipment examples:

* CNC Machines
* Hydraulic Pumps
* Industrial Turbines
* Air Compressors
* Conveyor Systems

---

## 🤖 AI Failure Prediction

Machine learning models analyze equipment sensor data to estimate failure probability.

The system provides:

* Failure risk percentage
* Machine health score
* Risk classification

  * 🟢 Healthy
  * 🟡 Warning
  * 🔴 Critical

---

## 🔍 Explainable AI

Predictions are supported with model explanations:

* Feature importance analysis
* Sensor condition impact
* Identification of contributing factors

This helps maintenance teams understand **why** a machine is considered high risk.

---

## 🚨 Intelligent Alert System

Automatically generates maintenance alerts based on predicted failure risk.

Capabilities:

* Alert severity classification
* Recommended maintenance actions
* Alert acknowledgement
* Alert resolution tracking
* Alert history

---

## 🛠 Maintenance Work Orders

Integrated maintenance workflow:

* Create maintenance tasks
* Link tasks to machine alerts
* Assign technicians
* Track progress

  * OPEN
  * IN_PROGRESS
  * COMPLETED

---

## 📊 Fleet Risk Dashboard

Interactive dashboard providing:

* Overall fleet health
* Machine risk ranking
* Failure probability visualization
* Active alerts
* Maintenance activity tracking

---

# 🏗 System Architecture

```
                    User
                     |
                     v
          Streamlit Dashboard
                     |
                     v
              FastAPI Backend
                     |
                     v
          PostgreSQL Database
                     |
                     v
        Machine Learning Pipeline
```

---

# 🧰 Technology Stack

## Backend

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* Alembic

## Machine Learning

* Scikit-learn
* Pandas
* NumPy
* SHAP explainability

## Dashboard

* Streamlit
* Plotly
* Pandas

## Infrastructure

* Docker
* Docker Compose
* GitHub

---

# 📂 Project Structure

```
predictive-maintenance-platform/

├── backend/
│   ├── app/
│   │   ├── routers/
│   │   ├── models/
│   │   ├── services/
│   │   └── ml/
│   ├── Dockerfile
│   └── requirements.txt
│
├── dashboard/
│   ├── streamlit_app.py
│   └── Dockerfile
│
├── alembic/
│
├── datasets/
│
├── scripts/
│
├── tests/
│
├── docker-compose.yml
└── README.md
```

---

# 🌿 Branching

`main` is the single source of truth for both GitHub issue automation and Railway deployment — branch from `main` for new work and merge back into it directly; don't accumulate work on a long-lived parallel branch. (Earlier history briefly diverged onto a `production-refactor` branch while `main` sat unchanged; that's been reconciled and `main` is once again current.)

---

# ⚙️ Local Installation

## 1. Clone repository

```bash
git clone https://github.com/yourusername/predictive-maintenance-platform.git

cd predictive-maintenance-platform
```

---

## 2. Configure environment variables

Copy `.env.example` to `.env` and fill it in:

```bash
cp .env.example .env
```

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=predictive_maintenance

DATABASE_URL=postgresql://postgres:password@db:5432/predictive_maintenance

JWT_SECRET_KEY=<generate one - see below>
```

`JWT_SECRET_KEY` is required - the app refuses to start without it (or if it's shorter than 32 characters). There is no default value, on purpose. Generate one with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

See `.env.example` for the full list of supported variables, including optional email-alerting and business-assumption overrides.

---

## 3. Start application

Using Docker:

```bash
docker compose up --build
```

Services:

Dashboard:

```
http://localhost:8501
```

API:

```
http://localhost:8000
```

API Documentation:

```
http://localhost:8000/docs
```

---

# 📈 Example Workflow

1. Equipment sensors generate operational data
2. Machine learning model evaluates failure probability
3. System calculates machine health score
4. High-risk conditions generate alerts
5. Maintenance teams review recommendations
6. Work orders are created and completed

---

# 🎯 Current MVP Capabilities

✅ Machine learning failure prediction
✅ Sensor monitoring
✅ Fleet health dashboard
✅ Explainable AI predictions
✅ Automated alerts
✅ Maintenance workflow management
✅ Dockerized deployment
✅ REST API architecture

---

# 🔮 Future Development

Planned improvements:

* IoT sensor integration
* Real-time streaming data ingestion
* User authentication and roles
* Technician scheduling
* Mobile maintenance application
* Automated maintenance recommendations
* Cloud deployment
* Multi-tenant SaaS architecture

---

# 👨‍💻 Author

Ajmer Thethy

GitHub:
https://github.com/ajmerthethy

---

# 📌 Project Status

**MVP Completed**

The platform is currently being prepared for public deployment and industry validation.
