# 🚑 AI Medical Ambulance Dispatch & Emergency Response System

<div align="center">

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-18.3.1-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org/)
[![Redux](https://img.shields.io/badge/Redux-Toolkit-764ABC?style=for-the-badge&logo=redux&logoColor=white)](https://redux.js.org/)
[![Google Maps](https://img.shields.io/badge/Google%20Maps-API%20Platform-4285F4?style=for-the-badge&logo=googlemaps&logoColor=white)](https://developers.google.com/maps)
[![Vapi AI](https://img.shields.io/badge/Voice%20AI-Vapi.ai-5B5BD6?style=for-the-badge&logo=openai&logoColor=white)](https://vapi.ai/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

<p align="center">
  <strong>An autonomous, real-time emergency triage and multi-criteria ambulance dispatch system powered by Large Language Models, Voice AI, and Google Maps Navigation Engine.</strong>
</p>

[Key Features](#-key-features) •
[System Architecture](#-system-architecture) •
[Dispatch Algorithm](#-smart-ambulance-selection-algorithm) •
[Voice AI Integration](#-vapi-voice-ai-telephony-pipeline) •
[API Reference](#-comprehensive-api-reference) •
[Database Schema](#-database-schema--erd) •
[Installation](#-getting-started)

<br/>

![Command Center Interface](FrontendUI.png)

</div>

---

## 📌 Executive Overview

In time-critical medical emergencies, every second saved translates directly to lives preserved. Traditional emergency dispatching suffers from operational bottlenecks: manual symptom intake, subjective triage assessment, and sub-optimal ambulance allocation based merely on straight-line proximity rather than real-time traffic, vehicle equipment capability, and operational readiness.

The **AI Medical Ambulance Dispatch System** is an end-to-end mission-critical platform that automates and optimizes the entire emergency response lifecycle:

1. **Omnichannel Patient Intake**: Captures emergency reports via interactive web chat (with Text-to-Speech synthesis) or direct telephony voice calls powered by **Vapi Voice AI**.
2. **Clinical Severity Triage (LLM)**: Analyzes unstructured symptom descriptions to classify cases into clinical triage categories (`Red` / `Orange` / `Yellow`) and determines the required ambulance tier (`ICU` / `Advanced` / `Basic`).
3. **Multi-Criteria Optimal Dispatching**: Queries the active fleet database, filters vehicles by fuel threshold ($\ge 50\%$) and operational availability, computes live driving routes via **Google Maps Directions API**, and selects the optimal unit minimizing ETA and distance.
4. **Real-Time Operational Command Center**: Delivers a full-featured dashboard for dispatchers with live Google Maps polyline routing, fleet telemetry, patient intake tracking, and administrative controls.

---

## ✨ Key Features

### 🧠 1. Intelligent AI Triage & Severity Classification
- **Zero-Shot Clinical Extraction**: Converts raw patient descriptions into structured triage metadata (`triage_level`, `patient_triage`, `ambulance_type`, `identified_symptoms`).
- **Standardized Medical Protocol**:
  - 🔴 **Red Priority (Emergency)**: Critical/life-threatening (cardiac arrest, respiratory failure, severe trauma) $\rightarrow$ Dispatches **ICU** or **Advanced Life Support (ALS)** units.
  - 🟠 **Orange Priority (Urgent)**: Severe but non-immediate threat $\rightarrow$ Dispatches **Advanced** or **Basic** units.
  - 🟡 **Yellow Priority (Clinical/Transport)**: Stable conditions $\rightarrow$ Dispatches **Basic Life Support (BLS)** units.
- **Dynamic System Prompts**: Dispatch administrators can fine-tune LLM clinical intake behavior at runtime via the Admin UI without restarting backend services.

### 🚑 2. Multi-Criteria Smart Ambulance Selection Algorithm
- **Fuel-Level Constraint Filter**: Excludes ambulances below $50\%$ fuel to prevent en-route failure during high-priority transfers.
- **Traffic-Aware Navigation**: Evaluates real-time driving duration (seconds) and route distance (meters) via Google Maps Directions API for every candidate unit.
- **Multi-Tiered Ranking Function**:
  $$\text{Score} = f(\text{ETA}_{\text{driving}}, \text{Distance}_{\text{route}}, -\text{Fuel Level})$$
- **Automatic Fallback Engine**: Falls back to the Haversine great-circle distance algorithm if external mapping APIs experience network disruption.

### 🎙️ 3. Autonomous Voice AI Telephony (Vapi.ai)
- **Live Voice Emergency Intake**: Receives inbound phone calls, speaks empathetic emergency instructions, and extracts patient parameters (Name, Age, Gender, Phone, Location, Symptoms).
- **In-Call Function Execution**: Triggers real-time tool calling (`create_emergency_case`) mid-conversation, dispatching medical personnel before the caller hangs up.
- **Automated Geocoding**: Automatically translates caller-provided street addresses or landmarks into precise geographic coordinates $(\text{Lat}, \text{Lng})$.
- **Transcript Extraction Fallback**: Asynchronously extracts emergency parameters from call transcripts if voice tool calling encounters network drops.

### 🗺️ 4. Interactive Live Routing & Command Dashboard
- **Turn-by-Turn Polyline Rendering**: Renders Google Maps vector routes between the assigned ambulance and patient GPS coordinates.
- **Fleet Telemetry Tracking**: Live status monitor for ambulance availability (`available`, `dispatch`, `out_of_services`, `maintenance`), crew headcount, and fuel capacity.
- **Interactive Audio Chat**: Supports conversational intake with Google Text-to-Speech (`gTTS`) streaming audio output.
- **Automated Case Lifecycle Management**: Background daemon periodically auto-resolves aged cases and transitions patient admission states.

---

## 🏗️ System Architecture

```mermaid
flowchart TB
    subgraph INTAKE[" Emergency Intake Layer "]
        P1["📞 Emergency Caller (Phone / PSTN)"] -->|"Inbound Call"| VAPI["Vapi Voice AI Platform"]
        P2["💻 Web Portal User"] -->|"Web Chat / GPS Intake"| FE["React Command Center (Velzon / Redux)"]
    end

    subgraph BACKEND[" FastAPI Core Application Layer "]
        API["FastAPI Dispatch Gateway"]
        
        subgraph ROUTERS[" Router Modules "]
            R_TRIAGE["/triage\n(Clinical Case Management)"]
            R_CHAT["/llm-chat\n(Conversational Symptom Intake)"]
            R_MAPS["/maps\n(Routing & Fleet Allocation)"]
            R_VAPI["/vapi\n(Voice Webhooks & Tool Calling)"]
            R_ADMIN["/admin\n(Fleet CRUD & Prompt Engineering)"]
        end

        subgraph SERVICES[" Intelligence & Computational Engines "]
            LLM_ENG["LLM Engine\n(LM Studio / Gemma 4-12B / OpenAI)"]
            GEO_ENG["Google Maps Directions & Geocoding"]
            SORT_ALG["Multi-Criteria Selection Algorithm"]
            TTS_ENG["gTTS Audio Streaming Engine"]
            BG_TASK["Async Lifecycle Daemon\n(Case Auto-Completion)"]
        end
    end

    subgraph PERSISTENCE[" Persistence Layer (MySQL) "]
        DB[(MySQL Database)]
        T_PATIENTS["patients"]
        T_CASES["cases"]
        T_AMBULANCES["ambulances"]
        T_STAFF["staffs"]
        T_PROMPTS["system_prompts"]
    end

    %% Intake connections
    VAPI -->|"POST /vapi/function-call"| R_VAPI
    VAPI -->|"POST /vapi/status"| R_VAPI
    FE -->|"REST / WebSocket"| API

    %% Router routing
    API --> R_TRIAGE
    API --> R_CHAT
    API --> R_MAPS
    API --> R_VAPI
    API --> R_ADMIN

    %% Internal module interactions
    R_CHAT --> LLM_ENG
    R_CHAT --> TTS_ENG
    R_TRIAGE --> LLM_ENG
    R_TRIAGE --> R_MAPS
    R_MAPS --> GEO_ENG
    R_MAPS --> SORT_ALG
    R_VAPI --> GEO_ENG
    R_VAPI --> R_TRIAGE

    %% Database connections
    R_TRIAGE --> DB
    R_MAPS --> DB
    R_ADMIN --> DB
    BG_TASK --> DB
    DB --- T_PATIENTS
    DB --- T_CASES
    DB --- T_AMBULANCES
    DB --- T_STAFF
    DB --- T_PROMPTS
```

---

## 🧮 Smart Ambulance Selection Algorithm

The ambulance dispatch algorithm replaces legacy static radius lookups with a high-assurance, multi-stage operational decision matrix:

```
                  [ Inbound Case with Patient Coordinates (Lat, Lng) & Severity Type ]
                                                    │
                                                    ▼
                     ┌─────────────────────────────────────────────────────────────┐
                     │ 1. Filter Database for Eligible Ambulances:                 │
                     │    • status == 'available'                                  │
                     │    • fuel_level > 50%                                       │
                     │    • latitude IS NOT NULL AND longitude IS NOT NULL        │
                     │    • type_of_ambulance == requested_type (with fallback)    │
                     └─────────────────────────────────────────────────────────────┘
                                                    │
                                                    ▼
                     ┌─────────────────────────────────────────────────────────────┐
                     │ 2. Concurrent Google Maps Routing Query:                    │
                     │    • Query Directions API for (Ambulance_Coords → Patient)  │
                     │    • Extract duration_seconds, distance_meters, polyline    │
                     │    • Fallback: Haversine straight-line distance if API down │
                     └─────────────────────────────────────────────────────────────┘
                                                    │
                                                    ▼
                     ┌─────────────────────────────────────────────────────────────┐
                     │ 3. Lexicographical Multi-Criteria Tuple Sort:               │
                     │    sort_key = (duration_seconds, distance_meters, -fuel)    │
                     └─────────────────────────────────────────────────────────────┘
                                                    │
                                                    ▼
                     ┌─────────────────────────────────────────────────────────────┐
                     │ 4. Dispatch Execution:                                      │
                     │    • Ambulance status → 'dispatch'                          │
                     │    • Case status → 'Assigned'                               │
                     │    • Patient status → 'Travelling'                          │
                     │    • Return Turn-by-Turn Route + Polyline + Reason Log      │
                     └─────────────────────────────────────────────────────────────┘
```

### Algorithm Implementation Excerpt (`backend/app/routers/maps.py`):
```python
def select_best_ambulance(ambulance_route_data: list, patient_lat: float, patient_lon: float) -> dict:
    """
    Multi-criteria ranking optimization:
    1. Primary: Minimum driving travel time (duration_seconds via Google Maps API)
    2. Secondary: Minimum route driving distance (distance_meters)
    3. Tertiary: Maximum fuel level reserve (-fuel_level)
    """
    def sort_key(data):
        route = data["route"]
        duration_seconds = route.get("duration_seconds", float('inf'))
        distance_meters = route.get("distance_meters", float('inf'))
        fuel_level = data["fuel_level"]
        return (duration_seconds, distance_meters, -fuel_level)

    sorted_ambulances = sorted(ambulance_route_data, key=sort_key)
    best_ambulance_data = sorted_ambulances[0]
    
    best_ambulance_data["selection_reason"] = (
        f"Selected based on shortest time ({best_ambulance_data['route'].get('duration', 'N/A')}) "
        f"and distance ({best_ambulance_data['route'].get('distance', 'N/A')}) "
        f"with {best_ambulance_data['fuel_level']}% fuel"
    )
    return best_ambulance_data
```

---

## 📞 Vapi Voice AI Telephony Pipeline

The platform connects directly to public telephone networks via **Vapi.ai** integration, enabling non-technical users to dial an emergency hotline and speak naturally to an AI dispatcher.

```
[ Patient Dials Hotline ] ──► [ Vapi Voice Bot ] ──► [ Speech-To-Text / LLM ]
                                                            │
                                             (Tool Call: create_emergency_case)
                                                            │
                                                            ▼
                                                [ POST /vapi/function-call ]
                                                            │
                                       ┌────────────────────┴────────────────────┐
                                       ▼                                         ▼
                             [ Google Geocoding ]                      [ Triage & Dispatch ]
                             Address ➔ (Lat, Lng)                      Assigns Optimal Unit
                                       └────────────────────┬────────────────────┘
                                                            │
                                                            ▼
                                              [ Immediate Voice Confirmation ]
                                              "Help is on the way to your location."
```

### Tool Calling Schema (`create_emergency_case`):
```json
{
  "type": "object",
  "properties": {
    "name": { "type": "string", "description": "Patient full name" },
    "age": { "type": "integer", "description": "Patient age in years" },
    "gender": { "type": "string", "enum": ["Male", "Female", "Other"] },
    "phone": { "type": "string", "description": "Callback phone number" },
    "symptoms": { "type": "string", "description": "Medical emergency symptoms" },
    "location": { "type": "string", "description": "Physical address or landmark to geocode" }
  },
  "required": ["name", "age", "gender", "symptoms"]
}
```

---

## 📡 Comprehensive API Reference

### 1. Triage & Emergency Cases (`/triage`)
| Method | Endpoint | Description | Request Body / Params |
|:---|:---|:---|:---|
| `POST` | `/triage/` | Analyzes symptoms via LLM, saves patient & case, and dispatches optimal ambulance | `CaseInput` (JSON: name, age, gender, contact, symptoms, location, lat, lon) |
| `GET` | `/triage/all-recent` | Fetches all recent emergency cases with triage status | *None* |
| `GET` | `/triage/ambulances/status` | Fetches all ambulances currently in `dispatch` status | *None* |
| `GET` | `/triage/case/{case_id}/ambulance` | Retrieves assigned vehicle, route info, and ETA for a specific case | `case_id` (Path param: int) |

### 2. Conversational Medical Chat (`/llm-chat`)
| Method | Endpoint | Description | Request Body / Params |
|:---|:---|:---|:---|
| `POST` | `/llm-chat/` | Multi-turn medical chat endpoint with dynamic TTS audio streaming | `ChatRequest` (JSON: message, session_id, latitude, longitude) |

### 3. Maps & Routing Engine (`/maps`)
| Method | Endpoint | Description | Request Body / Params |
|:---|:---|:---|:---|
| `GET` | `/maps/nearest-ambulance` | Runs multi-criteria ambulance ranking for given coordinates | `patient_lat`, `patient_lon`, `ambulance_type` |
| `POST` | `/maps/update-ambulance-location/{id}` | Updates GPS position and location string for an ambulance | `ambulance_id`, `latitude`, `longitude`, `current_location` |
| `GET` | `/maps/ambulances-with-coordinates` | Lists all fleet vehicles with active GPS telemetry | *None* |
| `POST` | `/maps/add-demo-ambulances` | Seeds demo ambulances across Chennai geographical sectors | *None* |
| `GET` | `/maps/debug/api-status` | Inspects Google Maps API configuration and connectivity | *None* |
| `GET` | `/maps/debug/test-route` | Validates route calculation between test coordinates | *None* |
| `GET` | `/maps/debug/system-info` | System diagnostic report on Python, Google Maps, and DB | *None* |

### 4. Vapi Voice AI Webhooks (`/vapi`)
| Method | Endpoint | Description | Request Body / Params |
|:---|:---|:---|:---|
| `POST` | `/vapi/function-call` | Webhook for Vapi tool-calling execution (`create_emergency_case`) | Vapi Function Call payload |
| `POST` | `/vapi/tool-calls` | Alias endpoint for modern Vapi tool-calls format | Vapi Tool Call payload |
| `POST` | `/vapi/status` | Inbound status webhook (call ringing, in-progress, ended) | Vapi Status payload |
| `POST` | `/vapi/server` | Real-time transcript chunk receiver | Vapi Server message payload |
| `POST` | `/vapi/end-call` | Post-call session cleanup and transcript fallback parser | Vapi End Call payload |
| `GET` | `/vapi/calls` | Lists active call sessions held in memory | *None* |
| `GET` | `/vapi/config` | Inspects Vapi webhook configurations and LLM routing settings | *None* |
| `POST` | `/vapi/initiate-call` | Triggers outbound automated emergency call | Query params: `phone_number`, `assistant_id` |

### 5. Administration & System Management (`/admin`)
| Method | Endpoint | Description | Request Body / Params |
|:---|:---|:---|:---|
| `GET` | `/admin/patients` | Retrieves all registered patient records | *None* |
| `GET` | `/admin/ambulances` | Retrieves all fleet vehicle entries | *None* |
| `POST` | `/admin/ambulances` | Registers a new vehicle into the fleet database | `AmbulanceCreate` (JSON) |
| `GET` | `/admin/staffs` | Retrieves all medical paramedic and driver staff records | *None* |
| `GET` | `/admin/system-prompt` | Retrieves the active LLM system prompt used for triage intake | *None* |
| `PUT` | `/admin/system-prompt` | Hot-reloads and updates the clinical system prompt | `SystemPromptUpdate` (JSON: prompt) |

---

## 🗄️ Database Schema & ERD

The database architecture is implemented in MySQL using **SQLAlchemy ORM** (`backend/app/models.py`):

```mermaid
erDiagram
    PATIENTS ||--o{ CASES : "has"
    AMBULANCES ||--o{ STAFFS : "assigned_to"

    PATIENTS {
        int id PK
        string name "VARCHAR(100)"
        int age
        enum gender "'M', 'F'"
        string contact "VARCHAR(20)"
        enum patient_triage "'Red', 'Orange', 'Yellow'"
        enum ambulance_type "'Basic', 'Advanced', 'ICU'"
        enum patient_status "'Pending', 'Admitted', 'Travelling'"
    }

    CASES {
        int id PK
        int patient_id FK
        enum triage_level "'Emergency', 'Transport', 'Clinical'"
        text symptoms
        string location "VARCHAR(255)"
        decimal latitude "DECIMAL(9,6)"
        decimal longitude "DECIMAL(9,6)"
        enum status "'Pending', 'Assigned', 'Completed'"
        timestamp created_at
    }

    AMBULANCES {
        int ambulance_id PK
        enum type_of_ambulance "'Basic', 'Advanced', 'ICU'"
        string vehicle_number UK "VARCHAR(255)"
        int no_of_staffs
        string current_location "VARCHAR(255)"
        decimal latitude "DECIMAL(9,6)"
        decimal longitude "DECIMAL(9,6)"
        enum status "'available', 'dispatch', 'out_of_services', 'maintenance'"
        int fuel_level "0 - 100"
        timestamp last_updated
    }

    STAFFS {
        int staff_id PK
        int ambulance_id FK
        string role "VARCHAR(255)"
        enum staff_status "'available', 'on_call', 'busy', 'on_leave'"
    }

    SYSTEM_PROMPTS {
        int id PK
        text prompt
        timestamp updated_at
    }
```

---

## 💻 Tech Stack Matrix

| Domain | Technology / Library | Version | Purpose |
|:---|:---|:---|:---|
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) | `0.104.1` | High-performance asynchronous REST API server |
| **ASGI Server** | [Uvicorn](https://www.uvicorn.org/) | `0.24.0` | Production ASGI web server implementation |
| **ORM & Database** | [SQLAlchemy](https://www.sqlalchemy.org/) + [PyMySQL](https://pymysql.readthedocs.io/) | `2.0.23` / `1.1.0` | Object Relational Mapping & MySQL database driver |
| **Data Validation** | [Pydantic](https://docs.pydantic.dev/) | `2.5.0` | Strict data schema parsing and request validation |
| **Mapping & Routing** | [Google Maps Services Python](https://github.com/googlemaps/google-maps-services-python) | `4.10.0` | Turn-by-turn routing, ETA calculation, and geocoding |
| **AI / LLM Runtime** | [LM Studio](https://lmstudio.ai/) / [Gemma 4-12B](https://huggingface.co/google/gemma-2-9b) | OpenAI API Compat | Local privacy-preserving LLM inference server |
| **Voice AI & Telephony** | [Vapi.ai](https://vapi.ai/) | Cloud API | Inbound/outbound speech-to-speech emergency call automation |
| **Audio Synthesis** | [gTTS (Google Text-to-Speech)](https://pypi.org/project/gTTS/) | `2.4.0` | Streaming audio generation for web medical chat |
| **Frontend Framework** | [React](https://reactjs.org/) + [Create React App](https://create-react-app.dev/) | `18.3.1` / `5.0.1` | Single Page Application command center |
| **State Management** | [Redux Toolkit](https://redux-toolkit.js.org/) | `2.3.0` | Global state container for cases, fleet telemetry, and UI |
| **Frontend Maps** | [@react-google-maps/api](https://www.npmjs.com/package/@react-google-maps/api) | `2.20.3` | Interactive route visualization and live ambulance tracking |
| **UI Component Suite** | [Bootstrap 5](https://getbootstrap.com/) + [Reactstrap](https://reactstrap.github.io/) | `5.3.3` / `9.2.3` | Responsive dark/light theme dashboard system |
| **Charts & Analytics** | [ApexCharts](https://apexcharts.com/) + [ECharts](https://echarts.apache.org/) | `3.54.1` / `5.5.1` | Real-time response time and case distribution metrics |

---

## 📁 Repository Directory Structure

```text
AI_Ambulance_Dispatch_System/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI initialization, CORS, middleware & lifecycle loops
│   │   ├── database.py            # SQLAlchemy engine, SessionLocal, and DB configuration
│   │   ├── models.py              # Declarative SQLAlchemy database models (Patients, Cases, Fleet)
│   │   ├── schemas.py             # Pydantic validation schemas and response DTOs
│   │   ├── crud.py                # Database queries and persistence abstractions
│   │   ├── llm_config.py          # LM Studio / Local LLM client configuration & options
│   │   ├── prompts.py             # Medical triage and symptom extraction prompt templates
│   │   └── routers/
│   │       ├── triage.py          # Clinical triage analysis and case dispatch handler
│   │       ├── maps.py            # Multi-criteria ambulance selection & Google Maps routing
│   │       ├── medicalchat.py     # Interactive patient web chat with gTTS audio streaming
│   │       ├── vapi.py            # Vapi voice webhooks, tool calls, and address geocoding
│   │       └── admin.py           # Fleet CRUD, paramedic staff, and live prompt management
│   ├── add_demo_ambulances.py     # Standalone seed script for fleet demo data
│   ├── start_server.py            # Automated Uvicorn launcher
│   ├── requirements.txt           # Python dependency specifications
│   └── .env                       # Backend secrets and environment configuration
├── frontend/
│   └── default/
│       ├── public/                # Static assets, favicon, and HTML entry point
│       ├── src/
│       │   ├── pages/
│       │   │   ├── DashboardMedical/  # Command center widgets, KPI counters, case tables
│       │   │   ├── MedicalChat/       # Live medical symptom chat & GPS route map component
│       │   │   ├── Cases/             # Active and historical case directory
│       │   │   └── Admin/             # Ambulances, Patients, Staff, and Prompt configuration
│       │   ├── Routes/            # Protected and public route declarations
│       │   ├── slices/            # Redux Toolkit reducers and async thunks
│       │   ├── helpers/           # Axios HTTP wrappers and API clients
│       │   ├── Layouts/           # Header, Sidebar, Footer layout scaffolding
│       │   └── App.js             # Root React component
│       └── package.json           # Frontend dependencies and npm scripts
├── Documentation/                 # Architectural deep-dives and integration guides
│   ├── AMBULANCE_SELECTION_IMPLEMENTATION.md
│   ├── VAPI_INTEGRATION.md
│   ├── VAPI_LOGS_GUIDE.md
│   ├── VAPI_TROUBLESHOOTING.md
│   └── ROUTE_MAP_FIX.md
├── DropTables.sql                 # Database reset script
├── FetchAmbulances.sql            # Fleet inspection query
├── FetchCases.sql                 # Case inspection query
├── FrontendUI.png                 # Main command center screenshot
└── README.md                      # Project documentation
```

---

## 🚀 Getting Started

### 📋 Prerequisites
Ensure you have the following installed on your host machine:
- **Python 3.10+**
- **Node.js 18+** & **npm**
- **MySQL 8.0+** instance
- **Google Maps Platform API Key** (Directions API, Geocoding API, Maps JavaScript API enabled)
- *(Optional)* **LM Studio** with a loaded LLM (e.g., `google/gemma-4-12b-qat`) running on `http://localhost:1234`
- *(Optional)* **Vapi Account** & **Ngrok** for testing telephone voice integrations

---

### ⚙️ 1. Environment Configuration

#### Backend `.env` (`backend/.env`):
```env
# Database Connection
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/ai_ambulance_db

# Google Maps API Key (Routing & Geocoding)
GOOGLE_MAPS_API_KEY=AIzaSyYourGoogleMapsApiKeyHere

# Local LLM Configuration (LM Studio / OpenAI Compatible)
LOCAL_LLM_URL=http://localhost:1234/v1/chat/completions
LOCAL_LLM_MODEL=google/gemma-4-12b-qat
LOCAL_LLM_REASONING=off

# Vapi Voice AI Platform Configuration
VAPI_API_KEY=your_vapi_private_api_key
VAPI_PHONE_NUMBER_ID=your_vapi_phone_number_id
```

#### Frontend `.env` (`frontend/default/.env`):
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_GOOGLE_MAPS_API_KEY=AIzaSyYourGoogleMapsApiKeyHere
```

---

### 🐍 2. Backend Setup & Launch

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database and seed demo fleet data:
   ```bash
   python add_demo_ambulances.py
   ```

5. Start the FastAPI development server:
   ```bash
   python start_server.py
   # Or directly via Uvicorn:
   # uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

- **API Base URL**: `http://localhost:8000`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **Alternative ReDoc UI**: `http://localhost:8000/redoc`

---

### ⚛️ 3. Frontend Setup & Launch

1. Navigate to the frontend application directory:
   ```bash
   cd frontend/default
   ```

2. Install Node dependencies:
   ```bash
   npm install --legacy-peer-deps
   ```

3. Launch the React development server:
   ```bash
   npm start
   ```

- **Command Center Web UI**: `http://localhost:3000`

---

### 🎙️ 4. Setting Up Vapi Voice AI Webhooks (Optional)

To test incoming telephony calls:

1. Expose your local backend using **Ngrok**:
   ```bash
   ngrok http 8000
   ```

2. In the **Vapi Dashboard** (`https://dashboard.vapi.ai/`):
   - Navigate to **Assistants** $\rightarrow$ Create or select your assistant.
   - Set Model to **OpenAI (GPT-4o or GPT-3.5-Turbo)** with Temperature `0.7`.
   - Under **Tools**, create a new Function named `create_emergency_case` with Server URL:
     ```
     https://your-ngrok-subdomain.ngrok-free.dev/vapi/function-call
     ```
   - Paste the JSON parameter schema provided in [Voice AI Telephony Pipeline](#-vapi-voice-ai-telephony-pipeline).
   - Under **System Prompt**, enter the clinical voice intake prompt from `Documentation/VAPI_INTEGRATION.md`.

3. Dial your assigned Vapi phone number to initiate an emergency call!

---

## 🧪 Verification & Testing Workflows

### 1. Test Smart Ambulance Selection Endpoint
```bash
curl -X GET "http://localhost:8000/maps/nearest-ambulance?patient_lat=13.0827&patient_lon=80.2707&ambulance_type=Advanced"
```

### 2. Submit an Emergency Case via Triage API
```bash
curl -X POST "http://localhost:8000/triage/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rajesh Kumar",
    "age": 52,
    "gender": "Male",
    "contact": "+919876543210",
    "symptoms": "Severe acute chest pain radiating to left arm, heavy sweating, difficulty breathing",
    "location": "Chennai Central Railway Station",
    "latitude": 13.0827,
    "longitude": 80.2707
  }'
```

### 3. Simulate Vapi Function Calling Webhook
```bash
curl -X POST "http://localhost:8000/vapi/function-call" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "toolCalls": [
        {
          "id": "call_test_001",
          "function": {
            "name": "create_emergency_case",
            "arguments": {
              "name": "Priya Sharma",
              "age": 28,
              "gender": "Female",
              "phone": "+919876500112",
              "symptoms": "High grade fever and sudden onset seizures",
              "location": "Anna Nagar Tower Park, Chennai"
            }
          }
        }
      ]
    },
    "call": {
      "id": "vapi_session_test_999",
      "from": "+919876500112"
    }
  }'
```

---

## 🔒 Security & Production Guidelines

- **Environment Isolation**: Never commit active API credentials (`GOOGLE_MAPS_API_KEY`, `VAPI_API_KEY`) or DB passwords to public repositories.
- **CORS Restrictons**: In production deployments, restrict CORS `allow_origins` in `backend/app/main.py` to verified domain names instead of wildcard `*`.
- **Database Connection Pooling**: Ensure `pool_size` and `max_overflow` are properly configured in `database.py` for high-concurrency environments.
- **Fail-Safe Routing**: The system includes built-in fallbacks (e.g. Haversine distance and fallback fleet objects) to ensure zero total service outages during external API downtime.

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <sub>Built with ❤️ for rapid emergency dispatch automation and healthcare operations optimization.</sub>
</div>
