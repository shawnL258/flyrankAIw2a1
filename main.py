from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

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
    return tasks

@app.get("/tasks/{id}")
async def read_tasks(id: int):
    for task in tasks:
        if task.id == id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {id} not found")

class TaskCreate(BaseModel):
    title: str

@app.post("/tasks")
async def create_task(task_in: TaskCreate):
    if task_in.title == "" or task_in.title is None:
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    next_id = max(t.id for t in tasks) + 1 if tasks else 1
    new_task = Task(id=next_id, title=task_in.title, done=False)
    tasks.append(new_task)
    return new_task