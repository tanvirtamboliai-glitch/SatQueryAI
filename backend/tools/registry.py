from typing import Dict, List, Optional
from .base_tool import BaseTool, ToolDefinition
from .geochat_tool import GeoChatTool
from .geoground_tool import GeoGroundTool
from .change_detection_tool import ChangeDetectionTool
from .change_captioning_tool import ChangeCaptioningTool
from .change_vqa_tool import ChangeVQATool
from .optical_analysis_tool import OpticalAnalysisTool
from .sar_analysis_tool import SARAnalysisTool
from .multimodal_alignment_tool import MultimodalAlignmentTool
from .multimodal_fusion_tool import MultimodalFusionTool
from .segmentation_tool import SegmentationTool
from .remoteclip_tool import RemoteCLIPTool
from .prithvi_tool import PrithviTool
from .clay_tool import ClayTool
from .geospatial_tool import GeospatialTool

class ToolRegistry:
    """Central registry maintaining specialist tools with capability and modality lookups."""
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        tools = [
            GeoChatTool(),
            GeoGroundTool(),
            ChangeDetectionTool(),
            ChangeCaptioningTool(),
            ChangeVQATool(),
            OpticalAnalysisTool(),
            SARAnalysisTool(),
            MultimodalAlignmentTool(),
            MultimodalFusionTool(),
            SegmentationTool(),
            RemoteCLIPTool(),
            PrithviTool(),
            ClayTool(),
            GeospatialTool()
        ]
        for t in tools:
            self.register(t)

    def register(self, tool: BaseTool):
        self._tools[tool.definition.name] = tool

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def list_tools(self) -> List[ToolDefinition]:
        return [t.definition for t in self._tools.values()]

    def filter_by_modality(self, modality: str) -> List[BaseTool]:
        return [
            t for t in self._tools.values()
            if modality.upper() in t.definition.accepted_modalities
        ]

    def filter_by_capability(self, capability: str) -> List[BaseTool]:
        return [
            t for t in self._tools.values()
            if capability.lower() in t.definition.capabilities
        ]

GLOBAL_TOOL_REGISTRY = ToolRegistry()
