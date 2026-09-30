# Task API

A FastAPI learning project for task CRUD operations, currently being migrated from an in-memory list to SQLite.

## Current implementation

- `GET /tasks` and `GET /tasks/{id}` read from `tasks.db`.
- `POST /tasks` inserts into SQLite, commits the change, and returns the generated ID with `done: false`. Created tasks survive app restarts.
- `PUT` and `DELETE` still modify the separate in-memory list in `main.py`. Their changes do not appear in database reads and reset when the app restarts. A task created through POST is not added to that list, so PUT and DELETE cannot modify it yet.
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

Database GET responses currently expose `done` as `0` or `1`. POST and PUT responses use JSON booleans (`false` or `true`).

## API endpoints

| Method | Endpoint | Storage / purpose | Status codes |
|---|---|---|---|
| `GET` | `/` | API information | `200` |
| `GET` | `/health` | App health response | `200` |
| `GET` | `/tasks` | List database tasks | `200`, `404` if empty |
| `GET` | `/tasks/{id}` | Read one database task | `200`, `404`, `422` |
| `POST` | `/tasks` | Create a database task | `201`, `400`, `422` |
| `PUT` | `/tasks/{id}` | Update an in-memory task | `200`, `400`, `404`, `422` |
| `DELETE` | `/tasks/{id}` | Delete an in-memory task | `204`, `404`, `422` |

POST accepts a JSON object containing `title`; clients do not need to send `done`. A missing, null, or empty title (`""`) returns `400`. New tasks always start with `done: false`.

PUT requires `done`; when `done` is valid, a missing, null, or empty title returns `400`. Missing `done`, invalid field types, non-integer path IDs, or an absent request body produce validation errors (`422`). Whitespace-only titles are currently accepted.

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

Example response for `/tasks/1` on a freshly initialized database:

```json
{"id":1,"title":"Buy groceries","done":0}
```

## Usage examples and screenshots

The existing Swagger screenshots are retained below as earlier API evidence. They may show earlier response values; the commands and descriptions here reflect the current implementation. Capture additional screenshots for the database persistence checkpoint as the assignment progresses.

### Create a task

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/tasks' -Method Post -ContentType 'application/json' -Body '{"title":"Learn FastAPI"}'
```

Returns **201** with the created task. On a fresh database with five seeds, the response is:

```json
{"id":6,"title":"Learn FastAPI","done":false}
```

The ID depends on existing database rows.

<img width="1240" height="605" alt="Screenshot 2026-08-01 210436" src="https://github.com/user-attachments/assets/a3138e4f-e58d-4250-a310-a4e2ea26d1a7" />

### Get all tasks

```powershell
curl.exe -i http://127.0.0.1:8000/tasks
```
<img width="1237" height="844" alt="Screenshot 2026-08-01 210102" src="https://github.com/user-attachments/assets/c0c70f48-76ba-4e76-9afc-805c54398b8f" />
<img width="1250" height="847" alt="Screenshot 2026-08-01 210129" src="https://github.com/user-attachments/assets/c77e377f-a20e-481d-962d-0fa1dec55856" />
<img width="1234" height="870" alt="Screenshot 2026-08-01 210219" src="https://github.com/user-attachments/assets/6121113e-c0df-4f3d-a841-6624845e5041" />
<img width="1241" height="869" alt="Screenshot 2026-08-01 210330" src="https://github.com/user-attachments/assets/8e005dcd-c914-4874-b444-d078cd99dfea" />

### Update a task

Returns **200** for an ID present in the in-memory list, or **404** when absent. This currently does not change SQLite.

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/tasks/1' -Method Put -ContentType 'application/json' -Body '{"title":"Buy groceries","done":true}'
```
<img width="1225" height="826" alt="Screenshot 2026-08-01 210542" src="https://github.com/user-attachments/assets/6e989d2b-8bd9-4bc8-b1a4-9d1a46543082" />

### Delete a task

This removes a task from the in-memory list only. The database copy remains visible through GET.

```powershell
curl.exe -i -X DELETE http://127.0.0.1:8000/tasks/1
# 204 No Content on success
# 404 Not Found if the task doesn't exist
```
<img width="1229" height="814" alt="Screenshot 2026-08-01 210814" src="https://github.com/user-attachments/assets/c69ab415-e301-4508-b064-b1f24fb17222" />

## Check validation and persistence

Use [Swagger UI](http://127.0.0.1:8000/docs) to send these POST bodies:

| JSON body | Expected status |
|---|---|
| `{"title":"Persistence check"}` | `201`, created task with ID and `done: false` |
| `{"title":""}` | `400` |
| `{}` | `400` |
| `{"title":null}` | `400` |

To verify persistence:

1. Create two tasks and note their returned IDs.
2. Read each using `GET /tasks/{id}` and confirm the titles.
3. Stop Uvicorn with Ctrl+C and restart it with `python -m uvicorn main:app --reload`.
4. Fetch the same IDs again. Both tasks should still exist.

Running `python database.py` again should not duplicate the seeds while the table contains rows. Run PUT and DELETE checks separately: their storage has not yet been migrated.

## Interactive Docs

FastAPI auto-generates interactive API documentation:

- **Swagger UI** — [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc** — [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Project structure

```text
flyrankAI/
|-- main.py        # FastAPI routes, models, and in-memory update/delete operations
|-- database.py    # SQLite connections, initialization, inserts, and reads
|-- tasks.db       # Database file generated by initialization
|-- README.md
|-- .gitignore
`-- venv/          # Local Python environment
```

## Remaining database migration work

- Move PUT and DELETE operations into SQLite so all endpoints share storage.
- Call database initialization during app startup.
- Align the five seed tasks with the lesson's three-task checkpoint.
- Align response formatting with the lesson: it specifies `{"error":"Task not found"}`, while the app currently uses FastAPI's `detail` field and includes the ID.
