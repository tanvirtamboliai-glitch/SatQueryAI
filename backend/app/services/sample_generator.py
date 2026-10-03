import os
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
from PIL import Image, ImageDraw
import cv2

from ..database.db import save_image_record, get_image_record
from ..services.input_validator import inspect_image

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "samples"
RESULTS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "results"
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

try:
    import tifffile
    HAS_TIFF = True
except ImportError:
    HAS_TIFF = False

def create_synthetic_geotiff(filename: str, rgb_arr: np.ndarray, extra_band: Optional[np.ndarray] = None) -> Path:
    """Save 3-4 band image as GeoTIFF format with spatial metadata."""
    out_path = SAMPLES_DIR / filename
    
    if extra_band is not None:
        # 4-band (RGB + NIR)
        combined = np.dstack([rgb_arr, extra_band])
    else:
        combined = rgb_arr

    if HAS_TIFF:
        tifffile.imwrite(
            str(out_path),
            combined,
            photometric='rgb' if combined.shape[2] == 3 else 'minisblack',
            description="SatQuery AI Multimodal Remote Sensing Standard Sample GeoTIFF (EPSG:4326)"
        )
    else:
        Image.fromarray(rgb_arr).save(out_path, format="TIFF")

    return out_path

def generate_samples_if_needed():
    """Generates and registers the 5 standardized benchmark demo samples."""
    np.random.seed(42)
    size = (512, 512)

    # -------------------------------------------------------------
    # DEMO 1: Single Optical Land Cover Scene
    # -------------------------------------------------------------
    fn1 = "demo1_optical_landcover.tif"
    p1 = SAMPLES_DIR / fn1
    if not p1.exists():
        img1 = np.zeros((size[1], size[0], 3), dtype=np.uint8)
        # Background: agricultural green/yellow fields
        img1[:, :] = [76, 120, 56]
        # Draw field parcels
        for x in range(0, 512, 128):
            for y in range(0, 512, 128):
                c = np.random.randint(-20, 20, 3)
                col = np.clip([85 + c[0], 135 + c[1], 50 + c[2]], 0, 255).astype(np.uint8)
                img1[y:y+124, x:x+124] = col
        # Draw urban cluster
        img1[180:330, 180:330] = [170, 175, 180]
        for bx in range(190, 320, 35):
            for by in range(190, 320, 35):
                img1[by:by+22, bx:bx+22] = [210, 215, 220]  # rooftops
        # Draw asphalt road corridor
        cv2.line(img1, (0, 256), (512, 256), (60, 62, 65), 10)
        cv2.line(img1, (256, 0), (256, 512), (60, 62, 65), 8)
        create_synthetic_geotiff(fn1, img1)

    # -------------------------------------------------------------
    # DEMO 2: Water Body Grounding Scene
    # -------------------------------------------------------------
    fn2 = "demo2_grounding_water.tif"
    p2 = SAMPLES_DIR / fn2
    if not p2.exists():
        img2 = np.zeros((size[1], size[0], 3), dtype=np.uint8)
        # Background: dry terrain / shrubland
        img2[:, :] = [160, 140, 105]
        # Add texture noise
        noise = np.random.randint(-15, 15, (512, 512, 3))
        img2 = np.clip(img2.astype(int) + noise, 0, 255).astype(np.uint8)
        # Draw large prominent reservoir / lake
        cv2.ellipse(img2, (260, 240), (160, 100), 25, 0, 360, (25, 85, 160), -1)
        # Winding river tributary
        pts = np.array([[0, 200], [100, 220], [180, 230], [240, 240]], np.int32)
        cv2.polylines(img2, [pts], False, (30, 95, 175), 18)
        create_synthetic_geotiff(fn2, img2)

    # -------------------------------------------------------------
    # DEMO 3 & 4: Bi-temporal Pair (T1: 2022-05-10, T2: 2025-06-15)
    # -------------------------------------------------------------
    fn3_t1 = "demo3_bitemporal_2022_05_10.tif"
    fn3_t2 = "demo3_bitemporal_2025_06_15.tif"
    p3_t1 = SAMPLES_DIR / fn3_t1
    p3_t2 = SAMPLES_DIR / fn3_t2

    if not p3_t1.exists() or not p3_t2.exists():
        # Base scene T1: Vegetated open land with small town
        base_t1 = np.zeros((size[1], size[0], 3), dtype=np.uint8)
        base_t1[:, :] = [90, 138, 70]
        # River in south
        cv2.line(base_t1, (0, 440), (512, 440), (35, 95, 170), 22)
        # Small town in south-west
        base_t1[280:380, 50:180] = [165, 170, 175]

        # T2: North-East sector replaced by massive commercial logistics center
        base_t2 = base_t1.copy()
        # Construction zone & new large buildings in north-east (x: 280..480, y: 50..260)
        base_t2[50:260, 280:480] = [210, 212, 215]  # New concrete paving
        # 4 large warehouse footprints
        cv2.rectangle(base_t2, (300, 70), (380, 140), (80, 85, 95), -1)
        cv2.rectangle(base_t2, (395, 70), (465, 140), (80, 85, 95), -1)
        cv2.rectangle(base_t2, (300, 160), (380, 230), (80, 85, 95), -1)
        cv2.rectangle(base_t2, (395, 160), (465, 230), (80, 85, 95), -1)
        # New arterial connector road
        cv2.line(base_t2, (180, 320), (280, 160), (55, 58, 62), 12)

        create_synthetic_geotiff(fn3_t1, base_t1)
        create_synthetic_geotiff(fn3_t2, base_t2)

    # -------------------------------------------------------------
    # DEMO 5: Co-registered Optical + SAR Pair
    # -------------------------------------------------------------
    fn5_opt = "demo5_optical_sentinel2.tif"
    fn5_sar = "demo5_sar_sentinel1.tif"
    p5_opt = SAMPLES_DIR / fn5_opt
    p5_sar = SAMPLES_DIR / fn5_sar

    if not p5_opt.exists() or not p5_sar.exists():
        # Optical scene: coastal city with cloud shadow covering western sector
        opt_scene = np.zeros((size[1], size[0], 3), dtype=np.uint8)
        opt_scene[:, :] = [100, 140, 80]  # Vegetation
        # Water bay in east
        opt_scene[:, 360:] = [28, 80, 150]
        # City structures
        opt_scene[160:340, 100:320] = [175, 180, 185]
        for bx in range(120, 300, 40):
            for by in range(180, 320, 40):
                opt_scene[by:by+25, bx:bx+25] = [230, 235, 240]
        # Semi-transparent cloud shadow in west
        shadow_mask = np.zeros((512, 512), dtype=np.uint8)
        cv2.circle(shadow_mask, (160, 240), 120, 255, -1)
        opt_scene[shadow_mask > 0] = (opt_scene[shadow_mask > 0] * 0.45).astype(np.uint8)

        # SAR scene (Microwave backscatter: clouds invisible, double-bounce on buildings)
        sar_scene = np.zeros((size[1], size[0]), dtype=np.uint8)
        # Water: specular reflection away from sensor -> very dark (0..20)
        sar_scene[:, 360:] = np.random.randint(5, 20, (512, 512 - 360))
        # Vegetation: diffuse volume scattering -> medium gray (50..80)
        sar_scene[:, :360] = np.random.randint(45, 75, (512, 360))
        # Buildings: metallic/corner reflector double bounce -> extremely bright (210..255)
        for bx in range(120, 300, 40):
            for by in range(180, 320, 40):
                sar_scene[by:by+25, bx:bx+25] = np.random.randint(220, 255, (25, 25))
        # Radar speckle noise
        speckle = np.random.normal(1.0, 0.18, (512, 512))
        sar_scene = np.clip(sar_scene.astype(float) * speckle, 0, 255).astype(np.uint8)

        create_synthetic_geotiff(fn5_opt, opt_scene)
        # Save SAR as 1-band GeoTIFF
        if HAS_TIFF:
            tifffile.imwrite(str(p5_sar), sar_scene, photometric='minisblack')
        else:
            Image.fromarray(sar_scene).save(p5_sar, format="TIFF")

    # Register each file in database
    registered_ids = {}
    for sample_fn, s_modality, s_sensor, s_date in [
        (fn1, "optical", "Sentinel-2 MSI", "2024-08-12"),
        (fn2, "optical", "Landsat-8 OLI", "2024-07-20"),
        (fn3_t1, "optical", "Sentinel-2 MSI", "2022-05-10"),
        (fn3_t2, "optical", "Sentinel-2 MSI", "2025-06-15"),
        (fn5_opt, "optical", "Sentinel-2 MSI", "2024-09-02"),
        (fn5_sar, "sar", "Sentinel-1 C-SAR (VV/VH)", "2024-09-02"),
    ]:
        fpath = SAMPLES_DIR / sample_fn
        fid = f"sample_{sample_fn.replace('.', '_')}"
        meta = inspect_image(str(fpath), fid)
        meta["file_path"] = str(fpath)
        meta["modality"] = s_modality
        meta["sensor"] = s_sensor
        meta["acquisition_date"] = s_date
        
        # Save preview in results
        prev_fn = f"preview_{fid}.png"
        prev_p = RESULTS_DIR / prev_fn
        if not prev_p.exists():
            with Image.open(fpath) as im:
                im.convert("RGB").save(prev_p, format="PNG")
        meta["preview_path"] = str(prev_p)
        meta["preview_url"] = f"/results/{prev_fn}"
        save_image_record(meta)
        registered_ids[sample_fn] = fid

    return registered_ids

