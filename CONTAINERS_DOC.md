Stage 0:
docker ps showing a running container
<img width="938" height="128" alt="image" src="https://github.com/user-attachments/assets/45734f22-1c70-4b5c-bc90-8d76eee5cb99" />

docker exec -it <db_name> psql -U <user> -d <tasks>
<img width="713" height="258" alt="image" src="https://github.com/user-attachments/assets/c80faec9-ad97-440d-85c2-8977a495cd33" />

Stage 1:
docker exec postgres then check database tables and selected all rows from tasks after 3 attempts
<img width="607" height="822" alt="image" src="https://github.com/user-attachments/assets/b13c7659-0538-4671-8ee2-1fe0229a59b2" />

Stage 2:
Testing GET and GET ?={id} endpoints
<img width="802" height="170" alt="image" src="https://github.com/user-attachments/assets/80b8a497-dd69-4235-bd92-61d687877fda" />

Stage 3:
POST, PUT, and DELETE in /tasks endpoint returning all the right corresponding endpoints
<img width="921" height="372" alt="image" src="https://github.com/user-attachments/assets/a8edc112-057f-4e65-8387-988c690e882b" />

Stage 4:
Made a DockerFile and Created TEST1TASK, TEST2TASK, and TEST3TASK then compose down and up to check persistance
<img width="912" height="422" alt="Screenshot 2026-10-17 221124" src="https://github.com/user-attachments/assets/159e284f-8c37-4a71-bc68-7d71f7bd64e3" />


---

## Containers: how this stack runs

## Services (`compose.yaml`)

| Service | Image | Role |
|---|---|---|
| `db` | `postgres:17` | PostgreSQL server. Data is stored in the named volume `taskdata` mounted at `/var/lib/postgresql/data`. Has a `pg_isready` healthcheck. Published on host port 5433. |
| `api` | built from `Dockerfile` | FastAPI app served by Uvicorn on port 8000. Starts only after `db` is healthy. |

## How they connect

- Inside the compose network the API reaches the database at host `db`, port 5432 (service name, not `localhost`).
- `compose.yaml` builds `DATABASE_URL` from `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, which Compose reads from `.env`. No password is hardcoded in any committed file.
- When running the API on the host instead, `database.py` loads `DATABASE_URL` from `.env` (`localhost:5433`).

## Dockerfile

`python:3.12-slim` base, install `requirements.txt` first (so the dependency layer is cached), copy `main.py` and `database.py`, run `uvicorn main:app --host 0.0.0.0 --port 8000`. `.dockerignore` keeps `.env`, `venv/`, `.git/` and the old `tasks.db` out of the image.

## Persistence

Rows live in the `taskdata` volume, not in the container. `docker compose down` removes containers but keeps the volume, so tasks survive. `docker compose down -v` deletes the volume and all data.

## Useful commands

```bash
docker compose up --build            # build and start everything
docker compose up -d db              # database only
docker compose exec db psql -U postgres -d tasks
docker compose logs -f api
docker compose down                  # stop, keep data
docker compose down -v               # stop, delete data
```

## Gotchas hit

- `postgres:latest` (v18+) refuses a volume mounted at `/var/lib/postgresql/data` and exits; the image is pinned to `postgres:17`.
- Port 5432 was already used by another Postgres on the host, so the container is published as `5433:5432`.
