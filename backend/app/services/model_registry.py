import os
from typing import Dict, Any, List, Optional
from ..schemas.schemas import ModelDescriptor

MODEL_MODE = os.getenv("MODEL_MODE", "calibrated_fallback")  # "local", "api", "calibrated_fallback"

MODEL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "vqa": {
        "model": "GeoChat",
        "version": "7B-v1.0",
        "role": "Single-image Remote Sensing Visual Question Answering & Scene Understanding",
        "input_types": ["single_image"],
        "outputs": ["text", "confidence"],
        "service_module": "app.models.geochat_service",
        "weights": "MBZUAI/geochat-7b",
        "mode": MODEL_MODE,
        "is_active": True,
        "description": "Groundbreaking multimodal vision-language model fine-tuned on high-resolution Earth observation data."
    },
    "captioning": {
        "model": "GeoChat",
        "version": "7B-v1.0",
        "role": "Dense Remote Sensing Scene Description and Spatial Captioning",
        "input_types": ["single_image"],
        "outputs": ["caption", "key_concepts"],
        "service_module": "app.models.geochat_service",
        "weights": "MBZUAI/geochat-7b",
        "mode": MODEL_MODE,
        "is_active": True,
        "description": "Generates structured captions summarizing land use, infrastructure, water bodies, and vegetation density."
    },
    "grounding": {
        "model": "GeoGround",
        "version": "v1.2",
        "role": "Text-Guided Geospatial Object and Region Localization",
        "input_types": ["single_image"],
        "outputs": ["bbox", "mask", "spatial_coordinates"],
        "service_module": "app.models.geoground_service",
        "weights": "weights/geoground_rs.pt",
        "mode": MODEL_MODE,
        "is_active": True,
        "description": "Localizes natural language referring expressions to bounding boxes and pixel-level segmentations in aerial imagery."
    },
    "change_detection": {
        "model": "Change-Agent",
        "version": "v2.0",
        "role": "Bi-temporal Remote Sensing Change Detection & Change Mask Extraction",
        "input_types": ["bi_temporal_pair"],
        "outputs": ["change_map", "change_mask", "changed_regions", "change_percentage"],
        "service_module": "app.models.change_service",
        "weights": "weights/change_agent_diff.pt",
        "mode": MODEL_MODE,
        "is_active": True,
        "description": "Specialist Siamese difference network computing change probability distributions, Otsu morphological change masks, and polygon statistics."
    },
    "change_vqa": {
        "model": "ChangeChat",
        "version": "v1.0",
        "role": "Bi-temporal Temporal Reasoning & Change-Based VQA",
        "input_types": ["bi_temporal_pair"],
        "outputs": ["text", "temporal_reasoning", "evidence"],
        "service_module": "app.models.change_vqa_service",
        "weights": "weights/changechat_adapter",
        "mode": MODEL_MODE,
        "is_active": True,
        "description": "Interprets temporal land cover dynamics, answering queries like 'Has built-up area increased?' or 'What changed between these dates?'"
    },
    "optical_sar": {
        "model": "Clay",
        "version": "v1.5",
        "role": "Cross-Modal Optical + SAR Joint Representation and Feature Fusion",
        "input_types": ["optical_sar_pair"],
        "outputs": ["joint_features", "fused_analysis", "structural_evidence"],
        "service_module": "app.models.clay_service",
        "weights": "made-with-clay/Clay",
        "mode": MODEL_MODE,
        "is_active": True,
        "description": "Multisensor Earth-observation transformer creating shared embedding spaces across optical reflectance and SAR backscatter."
    },
    "eo_features": {
        "model": "Prithvi-EO-2.0",
        "version": "300M",
        "role": "Multispectral Remote Sensing Foundation Backbone",
        "input_types": ["multispectral", "single_image"],
        "outputs": ["features", "embeddings"],
        "service_module": "app.models.prithvi_service",
        "weights": "ibm-nasa-geospatial/Prithvi-EO-2.0-300M",
        "mode": MODEL_MODE,
        "is_active": True,
        "description": "IBM & NASA geospatial foundation model pre-trained on Harmonized Landsat Sentinel-2 (HLS) multispectral imagery."
    },
    "retrieval": {
        "model": "RemoteCLIP",
        "version": "ViT-B-32",
        "role": "Remote Sensing Semantic Image-Text Alignment & Retrieval",
        "input_types": ["image", "text"],
        "outputs": ["similarity", "class_probabilities"],
        "service_module": "app.models.remoteclip_service",
        "weights": "chendelong/RemoteCLIP",
        "mode": MODEL_MODE,
        "is_active": True,
        "description": "Domain-adapted contrastive vision-language representation for aerial scene classification and zero-shot retrieval."
    }
}

def get_model_registry() -> Dict[str, Dict[str, Any]]:
    return MODEL_REGISTRY

def get_active_models_summary() -> List[ModelDescriptor]:
    descriptors = []
    for task_name, info in MODEL_REGISTRY.items():
        descriptors.append(ModelDescriptor(
            id=task_name,
            name=info["model"],
            role=info["role"],
            mode=info["mode"],
            input_types=info["input_types"],
            outputs=info["outputs"],
            description=info["description"],
            weights_path=info.get("weights"),
            is_active=info["is_active"]
        ))
    return descriptors
