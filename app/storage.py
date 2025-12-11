import uuid
from app.models import RunStateModel, LogEntry

GRAPHS = {}  # graph_id -> graph_spec (dict)
RUNS = {}    # run_id -> RunStateModel.dict()

def save_graph(graph_spec: dict) -> str:
    graph_id = uuid.uuid4().hex
    GRAPHS[graph_id] = graph_spec
    return graph_id

def create_run(graph_id: str, initial_state: dict) -> str:
    run_id = uuid.uuid4().hex
    run = RunStateModel(
        run_id=run_id,
        graph_id=graph_id,
        status="running",
        current_node=None,
        current_state=initial_state,
        logs=[]
    )
    RUNS[run_id] = run
    return run_id

def update_run_state(run_id: str, **kwargs):
    run = RUNS.get(run_id)
    if not run:
        return
    for k, v in kwargs.items():
        setattr(run, k, v)
    RUNS[run_id] = run

def append_log(run_id: str, node: str, message: str, state_snapshot: dict):
    run = RUNS.get(run_id)
    if not run:
        return
    run.logs.append(LogEntry(node=node, message=message, state_snapshot=state_snapshot))
    run.current_state = state_snapshot
    RUNS[run_id] = run

def finish_run(run_id: str, final_state: dict):
    run = RUNS.get(run_id)
    if not run:
        return
    run.status = "finished"
    run.current_state = final_state
    RUNS[run_id] = run
