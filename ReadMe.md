# AI Medical Dispatch System

AI-assisted emergency response platform for triage, ambulance assignment, map-based routing, and medical chat workflows.

## Core Features

- AI triage flow for patient/case prioritization.
- Smart ambulance selection using ETA, distance, and ambulance availability.
- Real-time medical chat endpoint for guided symptom collection.
- Live map support for ambulance and route visualization.
- Voice/workflow endpoints for VAPI-based integrations.
- Admin endpoints for operational data and system prompt management.

## Tech Stack

- Backend: Python, FastAPI, SQLAlchemy
- Frontend: React (Create React App), Redux
- Database: MySQL (current backend configuration uses `mysql+pymysql`)
- External services: Google Maps APIs

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js + npm
- MySQL instance
- Google Maps API key (for routes/maps)

### Backend

1. Go to backend:

```bash
cd backend
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure DB/API values:

- Current code uses a hardcoded DB connection in `backend/app/database.py`.
- Update `DATABASE_URL` there before running (or refactor to env usage).
- Ensure your Google Maps key is available where routers expect it.

4. Start server:

```bash
python start_server.py
```

Backend URLs:
- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`

### Frontend

1. Go to frontend app:

```bash
cd frontend/default
```

2. Install packages:

```bash
npm install
```

3. Start app:

```bash
npm start
```

Frontend URL:
- `http://localhost:3000`

## Key API Routes

### Triage + Chat

- `POST /triage/`
- `GET /triage/all-recent`
- `GET /triage/ambulances/status`
- `GET /triage/case/{case_id}/ambulance`
- `POST /llm-chat/`

### Maps

- `GET /maps/nearest-ambulance`
- `POST /maps/update-ambulance-location/{ambulance_id}`
- `GET /maps/ambulances-with-coordinates`
- `POST /maps/add-demo-ambulances`
- `GET /maps/debug/*`

### VAPI

- `POST /vapi/status`
- `POST /vapi/function-call`
- `POST /vapi/tool-calls`
- `POST /vapi/server`
- `POST /vapi/end-call`
- `GET /vapi/calls`
- `GET /vapi/config`
- `GET /vapi/debug/recent-calls`
- `POST /vapi/model`
- `POST /vapi/initiate-call`

### Admin

- `GET /admin/patients`
- `GET /admin/ambulances`
- `GET /admin/staffs`
- `POST /admin/ambulances`
- `GET /admin/system-prompt`
- `PUT /admin/system-prompt`

## Project Structure

```text
AIMedicalSystem/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── crud.py
│   │   ├── prompts.py
│   │   └── routers/
│   │       ├── triage.py
│   │       ├── medicalchat.py
│   │       ├── maps.py
│   │       ├── vapi.py
│   │       └── admin.py
│   ├── requirements.txt
│   └── start_server.py
├── frontend/
│   └── default/
│       ├── src/
│       │   ├── pages/MedicalChat/
│       │   ├── helpers/api_helper.js
│       │   └── Routes/index.js
│       └── package.json
└── README.md
```
