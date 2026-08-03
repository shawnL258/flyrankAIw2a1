
# Task API

A simple RESTful API built with **FastAPI** for managing tasks. Created as a small assignment project to demonstrate CRUD operations with proper HTTP status codes.

## Tech Stack

- **Python 3.12**
- **FastAPI** — async web framework
- **Pydantic** — request/response validation
- **Uvicorn** — ASGI server

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/flyrankAI.git
cd flyrankAI
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn
```

### 4. Run the server

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Endpoints

| Method   | Endpoint       | Description          | Status Codes |
|----------|----------------|----------------------|--------------|
| `GET`    | `/`            | API info             | `200`        |
| `GET`    | `/health`      | Health check         | `200`        |
| `GET`    | `/tasks`       | List all tasks       | `200`        |
| `GET`    | `/tasks/{id}`  | Get a task by ID     | `200`, `404` |
| `POST`   | `/tasks`       | Create a new task    | `201`, `400` |
| `PUT`    | `/tasks/{id}`  | Update a task        | `200`, `400`, `404` |
| `DELETE` | `/tasks/{id}`  | Delete a task        | `204`, `404` |

## Usage Examples (Curl with Swagger screenshots)

### Create a task

```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn FastAPI"}'
```

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

```bash
curl -X PUT http://127.0.0.1:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "done": true}'
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

## Project Structure

```
flyrankAI/
├── main.py          # API application
├── .gitignore
├── README.md
└── venv/            # Virtual environment (not tracked)
```

## Notes

- Tasks are stored **in memory** — data resets when the server restarts.
- The app ships with 5 sample tasks for quick testing.
