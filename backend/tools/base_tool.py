import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

@dataclass
class ToolDefinition:
    name: str
    description: str
    accepted_modalities: List[str]
    capabilities: List[str]
    input_requirements: List[str]
    output_types: List[str]
    confidence_supported: bool = True
    requires_gpu: bool = False
    estimated_vram: str = "4GB"
    mode: str = "LOCAL"

class BaseTool(ABC):
    def __init__(self, definition: ToolDefinition):
        self.definition = definition

    @abstractmethod
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute specialist logic and return domain results."""
        pass

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Structured execution wrapper tracking duration, status, and error safety."""
        start_time = time.time()
        try:
            output = self.run(context)
            duration = round((time.time() - start_time), 3)
            return {
                "tool": self.definition.name,
                "status": "success",
                "result": output.get("result", {}),
                "evidence": output.get("evidence", {}),
                "confidence": output.get("confidence", 0.90),
                "processing_time": duration
            }
        except Exception as e:
            duration = round((time.time() - start_time), 3)
            return {
                "tool": self.definition.name,
                "status": "failed",
                "error": str(e),
                "result": {},
                "evidence": {},
                "confidence": 0.0,
                "processing_time": duration
            }
