# Database Documentation

## Overview

The Amendment System uses SQLAlchemy 2.0 as the ORM (Object-Relational Mapping) framework to interact with the database. The system is designed to work with SQLite for development and can be easily configured to work with PostgreSQL or MySQL for production.

## Database Configuration

### Configuration File

The database configuration is located in `backend/app/database.py`. This file contains:

- **Engine configuration** - Database connection and pooling settings
- **Session management** - Factory for creating database sessions
- **Base model class** - Base class for all database models
- **Utility functions** - Helper functions for database operations

### Environment Variables

Configure the database using environment variables (see `.env.example`):

```bash
# Database connection URL
DATABASE_URL=sqlite:///./amendment_system.db

# Enable SQL query logging (for debugging)
SQL_ECHO=False

# Environment (affects certain safety checks)
ENVIRONMENT=development  # Options: development, staging, production
```

### Supported Databases

#### SQLite (Development)
```bash
DATABASE_URL=sqlite:///./amendment_system.db
```

SQLite-specific features:
- Foreign key constraints are automatically enabled
- Static connection pooling is used
- Thread-safety checks are disabled for FastAPI compatibility

#### PostgreSQL (Production)
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

PostgreSQL-specific features:
- Connection pool with pre-ping to verify connections
- Pool size: 5 connections
- Max overflow: 10 additional connections

#### MySQL
```bash
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/dbname
```

## Database Schema

### Tables

1. **amendments** - Main amendment tracking table
   - Primary Key: `amendment_id`
   - Unique: `amendment_reference`
   - Contains all amendment details, QA information, and audit fields

2. **amendment_progress** - Progress updates for amendments
   - Primary Key: `amendment_progress_id`
   - Foreign Key: `amendment_id` → `amendments.amendment_id`
   - Cascade delete when parent amendment is deleted

3. **amendment_applications** - Applications affected by amendments
   - Primary Key: `id`
   - Foreign Key: `amendment_id` → `amendments.amendment_id`
   - Cascade delete when parent amendment is deleted

4. **amendment_links** - Links between related amendments
   - Primary Key: `amendment_link_id`
   - Foreign Keys:
     - `amendment_id` → `amendments.amendment_id`
     - `linked_amendment_id` → `amendments.amendment_id`
   - Cascade delete when parent amendment is deleted

### Relationships

- **Amendment → AmendmentProgress**: One-to-Many
- **Amendment → AmendmentApplication**: One-to-Many
- **Amendment → AmendmentLink**: One-to-Many

All relationships use cascade delete, meaning when an amendment is deleted, all related records are automatically deleted.

## Session Management

### Using Sessions in FastAPI

The recommended way to use database sessions in FastAPI endpoints:

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db

@app.get("/amendments")
def get_amendments(db: Session = Depends(get_db)):
    amendments = db.query(Amendment).all()
    return amendments
```

The `get_db()` function:
- Creates a new database session for each request
- Automatically commits on success
- Rolls back on errors
- Always closes the session when done

### Using Sessions in Scripts

For standalone scripts or background tasks:

```python
from backend.app.database import get_db_context

# Context manager handles commit/rollback/close automatically
with get_db_context() as db:
    amendment = Amendment(
        amendment_reference="TEST-001",
        amendment_type=AmendmentType.BUG,
        description="Test amendment"
    )
    db.add(amendment)
    # Commit happens automatically at the end of the with block
```

## Database Operations

### Initialize Database

Create all tables on application startup:

```python
from backend.app.database import init_db

init_db()
```

This is automatically called when the FastAPI application starts.

### Check Database Connection

Verify the database is accessible:

```python
from backend.app.database import check_db_connection

if check_db_connection():
    print("Database is connected")
else:
    print("Database connection failed")
```

### Reset Database (Development Only)

**WARNING**: This deletes all data!

```python
from backend.app.database import reset_db

