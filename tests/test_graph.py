import asyncio
from app.engine.workflows import register_example_workflow
from app.storage import GRAPHS, RUNS, create_run
from app.engine.graph import execute_graph


def test_example_workflow_runs_successfully():
    # Register workflow
    register_example_workflow()

    # Graph must exist
    assert len(GRAPHS) >= 1

    # Get one graph_id
    graph_id = next(iter(GRAPHS.keys()))

    # Create a run with sample code
    run_id = create_run(graph_id, {
        "code": "def foo(x):\n    print(x)\n    return x+1",
        "threshold": 80
    })

    # Run the graph (async)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(execute_graph(graph_id, run_id))

    # Fetch result
    result = RUNS[run_id]

    # Validate workflow completed
    assert result.status == "finished"
    assert "quality_score" in result.current_state
    assert "functions" in result.current_state
