import unittest
import numpy as np
from PIL import Image
from backend.preprocessing.optical import normalize_band, compute_spectral_indices
from backend.preprocessing.sar import linear_to_db, apply_speckle_filter
from backend.preprocessing.alignment import align_multimodal_rasters
from backend.preprocessing.metadata import compute_spatial_overlap
from backend.tools.registry import GLOBAL_TOOL_REGISTRY
from backend.agent.remote_sensing_agent import RemoteSensingAgent
from backend.app.schemas.schemas import PlanRequest
from backend.app.api.endpoints import generate_agent_plan, list_models
from backend.app.services.sample_generator import generate_samples_if_needed, get_sample_scenarios

class TestAgenticSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        generate_samples_if_needed()
        cls.agent = RemoteSensingAgent()
        cls.scenarios = get_sample_scenarios()

    def test_optical_preprocessing(self):
        # 1-channel band normalization
        arr = np.random.randint(50, 4000, (64, 64), dtype=np.uint16)
        norm = normalize_band(arr, 2.0, 98.0)
        self.assertEqual(norm.dtype, np.uint8)
        self.assertEqual(norm.shape, (64, 64))

        # Multi-band spectral indices (3 bands, e.g. R, G, NIR)
        multi = np.random.randint(50, 4000, (3, 64, 64), dtype=np.uint16)
        indices = compute_spectral_indices(multi)
        self.assertIn("ndvi", indices)
        self.assertIn("ndwi", indices)
        self.assertEqual(indices["ndvi"].shape, (64, 64))

    def test_sar_preprocessing(self):
        # Linear amplitude synthetic SAR array
        amp = np.random.exponential(scale=50.0, size=(64, 64)).astype(np.float32) + 1e-4
        sigma_db = linear_to_db(amp)
        self.assertEqual(sigma_db.shape, (64, 64))
        self.assertTrue(np.all(np.isfinite(sigma_db)))

        filtered = apply_speckle_filter(np.clip(sigma_db + 30, 0, 255).astype(np.uint8), kernel_size=3)
        self.assertEqual(filtered.shape, (64, 64))

    def test_spatial_alignment(self):
        arr1 = np.zeros((100, 100, 3), dtype=np.uint8)
        arr2 = np.zeros((80, 80, 3), dtype=np.uint8)
        meta1 = {"crs": "EPSG:4326", "bounds": [10.0, 40.0, 11.0, 41.0]}
        meta2 = {"crs": "EPSG:4326", "bounds": [10.0, 40.0, 11.0, 41.0]}

        a1, a2, report = align_multimodal_rasters(arr1, arr2, meta1, meta2)
        self.assertTrue(report["is_aligned"])
        self.assertEqual(a2.shape[:2], (100, 100))
        self.assertAlmostEqual(report["spatial_overlap_pct"], 100.0)

        overlap = compute_spatial_overlap([0.0, 0.0, 1.0, 1.0], [0.0, 0.0, 1.0, 1.0])
        self.assertAlmostEqual(overlap, 1.0)

    def test_tool_registry(self):
        tools = GLOBAL_TOOL_REGISTRY.list_tools()
        self.assertGreaterEqual(len(tools), 10)
        for t in tools:
            self.assertIsNotNone(t.name)
            self.assertIsNotNone(t.description)
            self.assertTrue(len(t.accepted_modalities) > 0)

    def test_agent_plan_single_optical(self):
        plan = self.agent.plan(
            "Is there an airport runway visible in this scene?",
            image1_id={"modality": "optical"}
        )
        self.assertEqual(plan.intent, "VQA")
        self.assertIn("geochat", plan.selected_tools)
        
        # Verify skipped tools and explicit rationales
        skipped_names = [s["tool"] for s in plan.skipped_tools]
        self.assertIn("sar_analysis", skipped_names)
        self.assertIn("change_detection", skipped_names)
        for s in plan.skipped_tools:
            self.assertTrue(len(s["reason"]) > 5)

    def test_agent_plan_grounding(self):
        plan = self.agent.plan(
            "Highlight the lake",
            image1_id={"modality": "optical"}
        )
        self.assertEqual(plan.intent, "GROUNDING")
        self.assertIn("geoground", plan.selected_tools)

    def test_agent_plan_bitemporal(self):
        plan = self.agent.plan(
            "What changes occurred between 2022 and 2025?",
            image1_id={"modality": "optical"},
            image2_id={"modality": "optical"},
            requested_mode="bi_temporal"
        )
        self.assertEqual(plan.intent, "CHANGE_DETECTION")
        self.assertIn("change_detection", plan.selected_tools)
        self.assertIn("change_captioning", plan.selected_tools)

    def test_agent_plan_optical_sar(self):
        plan = self.agent.plan(
            "Analyze structures using optical and SAR",
            image1_id={"modality": "optical"},
            image2_id={"modality": "sar"},
            requested_mode="optical_sar"
        )
        self.assertEqual(plan.intent, "OPTICAL_SAR_FUSION")
        self.assertIn("optical_analysis", plan.selected_tools)
        self.assertIn("sar_analysis", plan.selected_tools)
        self.assertIn("multimodal_fusion", plan.selected_tools)
        self.assertIn("clay", plan.selected_tools)

    def test_execution_demo1_optical_vqa(self):
        res = self.agent.execute_workflow(
            "Describe the land cover and major objects visible in this image.",
            "sample_demo1_optical_landcover_tif"
        )
        self.assertEqual(res["detected_task"], "SCENE_DESCRIPTION")
        self.assertTrue(len(res["answer"]) > 10)
        self.assertTrue(len(res["execution_trace"]) >= 4)
        self.assertIsNotNone(res["agent_plan"])
        self.assertTrue(len(res["agent_plan"]["skipped_tools"]) > 0)

    def test_execution_demo2_grounding(self):
        res = self.agent.execute_workflow(
            "Highlight the water body.",
            "sample_demo2_grounding_water_tif"
        )
        self.assertEqual(res["detected_task"], "GROUNDING")
        self.assertIn("geoground", res["selected_models"])
        self.assertTrue(len(res["evidence"]["bboxes"]) > 0)

    def test_execution_demo3_bitemporal(self):
        res = self.agent.execute_workflow(
            "What changed between these two dates?",
            "sample_demo3_bitemporal_2022_05_10_tif",
            "sample_demo3_bitemporal_2025_06_15_tif",
            requested_mode="bi_temporal"
        )
        self.assertEqual(res["detected_task"], "CHANGE_DETECTION")
        self.assertIn("change_detection", res["selected_models"])
        self.assertIsNotNone(res["evidence"]["change_percentage"])
        self.assertIsNotNone(res["evidence"]["change_map_url"])

    def test_execution_demo4_optical_sar_fusion(self):
        res = self.agent.execute_workflow(
            "Use the optical and SAR images together to identify built-up and water-covered regions.",
            "sample_demo5_optical_sentinel2_tif",
            "sample_demo5_sar_sentinel1_tif",
            requested_mode="optical_sar"
        )
        self.assertEqual(res["detected_task"], "OPTICAL_SAR_FUSION")
        self.assertIn("multimodal_fusion", res["selected_models"])
        self.assertIsNotNone(res["multimodal_evidence"])
        self.assertIn("optical", res["multimodal_evidence"])
        self.assertIn("sar", res["multimodal_evidence"])
        self.assertIn("cross_modal_agreement", res["multimodal_evidence"])

    def test_api_agent_plan_endpoint(self):
        req = PlanRequest(
            query="Detect changes between images",
            image1_id="sample_demo3_bitemporal_2022_05_10_tif",
            image2_id="sample_demo3_bitemporal_2025_06_15_tif",
            mode="bi_temporal"
        )
        data = generate_agent_plan(req)
        self.assertEqual(data["intent"], "CHANGE_DETECTION")
        self.assertTrue(len(data["selected_tools"]) > 0)
        self.assertTrue(len(data["skipped_tools"]) > 0)

    def test_api_models_endpoint(self):
        models = list_models()
        self.assertGreaterEqual(len(models), 6)

if __name__ == "__main__":
    unittest.main()
