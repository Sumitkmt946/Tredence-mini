from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
from app.storage import GRAPHS, RUNS, save_graph, create_run, update_run_state
from app.models import GraphSpecModel, RunRequestModel, RunStateModel
from app.engine.graph import execute_graph
from app.engine.workflows import register_example_workflow

app = FastAPI(title="Mini Agent Workflow Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register an example graph on startup
@app.on_event("startup")
def startup_event():
    register_example_workflow()

class CreateGraphResponse(BaseModel):
    graph_id: str

class RunResponse(BaseModel):
    run_id: str

@app.post("/graph/create", response_model=CreateGraphResponse)
def create_graph(spec: GraphSpecModel):
    graph_id = save_graph(spec.dict())
    return {"graph_id": graph_id}

@app.post("/graph/run", response_model=RunResponse)
def run_graph(req: RunRequestModel, background_tasks: BackgroundTasks):
    graph_id = req.graph_id
    initial_state = req.initial_state or {}
    if graph_id not in GRAPHS:
        raise HTTPException(status_code=404, detail="Graph not found")
    run_id = create_run(graph_id, initial_state)
    # run in background
    background_tasks.add_task(execute_graph, graph_id, run_id)
    return {"run_id": run_id}

@app.get("/graph/state/{run_id}", response_model=RunStateModel)
def get_run_state(run_id: str):
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
