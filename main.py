from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import database

@asynccontextmanager
async def lifespan(app: FastAPI):
    database.check_database()
    yield


app = FastAPI(lifespan=lifespan)

@app.exception_handler(RequestValidationError)
async def handle_request_validation(request: Request, exc: RequestValidationError):
    response = await request_validation_exception_handler(request, exc)
    route = request.scope.get("route")
    if (
        (request.method, getattr(route, "path", None))
        in {("POST", "/tasks"), ("PUT", "/tasks/{id}")}
        and all(error["loc"][0] == "body" for error in exc.errors())
    ):
        return JSONResponse(status_code=400, content={"error": "Invalid request body"})
    return response

@app.exception_handler(HTTPException)
async def handle_http_error(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
        headers=exc.headers,
    )

@app.get("/")
async def root():
    return {"name" : "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
async def health():
   return {"status": "ok"}

@app.get("/tasks")
async def read_tasks():
    return database.select_task()

@app.get("/tasks/{id}")
async def read_task(id: int):
    get_task = database.where_task(id)
    if not get_task:
        raise HTTPException(status_code=404, detail="Task not found")

    return get_task

class TaskCreate(BaseModel):
    title: str | None = None

@app.post("/tasks", status_code=201)
async def create_task(task_in: TaskCreate):

    if task_in.title == "" or task_in.title is None:
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    return database.create_task(task_in.title, False)

class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool

@app.put("/tasks/{id}")
async def update_task(id: int, task_in: TaskUpdate):
    if task_in.title == "" or task_in.title is None:
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    if database.where_task(id) is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return database.update_task(id, task_in.title, task_in.done)

@app.delete("/tasks/{id}", status_code=204)
async def delete_task(id: int):
    if database.where_task(id) is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return database.delete_task(id)