reset_db()  # Drops all tables and recreates them
```

This function will raise an error if `ENVIRONMENT=production` to prevent accidental data loss.

## Error Handling

The database module includes comprehensive error handling:

### Connection Errors

If the database connection fails at startup, the application will:
1. Log the error with details
2. Raise a `RuntimeError` with a descriptive message
3. Prevent the application from starting

### Session Errors

If an error occurs during a database operation:
1. The error is logged
2. The session is automatically rolled back
3. The original exception is re-raised for handling

### Foreign Key Violations

Foreign key constraints are enforced:
- SQLite: Automatically enabled via PRAGMA
- PostgreSQL/MySQL: Enforced by default

Example error when trying to link to a non-existent amendment:
```
IntegrityError: FOREIGN KEY constraint failed
```

## Model Features

### Auto-Generated Fields

All models automatically include:

1. **Primary Keys**: Auto-incrementing integer IDs
2. **Audit Fields** (where applicable):
   - `created_by` - Username of creator
   - `created_on` - Timestamp of creation (auto-set)
   - `modified_by` - Username of last modifier
   - `modified_on` - Timestamp of last update (auto-updated)

### String Representation

All models include `__repr__` methods for better debugging:

```python
amendment = Amendment(...)
print(amendment)
# Output: <Amendment(id=1, ref='AMD-001', type=Bug, status=Open)>
```

## Best Practices

### 1. Always Use Dependency Injection

In FastAPI endpoints, always use `Depends(get_db)`:

```python
# ✅ Good
@app.get("/amendments")
def get_amendments(db: Session = Depends(get_db)):
    return db.query(Amendment).all()

# ❌ Bad - creates session without proper cleanup
@app.get("/amendments")
def get_amendments():
    db = SessionLocal()
    return db.query(Amendment).all()
```

### 2. Use Context Managers in Scripts

For standalone scripts, use `get_db_context()`:

```python
# ✅ Good
with get_db_context() as db:
    db.add(amendment)

# ❌ Bad - no automatic commit/rollback
db = SessionLocal()
db.add(amendment)
db.commit()
db.close()
```

### 3. Handle Exceptions Properly

```python
from sqlalchemy.exc import IntegrityError

try:
    with get_db_context() as db:
        amendment = Amendment(amendment_reference="DUP-001", ...)
        db.add(amendment)
except IntegrityError:
    print("Duplicate reference number")
```

### 4. Use Indexes

Key fields are already indexed for performance:
- `amendment_id` (primary key)
- `amendment_reference` (unique)

### 5. Cascade Deletes

Relationships use cascade delete, so you don't need to manually delete related records:

```python
# This automatically deletes all progress, applications, and links
db.delete(amendment)
db.commit()
```

## Testing

### Running Database Tests

```bash
pytest tests/test_database.py -v
```

### Test Database

Tests use the same database as development. Each test:
1. Initializes the database
2. Runs the test
3. Cleans up all test data

### Writing Database Tests

```python
from backend.app.database import get_db_context
from backend.app.models import Amendment

def test_create_amendment():
    with get_db_context() as db:
        amendment = Amendment(
            amendment_reference="TEST-001",
            amendment_type=AmendmentType.BUG,
            description="Test"
        )
        db.add(amendment)
        db.commit()

        result = db.query(Amendment).filter_by(
            amendment_reference="TEST-001"
        ).first()
        assert result is not None
```

## Troubleshooting

### "FOREIGN KEY constraint failed"

This means you're trying to:
- Delete a parent record that has children (shouldn't happen with cascade)
- Insert a child record with an invalid parent ID
- Link to a non-existent amendment

**Solution**: Ensure all foreign key references point to existing records.

### "database is locked" (SQLite)

SQLite has limited concurrent write support.

**Solution**:
- Use PostgreSQL for production
- Ensure sessions are properly closed
- Check for long-running transactions

### "connection already closed"

**Solution**: Don't reuse sessions across requests. Always use `Depends(get_db)` in FastAPI.

### Deprecated `declarative_base()` warning

We've already migrated to SQLAlchemy 2.0's `DeclarativeBase` class, so this warning should not appear.

## Migration to Production Database

### Step 1: Install Database Driver

For PostgreSQL:
```bash
pip install psycopg2-binary
```

For MySQL:
```bash
pip install pymysql
```

### Step 2: Update Environment Variable

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/amendment_system
```

### Step 3: Initialize Database

```bash
python -c "from backend.app.database import init_db; init_db()"
```

### Step 4: Verify Connection

```bash
python -c "from backend.app.database import check_db_connection; print(check_db_connection())"
```

## Future Enhancements

Planned improvements:

1. **Database Migrations** - Alembic integration for schema versioning
2. **Read Replicas** - Support for read-only database replicas
3. **Connection Pooling** - Advanced pooling for high-traffic scenarios
4. **Query Optimization** - Additional indexes based on query patterns
5. **Soft Deletes** - Option to mark records as deleted instead of removing them
