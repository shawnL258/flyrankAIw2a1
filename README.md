# Task API

A FastAPI task CRUD API backed by PostgreSQL. The whole stack (API + database) runs in Docker with one command.

## Run it (one command)

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/).

```bash
git clone <this repo> && cd flyrankAI
cp .env.example .env      # then edit the password in .env
docker compose up --build
```

The API is at [http://127.0.0.1:8000](http://127.0.0.1:8000) (Swagger UI at `/docs`). On first start the API creates the `tasks` table and seeds three example tasks only if the table is empty. Data lives in the `taskdata` volume, so it survives `docker compose down` and `up`.

Stop and keep data: `docker compose down`. Stop and wipe data: `docker compose down -v`.

## Configuration (`.env`)

Copy [`.env.example`](.env.example) to `.env`. `.env` is git-ignored; never commit it.

| Variable | Purpose |
|---|---|
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | Credentials and database name for the `db` container |
| `DATABASE_URL` | Connection string used when running the API on your machine (`localhost:5433`). Inside compose the API gets its own URL pointing at the `db` service. |

The database is published on host port **5433** (container port 5432) so it does not clash with a local PostgreSQL install.

## Tech stack

- Python 3.12, FastAPI, Pydantic, Uvicorn
- PostgreSQL 17 (official `postgres:17` image) through `psycopg` 3 with parameterized queries (`%s`)
- Docker + Docker Compose, config via `.env` (`python-dotenv` for local runs)

`postgres:17` is pinned on purpose: the `latest` image (18+) expects the volume mounted at `/var/lib/postgresql`, and mounting `/var/lib/postgresql/data` makes the container exit.

## Run without Docker for the API (optional)

Start only the database, then run the API from a virtualenv (Windows PowerShell):

```powershell
docker compose up -d db
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

## Database access

```bash
docker compose exec db psql -U postgres -d tasks
```

Then `\dt`, `SELECT * FROM tasks;`, `\q`.

## Database structure

| Column | Declaration | Purpose |
|---|---|---|
| `id` | `SERIAL PRIMARY KEY` | Automatically assigned task ID |
| `title` | `TEXT NOT NULL` | Task description |
| `done` | `BOOLEAN NOT NULL` | Completion state |

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

Returns **200** with the updated task, or **404** when absent. The change is committed to PostgreSQL and is immediately visible through GET.

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/tasks/1' -Method Put -ContentType 'application/json' -Body '{"title":"Buy groceries","done":true}'
```
<img width="1225" height="826" alt="Screenshot 2026-08-01 210542" src="https://github.com/user-attachments/assets/6e989d2b-8bd9-4bc8-b1a4-9d1a46543082" />

### Delete a task

This deletes the task from PostgreSQL. A later GET for that ID returns **404**.

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
|-- main.py          # FastAPI routes, startup, models, and error handling
|-- database.py      # PostgreSQL connection (psycopg) and all CRUD queries
|-- Dockerfile       # Image for the API
|-- compose.yaml     # api + db services and the taskdata volume
|-- .env.example     # Template for .env (committed); .env itself is git-ignored
|-- tests/           # Regression tests (run against a throwaway Postgres database)
`-- README.md
```

## Proof: curl -i and the database

```text
$ curl -i http://127.0.0.1:8000/tasks
HTTP/1.1 200 OK
server: uvicorn
content-type: application/json

[{"id":2,"title":"Read FastAPI docs","done":true},{"id":3,"title":"Learn FastAPI","done":false}, ...]
```
<img width="802" height="170" alt="676674564-80b8a497-dd69-4235-bd92-61d687877fda" src="https://github.com/user-attachments/assets/c1bdbbc8-a90e-4b24-93d3-f48322b0523b" />

Data in Postgres (`docker exec flyrankai-db-1 psql -U postgres -d tasks -c "\dt" -c "SELECT * FROM tasks;"`):

<img width="607" height="822" alt="psql \dt and SELECT * FROM tasks" src="https://github.com/user-attachments/assets/b13c7659-0538-4671-8ee2-1fe0229a59b2" />

Persistence check: create tasks, run `docker compose down` then `docker compose up`, and the tasks are still returned because the `taskdata` volume keeps them.
<img width="912" height="422" alt="676692542-159e284f-8c37-4a71-bc68-7d71f7bd64e3" src="https://github.com/user-attachments/assets/1c9b5901-057e-4846-8be0-6dda7693b4b3" />

## Migration note

Earlier versions stored tasks in SQLite (`tasks.db`). The existing rows were copied into Postgres with their original IDs, and the ID sequence was advanced past the highest ID so new tasks do not collide.

Check COTAINERS_DOC.md for more info

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


## Why PostgreSQL in a container

Postgres runs as its own server, so the app and database are separate programs that talk over a connection string kept in `.env`. Running it as a container means no local install, the same version everywhere, and a named volume keeps the data when the container is recreated. Compose starts both services together; the `api` waits for the database healthcheck (`pg_isready`) before starting.

## Verification

```powershell
docker compose up -d db
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

Tests create and use a separate `tasks_test` database on the same server, so your real tasks are never touched. They cover startup, exactly three seeds, missing-table recovery, parameter binding, CRUD, restart persistence, response types, and error codes.

See [the HTTP verification transcript](docs/crud-verification.txt) for an earlier `curl -i` cycle (recorded against the SQLite version; behavior is unchanged).