def get_sample_scenarios() -> List[Dict[str, Any]]:
    """Returns curated demo scenarios matching the 5 mandatory hackathon workflows."""
    reg = generate_samples_if_needed()
    return [
        {
            "id": "demo-1",
            "title": "Demo 1: Single-Image Scene Understanding & VQA",
            "description": "Dense land use classification and spatial structure interpretation with GeoChat-7B.",
            "mode": "single",
            "image1_id": reg["demo1_optical_landcover.tif"],
            "image2_id": None,
            "preview1": f"/results/preview_{reg['demo1_optical_landcover.tif']}.png",
            "preview2": None,
            "query": "Describe the land cover and major objects visible in this image.",
            "expected_task": "VQA / Captioning",
            "expected_models": ["GeoChat"]
        },
        {
            "id": "demo-2",
            "title": "Demo 2: Text-Guided Geospatial Grounding",
            "description": "Zero-shot referring expression localization of water bodies into bounding coordinates and masks.",
            "mode": "single",
            "image1_id": reg["demo2_grounding_water.tif"],
            "image2_id": None,
            "preview1": f"/results/preview_{reg['demo2_grounding_water.tif']}.png",
            "preview2": None,
            "query": "Highlight the water body.",
            "expected_task": "Grounding",
            "expected_models": ["GeoGround", "GeoChat"]
        },
        {
            "id": "demo-3",
            "title": "Demo 3: Bi-Temporal Change Detection & Mapping",
            "description": "Siamese CVA change probability, Otsu segmentation, and change description across epochs.",
            "mode": "bi_temporal",
            "image1_id": reg["demo3_bitemporal_2022_05_10.tif"],
            "image2_id": reg["demo3_bitemporal_2025_06_15.tif"],
            "preview1": f"/results/preview_{reg['demo3_bitemporal_2022_05_10.tif']}.png",
            "preview2": f"/results/preview_{reg['demo3_bitemporal_2025_06_15.tif']}.png",
            "query": "What changed between these two dates?",
            "expected_task": "Change Detection",
            "expected_models": ["Change-Agent"]
        },
        {
            "id": "demo-4",
            "title": "Demo 4: Change-Based VQA & Built-up Expansion",
            "description": "Temporal reasoning measuring urban expansion and structural footprint increase.",
            "mode": "bi_temporal",
            "image1_id": reg["demo3_bitemporal_2022_05_10.tif"],
            "image2_id": reg["demo3_bitemporal_2025_06_15.tif"],
            "preview1": f"/results/preview_{reg['demo3_bitemporal_2022_05_10.tif']}.png",
            "preview2": f"/results/preview_{reg['demo3_bitemporal_2025_06_15.tif']}.png",
            "query": "Has the built-up area increased?",
            "expected_task": "Change VQA",
            "expected_models": ["Change-Agent", "ChangeChat"]
        },
        {
            "id": "demo-5",
            "title": "Demo 5: Optical + SAR Cross-Modal Feature Fusion",
            "description": "Joint latent feature fusion with Clay foundation model, penetrating optical shadows via SAR double-bounce.",
            "mode": "optical_sar",
            "image1_id": reg["demo5_optical_sentinel2.tif"],
            "image2_id": reg["demo5_sar_sentinel1.tif"],
            "preview1": f"/results/preview_{reg['demo5_optical_sentinel2.tif']}.png",
            "preview2": f"/results/preview_{reg['demo5_sar_sentinel1.tif']}.png",
            "query": "Use the optical and SAR images together to identify built-up and water-covered regions.",
            "expected_task": "Optical + SAR Fusion",
            "expected_models": ["Clay", "Prithvi-EO-2.0"]
        }
    ]
