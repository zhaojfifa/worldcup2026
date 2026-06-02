# Architecture

## Core Pipeline

DataSource
→ Feature Builder
→ Prediction Engine
→ Explanation Engine
→ Report Generator
→ Frontend API

## Frontend

Mobile-first web app.

Pages:

- Home
- Match Detail
- Report
- Token Center
- Community

## Backend

Suggested stack:

- FastAPI
- PostgreSQL
- SQLAlchemy
- APScheduler or lightweight jobs
- API-FOOTBALL connector
- CSV fallback

## Modeling

MVP uses baseline rules model.

Future upgrade:

- LightGBM
- CatBoost
- SHAP
- Multi-source data fusion
