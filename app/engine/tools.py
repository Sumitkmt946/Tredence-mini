from typing import Callable, Dict, Any, List
import re

TOOLS: Dict[str, Callable] = {}

def register_tool(name: str):
    def _wrap(fn: Callable):
        TOOLS[name] = fn
        return fn
    return _wrap

def call_tool(name: str, *args, **kwargs):
    fn = TOOLS.get(name)
    if not fn:
        raise KeyError(f"Tool {name} not registered")
    return fn(*args, **kwargs)

# --- Tools for the Code Review mini-agent (simple rule-based heuristics) ---

@register_tool("extract_functions")
def extract_functions(code_text: str) -> Dict[str, Any]:
    """
    Very naive extractor: finds 'def ' lines and returns function name and lines.
    """
    funcs = []
    lines = code_text.splitlines()
    current = None
    buff = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("def "):
            if current:
                funcs.append({"name": current, "code": "\n".join(buff)})
            # extract name
            m = re.match(r"def\s+([a-zA-Z0-9_]+)\s*\(", stripped)
            current = m.group(1) if m else "unknown"
            buff = [line]
        else:
            if current:
                buff.append(line)
    if current:
        funcs.append({"name": current, "code": "\n".join(buff)})
    return {"functions": funcs, "count": len(funcs)}

@register_tool("check_complexity")
def check_complexity(func_code: str) -> Dict[str, Any]:
    """
    Simple complexity heuristic: lines count + nested indentation levels
    """
    lines = func_code.splitlines()
    line_count = len([l for l in lines if l.strip() != ""])
    indent_levels = max((len(l) - len(l.lstrip())) // 4 for l in lines if l.strip()) if lines else 0
    score = max(0, 100 - (line_count * 2 + indent_levels * 5))
    return {"line_count": line_count, "indent_levels": indent_levels, "complexity_score": score}

@register_tool("detect_issues")
def detect_issues(func_code: str) -> Dict[str, Any]:
    issues = []
    if "TODO" in func_code or "FIXME" in func_code:
        issues.append("contains TODO/FIXME")
    if "print(" in func_code:
        issues.append("debug prints present")
    if len(func_code) > 500:
        issues.append("function too long")
    # too many params
    first_line = func_code.splitlines()[0] if func_code.splitlines() else ""
    if "(" in first_line and ")" in first_line:
        params = first_line.split("(", 1)[1].split(")", 1)[0]
        if params.strip():
            if len([p for p in params.split(",") if p.strip()]) > 5:
                issues.append("too many parameters")
    return {"issues": issues, "issue_count": len(issues)}

@register_tool("suggest_improvements")
def suggest_improvements(issues: list) -> Dict[str, Any]:
    suggestions = []
    for i in issues:
        if "TODO" in i or "FIXME" in i:
            suggestions.append("Resolve TODOs or create tasks")
        if "debug prints" in i:
            suggestions.append("Remove debug prints or use logging")
        if "function too long" in i:
            suggestions.append("Split the function into smaller helpers")
        if "too many parameters" in i:
            suggestions.append("Use dataclass or group params into an object")
    if not suggestions:
        suggestions.append("No suggestions; looks fine")
    return {"suggestions": suggestions}
