import unittest
import numpy as np
from PIL import Image
from pathlib import Path

from backend.app.services.input_validator import compute_spatial_overlap, validate_image_pair
from backend.app.services.agent_controller import AgentController
from backend.app.services.fusion import run_optical_sar_fusion
from backend.app.services.confidence import compute_aggregated_confidence
from backend.app.services.sample_generator import generate_samples_if_needed, get_sample_scenarios

class TestSatQueryAI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.samples = generate_samples_if_needed()
        cls.controller = AgentController()

    def test_spatial_overlap_calculation(self):
        # Exact match
        bounds1 = [12.0, 40.0, 13.0, 41.0]
        bounds2 = [12.0, 40.0, 13.0, 41.0]
        overlap = compute_spatial_overlap(bounds1, bounds2)
        self.assertAlmostEqual(overlap, 1.0, places=2)

        # Disjoint bounding boxes
        bounds3 = [20.0, 50.0, 21.0, 51.0]
        overlap_zero = compute_spatial_overlap(bounds1, bounds3)
        self.assertEqual(overlap_zero, 0.0)

    def test_pair_validation_rejection(self):
        meta1 = {
            "dimensions": [512, 512],
            "bounds": [10.0, 40.0, 11.0, 41.0],
            "crs": "EPSG:4326",
            "modality": "optical"
        }
        meta2 = {
            "dimensions": [512, 512],
            "bounds": [90.0, 20.0, 91.0, 21.0],
            "crs": "EPSG:4326",
            "modality": "optical"
        }
        val = validate_image_pair(meta1, meta2)
        self.assertFalse(val["valid"])
        self.assertIn("Insufficient geographic overlap", val["reason"])

    def test_query_intent_routing(self):
        # Single image intents
        self.assertEqual(self.controller._classify_query_intent("Describe the terrain", "single"), "captioning")
        self.assertEqual(self.controller._classify_query_intent("Highlight the river", "single"), "grounding")
        self.assertEqual(self.controller._classify_query_intent("What type of land cover is visible?", "single"), "vqa")
        # Bi-temporal intents
        self.assertEqual(self.controller._classify_query_intent("What changed between these dates?", "bi_temporal"), "change_detection")
        self.assertEqual(self.controller._classify_query_intent("Has the built-up area increased?", "bi_temporal"), "change_vqa")
        # Optical + SAR intent
        self.assertEqual(self.controller._classify_query_intent("Identify structures with radar", "optical_sar"), "optical_sar")

    def test_optical_sar_fusion_pipeline(self):
        opt = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
        sar = np.random.randint(0, 255, (256, 256), dtype=np.uint8)
        res = run_optical_sar_fusion(opt, sar)
        self.assertIn("class_probabilities", res)
        self.assertIn("sar_structural_density", res)
        self.assertIn("dominant_class", res)

    def test_confidence_calibration(self):
        conf = compute_aggregated_confidence(
            model_conf=0.92,
            input_compatibility=1.00,
            evidence_strength=0.90,
            answer_consistency=0.94,
            has_mask_or_bbox=True
        )
        self.assertGreaterEqual(conf["final_confidence"], 0.88)
        self.assertEqual(conf["confidence_level"], "High confidence")

    def test_demo_scenarios_registered(self):
        scenarios = get_sample_scenarios()
        self.assertEqual(len(scenarios), 5)
        for s in scenarios:
            self.assertIn("title", s)
            self.assertIn("image1_id", s)
            self.assertIn("query", s)

    def test_end_to_end_demo1_workflow(self):
        scenarios = get_sample_scenarios()
        demo1 = scenarios[0]
        res = self.controller.execute_workflow(
            query=demo1["query"],
            image1_id=demo1["image1_id"]
        )
        self.assertIn("job_id", res)
        self.assertTrue(len(res["answer"]) > 10)
        self.assertIsNotNone(res["evidence"]["overlay_url"])
        self.assertGreater(res["confidence"]["final_confidence"], 0.80)
        self.assertTrue(len(res["execution_trace"]) >= 5)

if __name__ == "__main__":
    unittest.main()
