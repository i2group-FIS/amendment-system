# Amendment System

An internal amendment tracking system for managing application updates.

## Features

- Track past, current, and future amendments
- Unique ID for each amendment
- RESTful API backend (FastAPI + SQLite)
- Modern React frontend
- Full CRUD operations
- Timeline view of amendments

## Tech Stack

- **Backend**: Python FastAPI
- **Frontend**: React
- **Database**: SQLite
- **API Documentation**: Auto-generated with FastAPI/Swagger

## Project Structure

```
amendment-system/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── models.py      # Database models
│   │   ├── schemas.py     # Pydantic schemas
│   │   ├── crud.py        # CRUD operations
│   │   ├── database.py    # Database connection
│   │   └── main.py        # FastAPI app
│   └── requirements.txt
├── frontend/          # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.js
│   └── package.json
├── tests/            # Test suite
└── docs/             # Documentation
```

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm

### Quick Start

1. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Backend runs on http://localhost:8000

2. **Frontend Setup** (in a new terminal)
```bash
cd frontend
npm install
npm start
```
Frontend runs on http://localhost:3000

3. **Seed Database** (optional but recommended)
```bash
source backend/venv/bin/activate
python scripts/seed_db.py
```
Creates 50 sample amendments for testing

### Accessing the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative API Docs**: http://localhost:8000/redoc (ReDoc)

## Current Status

**Working Features:**
- ✅ Backend API with all CRUD operations (148 tests passing)
- ✅ Dashboard with statistics
- ✅ Amendment list with filtering and pagination
- ✅ Database seeding script
- 🚧 Amendment detail page (placeholder)
- 🚧 Amendment create form (placeholder)

**Next Steps:**
- Complete Amendment Detail page with edit functionality
- Complete Amendment Create form
- Add progress update modal
- Implement authentication

## API Endpoints

### Amendments
- `GET /api/amendments` - List amendments (with filtering/pagination)
- `GET /api/amendments/stats` - Get statistics
- `GET /api/amendments/{id}` - Get specific amendment
- `GET /api/amendments/reference/{ref}` - Get by reference number
- `POST /api/amendments` - Create new amendment
- `PUT /api/amendments/{id}` - Update amendment
- `DELETE /api/amendments/{id}` - Delete amendment

### Progress Tracking
- `POST /api/amendments/{id}/progress` - Add progress update
- `GET /api/amendments/{id}/progress` - Get progress history

### Amendment Linking
- `POST /api/amendments/{id}/links` - Link amendments
- `DELETE /api/amendments/{id}/links/{linked_id}` - Unlink amendments

### Reference Data
- `GET /api/reference/statuses` - Get all amendment statuses
- `GET /api/reference/priorities` - Get all priorities
- `GET /api/reference/types` - Get all amendment types
- `GET /api/reference/forces` - Get all forces
- `GET /api/reference/development-statuses` - Get development statuses
- `GET /api/reference/link-types` - Get link types

## Testing

Run the test suite:
```bash
source backend/venv/bin/activate
pytest
```

All 148 tests should pass.

## Development

See `SHARED_TASK_NOTES.md` for current development status and next steps.
See `TODO.md` for detailed task tracking.
