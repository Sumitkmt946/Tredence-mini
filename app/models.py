from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class NodeSpec(BaseModel):
    name: str
    fn: str
    params: Optional[Dict[str, Any]] = None

class EdgeCond(BaseModel):
    cond: Optional[str] = None
    true: Optional[str] = None
    false: Optional[str] = None

class GraphSpecModel(BaseModel):
    nodes: List[NodeSpec]
    edges: Dict[str, Any] = Field(default_factory=dict)

class RunRequestModel(BaseModel):
    graph_id: str
    initial_state: Optional[Dict[str, Any]] = Field(default_factory=dict)

class LogEntry(BaseModel):
    node: str
    message: Optional[str] = None
    state_snapshot: Optional[Dict[str, Any]] = None

class RunStateModel(BaseModel):
    run_id: str
    graph_id: str
    status: str
    current_node: Optional[str] = None
    current_state: Dict[str, Any] = Field(default_factory=dict)
    logs: List[LogEntry] = Field(default_factory=list)
