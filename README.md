
# Task API

A FastAPI learning project for task CRUD operations, currently being migrated from an in-memory list to SQLite.

## Current implementation

- `GET /tasks` and `GET /tasks/{id}` read from `tasks.db`.
- `POST`, `PUT`, and `DELETE` still modify the separate in-memory list in `main.py`. Their changes do not appear in database reads and reset when the app restarts.
- Database initialization is manual: run `python database.py` before starting the API for the first time.

## Tech stack

- Python 3.12
- FastAPI and Pydantic for routes and request validation
- Uvicorn for serving the app
- SQLite through Python's built-in `sqlite3` module; SQLModel and a separate database server are not required

## Getting started (Windows PowerShell)

Open a terminal in the project folder.

### 1. Create and activate a virtual environment

Skip creation if you already have `venv`.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install fastapi uvicorn
```

### 3. Initialize the database

```powershell
python database.py
```

This creates `tasks.db` beside `database.py`, creates the `tasks` table if needed, and inserts five example tasks only if the table is empty. Repeating the command preserves existing rows without adding duplicate examples. The app does not currently call `init_db()` automatically at startup.

The lesson's Step 0 asks for three example tasks; the current code seeds five.

### 4. Start the API

```powershell
python -m uvicorn main:app --reload
```

The API runs at [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Database structure

| Column | Declaration | Purpose |
|---|---|---|
| `id` | `INTEGER PRIMARY KEY AUTOINCREMENT` | Automatically assigned task ID |
| `title` | `TEXT NOT NULL` | Task description |
| `done` | `BOOLEAN NOT NULL` | Completion state, stored as `0` or `1` |

Database GET responses currently expose `done` as `0` or `1`. In-memory write responses use JSON booleans (`false` or `true`).

## API endpoints

| Method | Endpoint | Storage / purpose | Status codes |
|---|---|---|---|
| `GET` | `/` | API information | `200` |
| `GET` | `/health` | App health response | `200` |
| `GET` | `/tasks` | List database tasks | `200`, `404` if empty |
| `GET` | `/tasks/{id}` | Read one database task | `200`, `404`, `422` |
| `POST` | `/tasks` | Create an in-memory task | `201`, `400`, `422` |
| `PUT` | `/tasks/{id}` | Update an in-memory task | `200`, `400`, `404`, `422` |
| `DELETE` | `/tasks/{id}` | Delete an in-memory task | `204`, `404`, `422` |

An empty title (`""`) returns `400`. Missing required fields, null titles, and non-integer path IDs return FastAPI validation errors (`422`). Whitespace-only titles are currently accepted. PUT requires both `title` and `done`.

A missing task returns `404`, not `400`, with a response such as:

```json
{"detail":"Task 999 not found"}
```

## Read checks

With the server running, use a second PowerShell terminal:

```powershell
curl.exe -i http://127.0.0.1:8000/tasks
curl.exe -i http://127.0.0.1:8000/tasks/1
curl.exe -i http://127.0.0.1:8000/tasks/999
```

On the current seeded database, the expected statuses are `200`, `200`, and `404`, respectively. These were verified against the app using FastAPI's test client.

Example response for `/tasks/1`:

```json
{"id": 6, "title": "Learn FastAPI", "done": false}
```
<img width="1240" height="605" alt="Screenshot 2026-08-01 210436" src="https://github.com/user-attachments/assets/a3138e4f-e58d-4250-a310-a4e2ea26d1a7" />

### Get all tasks

```bash
curl http://127.0.0.1:8000/tasks
```
<img width="1237" height="844" alt="Screenshot 2026-08-01 210102" src="https://github.com/user-attachments/assets/c0c70f48-76ba-4e76-9afc-805c54398b8f" />
<img width="1250" height="847" alt="Screenshot 2026-08-01 210129" src="https://github.com/user-attachments/assets/c77e377f-a20e-481d-962d-0fa1dec55856" />
<img width="1234" height="870" alt="Screenshot 2026-08-01 210219" src="https://github.com/user-attachments/assets/6121113e-c0df-4f3d-a841-6624845e5041" />
<img width="1241" height="869" alt="Screenshot 2026-08-01 210330" src="https://github.com/user-attachments/assets/8e005dcd-c914-4874-b444-d078cd99dfea" />

### Update a task

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/tasks/1' -Method Put -ContentType 'application/json' -Body '{"title":"Buy groceries","done":true}'
```
<img width="1225" height="826" alt="Screenshot 2026-08-01 210542" src="https://github.com/user-attachments/assets/6e989d2b-8bd9-4bc8-b1a4-9d1a46543082" />

### Delete a task

```bash
curl -X DELETE http://127.0.0.1:8000/tasks/1
# 204 No Content on success
# 404 Not Found if the task doesn't exist
```
<img width="1229" height="814" alt="Screenshot 2026-08-01 210814" src="https://github.com/user-attachments/assets/c69ab415-e301-4508-b064-b1f24fb17222" />

## Interactive Docs

FastAPI auto-generates interactive API documentation:

- **Swagger UI** — [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc** — [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Project structure

```text
flyrankAI/
|-- main.py        # FastAPI routes, models, and in-memory write operations
|-- database.py    # SQLite connections, initialization, and read queries
|-- tasks.db       # Database file generated by initialization
|-- README.md
|-- .gitignore
`-- venv/          # Local Python environment
```

## Remaining database migration work

- Move POST, PUT, and DELETE operations into SQLite so reads and writes share storage.
- Call database initialization during app startup.
- Align the five seed tasks with the lesson's three-task checkpoint.
- Align response formatting with the lesson: it specifies `{"error":"Task not found"}`, while the app currently uses FastAPI's `detail` field and includes the ID.
