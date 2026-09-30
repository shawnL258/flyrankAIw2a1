from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import database

app = FastAPI()
class Task(BaseModel):
    id: int
    title: str
    done: bool = False

@app.get("/")
async def root():
    return {"name" : "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
async def health():
   return {"status": "ok"}

tasks = [
    Task(id=1, title="Buy groceries", done=False),
    Task(id=2, title="Read FastAPI docs", done=True),
    Task(id=3, title="Learn FastAPI", done=False),
    Task(id=4, title="Build a FastAPI app", done=False),
    Task(id=5, title="Deploy the FastAPI app", done=False),
]

@app.get("/tasks")
async def read_tasks():
    get_task = database.select_task()
    if not get_task:
        raise HTTPException(status_code=404, detail="Tasks not found")
    return get_task

@app.get("/tasks/{id}")
async def read_task(id: int):
    get_task = database.where_task(id)
    if not get_task:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")

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

    for task in tasks:
        if task.id == id:
            task.title = task_in.title
            task.done = task_in.done
            return task
    raise HTTPException(status_code=404, detail=f"Task {id} not found")

@app.delete("/tasks/{id}", status_code=204)
async def delete_task(id: int):
    for i, task in enumerate(tasks):
        if task.id == id:
            tasks.pop(i)
            return
    raise HTTPException(status_code=404, detail=f"Task {id} not found")
