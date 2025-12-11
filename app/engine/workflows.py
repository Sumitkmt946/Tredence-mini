from app.engine import tools
from typing import Dict, Any

# Node functions for the Code Review mini-agent. Each node receives (state, params)
# and returns dict updates to the shared state.

async def node_extract(state: Dict[str, Any], params: Dict[str, Any]):
    code = state.get("code", "")
    res = tools.call_tool("extract_functions", code)
    state["functions"] = res["functions"]
    state["function_count"] = res["count"]
    # initialize score and threshold
    state.setdefault("quality_score", 0)
    state.setdefault("threshold", state.get("threshold", 80))
    return {"functions": state["functions"], "function_count": state["function_count"]}

async def node_check_complexity(state: Dict[str, Any], params: Dict[str, Any]):
    funcs = state.get("functions", [])
    total_score = 0
    details = []
    for f in funcs:
        out = tools.call_tool("check_complexity", f["code"])
        details.append({"name": f["name"], "score": out["complexity_score"], "line_count": out["line_count"]})
        total_score += out["complexity_score"]
    avg_score = int(total_score / (len(funcs) or 1))
    # update quality_score as average of complexity and previous score
    state["complexity_details"] = details
    state["quality_score"] = int((state.get("quality_score", 0) + avg_score) / 2) if state.get("quality_score") else avg_score
    return {"complexity_details": details, "quality_score": state["quality_score"]}

async def node_detect_issues(state: Dict[str, Any], params: Dict[str, Any]):
    funcs = state.get("functions", [])
    issues = []
    for f in funcs:
        out = tools.call_tool("detect_issues", f["code"])
        if out["issues"]:
            issues.append({"name": f["name"], "issues": out["issues"]})
    state["issues"] = issues
    # decrement score slightly if issues found
    if issues:
        state["quality_score"] = max(0, state.get("quality_score", 0) - len(issues) * 5)
    return {"issues": issues, "quality_score": state["quality_score"]}

async def node_suggest_improvements(state: Dict[str, Any], params: Dict[str, Any]):
    all_suggestions = []
    for item in state.get("issues", []):
        suggestions = tools.call_tool("suggest_improvements", item["issues"])
        all_suggestions.append({"name": item["name"], "suggestions": suggestions["suggestions"]})
    state["suggestions"] = all_suggestions
    # small improvement to score after suggestions
    if all_suggestions:
        state["quality_score"] = min(100, state.get("quality_score", 0) + 5)
    return {"suggestions": all_suggestions, "quality_score": state["quality_score"]}

def register_example_workflow():
    """
    Pre-registers an example Code Review graph into the in-memory store.
    This helps you start quickly without calling /graph/create.
    """
    from app.storage import save_graph
    graph = {
        "nodes": [
            {"name": "extract", "fn": "node_extract"},
            {"name": "check_complexity", "fn": "node_check_complexity"},
            {"name": "detect_issues", "fn": "node_detect_issues"},
            {"name": "suggest_improvements", "fn": "node_suggest_improvements"}
        ],
        "edges": {
            "extract": "check_complexity",
            "check_complexity": "detect_issues",
            "detect_issues": "suggest_improvements",
            # loop: if quality_score < threshold -> go back to check_complexity
            "suggest_improvements": {
                "cond": "state.get('quality_score',0) < state.get('threshold',80)",
                "true": "check_complexity",
                "false": None
            }
        }
    }
    save_graph(graph)
