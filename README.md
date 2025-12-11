# 🚀 Mini Agent Workflow Engine — AI Engineering Internship Assignment

This project implements a **minimal workflow/graph engine** using **FastAPI**, created as part of the **AI Engineering Intern Case Study**.  
It supports:

- Node-based computation  
- Directed edges  
- Shared state  
- Conditional branching  
- Looping  
- Tool registry  
- Background execution  
- Execution logs  
- Example Agent Workflow (Code Review Mini-Agent)

The goal is clarity, correctness, and clean engineering — not complexity.

---

## 📁 Project Structure

<img width="717" height="349" alt="image" src="https://github.com/user-attachments/assets/98e1cd32-8434-4e6b-ba5e-f3e831e439a4" />


---

## 🔧 Features Implemented

### ✅ Workflow Engine
- Node definitions (Python functions)
- Directed edges between nodes
- Shared state propagation
- Conditional branching via `cond`
- Looping until condition satisfied
- Sync + async node support

### ✅ Tool Registry
- Simple rule-based tools
- Functions for extraction, complexity check, issue detection, suggestions

### ✅ FastAPI Endpoints

| Method | Endpoint | Description |
|--------|-----------|--------------|
| **POST** | `/graph/create` | Create a graph |
| **POST** | `/graph/run` | Execute a graph (background) |
| **GET** | `/graph/state/{run_id}` | Fetch execution state + logs |

### ✅ Example Workflow Implemented (Option A — Code Review Mini-Agent)
Steps:
1. Extract functions  
2. Check complexity  
3. Detect issues  
4. Suggest improvements  
5. Loop until `quality_score >= threshold`

---

## ▶️ How to Run

### 1️⃣ Install Dependencies
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
Start Server
```bash
uvicorn app.main:app --reload
```
Open Swagger UI:
👉 http://127.0.0.1:8000/docs

Create a Graph
```base
{
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
    "suggest_improvements": {
      "cond": "state.get('quality_score',0) < state.get('threshold',80)",
      "true": "check_complexlicity",
      "false": null
    }
  }
}
```
Example Response:
```base
{
  "graph_id": "5842016015b946299e1f916a98ab4846"
}
```

Run the Graph:
```base
{
  "graph_id": "5842016015b946299e1f916a98ab4846",
  "initial_state": {
    "code": "def add(a,b):\n    return a+b\n\ndef slow(n):\n    for i in range(n):\n        print(i)\n    return n",
    "threshold": 85
  }
}
```
Example Response:
```base
{
  "run_id": "90c33c197e0045b880cc5919c1776e9b"
}
```
Check Final Execution State
```base
{
  "run_id": "90c33c197e0045b880cc5919c1776e9b",
  "graph_id": "5842016015b946299e1f916a98ab4846",
  "status": "finished",
  "current_state": {
    "function_count": 2,
    "quality_score": 86,
    "functions": [
      {"name": "add", "code": "def add(a,b):\n    return a+b"},
      {"name": "slow", "code": "def slow(n):\n    for i in range(n):\n        print(i)\n    return n"}
    ],
    "issues": [...],
    "suggestions": [...],
    "complexity_details": [...]
  },
  "logs": [
    {"node": "extract", "message": "starting node extract", ...},
    {"node": "extract", "message": "completed node extract", ...},
    {"node": "check_complexity", "message": "starting node check_complexity", ...},
    ...
  ]
}
```
