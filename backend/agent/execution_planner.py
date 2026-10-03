import time
from typing import Dict, Any, List
from .task_planner import AgentPlan
from ..tools.base_tool import BaseTool

class ExecutionPlanner:
    """
    Executes ordered specialist tools, feeds forward intermediate raster and tensor representations,
    and logs observable step-by-step traces without exposing hidden chain-of-thought.
    """
    def execute_plan(
        self,
        plan: AgentPlan,
        tools: List[BaseTool],
        initial_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        context = dict(initial_context)
        trace: List[Dict[str, Any]] = []
        tool_results: Dict[str, Any] = {}
        step_idx = 1

        for tool in tools:
            tool_name = tool.definition.name
            t0 = time.time()

            # Execute tool with current context
            res = tool.execute(context)
            duration_ms = round(res["processing_time"] * 1000.0, 1)

            # Record observable execution trace
            trace.append({
                "step_number": step_idx,
                "name": tool.definition.name.replace("_", " ").title(),
                "status": res["status"],
                "details": res.get("evidence", {}).get("textual_evidence") or tool.definition.description[:80] + "...",
                "duration_ms": duration_ms,
                "timestamp": time.strftime("%H:%M:%S")
            })
            step_idx += 1

            # Store result
            tool_results[tool_name] = res

            # Feed forward context artifacts for downstream tools
            if "result" in res:
                context[f"{tool_name}_result"] = res["result"]
            if "evidence" in res:
                evidence = res["evidence"]
                for k, v in evidence.items():
                    context[k] = v

        return {
            "trace": trace,
            "tool_results": tool_results,
            "final_context": context
        }
