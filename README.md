# Task API

A FastAPI learning project for task CRUD operations, using SQLite for all task CRUD operations.

## Current implementation

- GET, POST, PUT, and DELETE all read or modify `tasks.db` through parameterized SQL.
- Startup creates the database and table if missing, then seeds three examples if the table is empty. Existing nonempty databases retain their tasks.
- Changes survive server restarts. Committed DB Browser changes appear on the next API request without restarting.
- SQLite stores completion as 0/1; API responses consistently use JSON booleans.

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
python -m pip install -r requirements.txt
```

### 3. Start the API

```powershell
python -m uvicorn main:app --reload
```

No separate database setup command is needed. Startup creates `tasks.db` beside `database.py` and ensures the `tasks` table exists, even when the file already exists. Three examples are inserted only when the table is empty; repeated starts do not duplicate existing tasks. If you delete every task, the next startup seeds the empty table again.

The database is git-ignored so a fresh clone starts with its own data. An older local database may contain more than three rows; startup deliberately preserves them.

The API runs at [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Database structure

| Column | Declaration | Purpose |
|---|---|---|
| `id` | `INTEGER PRIMARY KEY AUTOINCREMENT` | Automatically assigned task ID |
| `title` | `TEXT NOT NULL` | Task description |
| `done` | `BOOLEAN NOT NULL` | Completion state, stored as `0` or `1` |

All task responses expose `done` as a JSON boolean (`false` or `true`).

## API endpoints

| Method | Endpoint | Storage / purpose | Status codes |
|---|---|---|---|
| `GET` | `/` | API information | `200` |
| `GET` | `/health` | App health response | `200` |
| `GET` | `/tasks` | List database tasks | `200` (empty table returns `[]`) |
| `GET` | `/tasks/{id}` | Read one database task | `200`, `404`, `422` |
| `POST` | `/tasks` | Create a database task | `201`, `400` |
| `PUT` | `/tasks/{id}` | Update a database task | `200`, `400`, `404`, `422` |
| `DELETE` | `/tasks/{id}` | Delete a database task | `204`, `404`, `422` |

POST accepts a JSON object containing `title`; clients do not need to send `done`. A missing, null, or empty title (`""`) returns `400`. New tasks always start with `done: false`.

PUT requires `title` and `done`. Invalid POST/PUT bodies, including missing fields, invalid field types, absent bodies, and malformed JSON, return `400` with a JSON error message. Non-integer path IDs return `422`. Whitespace-only titles are currently accepted.

A missing task returns `404`, not `400`, with a response such as:

```json
{"error":"Task not found"}
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
{"id":1,"title":"Buy groceries","done":false}
```

## Usage examples and screenshots

The existing Swagger screenshots are retained below as earlier API evidence. They may show earlier response values; the commands and descriptions here reflect the current implementation. Capture additional screenshots for the database persistence checkpoint as the assignment progresses.

### Create a task

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/tasks' -Method Post -ContentType 'application/json' -Body '{"title":"Learn FastAPI"}'
```

Returns **201** with the created task. On a fresh database with three seeds, the response is:

```json
{"id":4,"title":"Learn FastAPI","done":false}
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

Returns **200** with the updated task, or **404** when absent. The change is committed to SQLite and is immediately visible through GET.

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/tasks/1' -Method Put -ContentType 'application/json' -Body '{"title":"Buy groceries","done":true}'
```
<img width="1225" height="826" alt="Screenshot 2026-08-01 210542" src="https://github.com/user-attachments/assets/6e989d2b-8bd9-4bc8-b1a4-9d1a46543082" />

### Delete a task

This deletes the task from SQLite. A later GET for that ID returns **404**.

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

Repeated startup preserves existing tasks without duplicating seeds while the table contains rows.

## Interactive Docs

FastAPI auto-generates interactive API documentation:

- **Swagger UI** — [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc** — [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Project structure

```text
flyrankAI/
|-- main.py        # FastAPI routes, startup, models, and error handling
|-- database.py    # SQLite initialization and all CRUD queries
|-- tasks.db       # Database file generated by initialization
|-- README.md
|-- .gitignore
`-- venv/          # Local Python environment
```

## Stage 4: SQL by hand
List all tasks
<img width="586" height="453" alt="Screenshot 2026-10-01 205722" src="https://github.com/user-attachments/assets/975553bf-e3b7-405f-8bf4-b82c1c47a10c" />

Only completed tasks
<img width="328" height="263" alt="Screenshot 2026-10-01 205804" src="https://github.com/user-attachments/assets/dca06d71-644a-4a30-9383-454c87f2f6cf" />

How many tasks are there?
<img width="270" height="248" alt="Screenshot 2026-10-01 205852" src="https://github.com/user-attachments/assets/2232eb4e-2868-4fdc-9a75-667bda8b0de8" />

Mark every task completed
<img width="372" height="473" alt="Screenshot 2026-10-01 210011" src="https://github.com/user-attachments/assets/2d612a62-4b8e-4541-b125-7d50bd2011cc" />

Delete all completed tasks
<img width="480" height="476" alt="Screenshot 2026-10-01 210355" src="https://github.com/user-attachments/assets/fecff8dc-fca6-4123-8a2d-969254203d8f" />

I ran all the sample queries in DB Browser for SQLite. I also inserted a task and listed the rows:

```sql
INSERT INTO tasks (title, done) VALUES ('Code with Claude', 0);
SELECT * FROM tasks;
```

The SELECT result included the new task with ID 11. After saving the database changes, I fetched `/tasks/11` through the API without restarting the server.

It returned the following response (the current API now serializes `done` as a boolean):

```json
{
  "id": 11,
  "title": "Code with Claude",
  "done": 0
}
```

Status: **200**.

Screenshot proof:
<img width="503" height="382" alt="Screenshot 2026-10-01 215159" src="https://github.com/user-attachments/assets/67797946-80dc-49e4-8df5-64ca8e8e63de" />


## Why SQLite

SQLite keeps this small project's data in a single file, needs no separate database server, and preserves tasks across restarts. Python includes `sqlite3`, so no additional database driver is required. The API and DB Browser read the same file; click **Write Changes** in DB Browser to commit edits before checking the API.

## Verification

Install test dependencies and run the isolated regression checks:

```powershell
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

Tests use temporary databases and do not modify your own `tasks.db`. They cover startup, exactly three seeds, missing-table recovery, parameter binding, CRUD, restart persistence, response types, and error codes.

See [the HTTP verification transcript](docs/crud-verification.txt) for a real `curl -i` cycle against a separate server and temporary database, including a full process restart. The clean-source check uses a copy of the application with the installed Python environment; it is not a fresh dependency installation or proof that unpushed changes are already on GitHub.
