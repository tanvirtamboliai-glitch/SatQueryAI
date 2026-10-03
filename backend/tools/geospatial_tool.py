from typing import Dict, Any
from .base_tool import BaseTool, ToolDefinition
from ..preprocessing.metadata import extract_geospatial_metadata

class GeospatialTool(BaseTool):
    def __init__(self):
        defn = ToolDefinition(
            name="geospatial",
            description="Inspects raster geospatial projection, CRS, bounds, affine geotransform, and GSD resolution.",
            accepted_modalities=["OPTICAL", "SAR", "MULTISPECTRAL", "TEMPORAL_PAIR", "OPTICAL_SAR"],
            capabilities=["metadata_inspection", "crs_validation", "coordinate_conversion"],
            input_requirements=["file_path"],
            output_types=["geospatial_metadata"],
            confidence_supported=True,
            requires_gpu=False,
            estimated_vram="1GB"
        )
        super().__init__(defn)

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        fpath = context.get("file_path") or context.get("optical_path") or context.get("image1_path")
        if not fpath:
            raise ValueError("File path required for geospatial inspection.")
        meta = extract_geospatial_metadata(fpath)
        return {
            "result": meta,
            "evidence": {
                "textual_evidence": f"Geospatial projection: {meta['crs']}, resolution: {meta['resolution']}m."
            },
            "confidence": 1.0
        }
