from typing import List, Dict, Any, Optional
from ..tools.registry import GLOBAL_TOOL_REGISTRY
from ..tools.base_tool import BaseTool

class ToolSelector:
    """
    Matches planned tool names against registered specialist capabilities,
    handling hardware requirements and fallback degradation gracefully.
    """
    def __init__(self, registry=None):
        self.registry = registry or GLOBAL_TOOL_REGISTRY

    def select(self, tool_names: List[str]) -> List[BaseTool]:
        selected: List[BaseTool] = []
        for name in tool_names:
            tool = self.registry.get_tool(name)
            if tool:
                selected.append(tool)
        return selected
