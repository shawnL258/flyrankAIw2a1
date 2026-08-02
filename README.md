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

## Usage Examples (Curl with screenshots)

### Create a task

```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn FastAPI"}'
```

```json
{"id": 6, "title": "Learn FastAPI", "done": false}
```

### Get all tasks

```bash
curl http://127.0.0.1:8000/tasks
```

### Update a task

```bash
curl -X PUT http://127.0.0.1:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "done": true}'
```

### Delete a task

```bash
curl -X DELETE http://127.0.0.1:8000/tasks/1
# 204 No Content on success
# 404 Not Found if the task doesn't exist
```

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
