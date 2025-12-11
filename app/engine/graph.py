import asyncio
from typing import Dict, Any, Optional
from app.storage import GRAPHS, RUNS, append_log, update_run_state, finish_run
from app.engine import tools
import copy
import inspect

def _get_node_fn(graph_spec: dict, node_name: str):
    node_entry = next((n for n in graph_spec.get("nodes", []) if n["name"] == node_name), None)
    if not node_entry:
        return None, None
    fn_name = node_entry["fn"]
    params = node_entry.get("params") or {}
    # node functions are expected to be in app.engine.workflows module
    from app.engine import workflows
    fn = getattr(workflows, fn_name, None)
    return fn, params

def _resolve_edge(edges: dict, current: str, state: dict) -> Optional[str]:
    """
    Edges can be:
      - string -> next node
      - dict with 'cond' and 'true'/'false' keys
    """
    target = edges.get(current)
    if isinstance(target, str) or target is None:
        return target
    if isinstance(target, dict):
        cond = target.get("cond")
        true_t = target.get("true")
        false_t = target.get("false")
        if cond is None:
            return true_t
        # WARNING: using eval here with restricted globals. This is simple but not fully secure.
        try:
            allowed_globals = {"__builtins__": None}
            allowed_locals = {"state": state}
            res = eval(cond, allowed_globals, allowed_locals)
            return true_t if res else false_t
        except Exception:
            # if eval fails, default to false branch
            return false_t
    return None

async def _maybe_await(fn, *args, **kwargs):
    if inspect.iscoroutinefunction(fn):
        return await fn(*args, **kwargs)
    else:
        # run sync function in threadpool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: fn(*args, **kwargs))

async def execute_graph(graph_id: str, run_id: str):
    graph_spec = GRAPHS.get(graph_id)
    if not graph_spec:
        update_run_state(run_id, status="failed")
        return
    edges = graph_spec.get("edges", {})
    # pick first node as entry
    nodes = graph_spec.get("nodes", [])
    if not nodes:
        update_run_state(run_id, status="failed")
        return
    entry = nodes[0]["name"]
    current = entry
    state = copy.deepcopy(RUNS[run_id].current_state)
    step_limit = 1000
    steps = 0

    while current and steps < step_limit:
        steps += 1
        fn, params = _get_node_fn(graph_spec, current)
        update_run_state(run_id, current_node=current)
        # log before running
        append_log(run_id, current, f"starting node {current}", copy.deepcopy(state))
        try:
            # node functions should accept and return a state dict or partial updates
            result = await _maybe_await(fn, state, params or {})
            # result may be dict of updates or a full state
            if isinstance(result, dict):
                # merge
                state.update(result)
            # persist
            append_log(run_id, current, f"completed node {current}", copy.deepcopy(state))
        except Exception as e:
            append_log(run_id, current, f"error: {repr(e)}", copy.deepcopy(state))
            update_run_state(run_id, status="failed")
            return
        # resolve next
        next_node = _resolve_edge(edges, current, state)
        current = next_node
        update_run_state(run_id, current_state=state)
        # small sleep to simulate async steps and allow external polling
        await asyncio.sleep(0.01)

    finish_run(run_id, state)
