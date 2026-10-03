import random
import numpy as np
from PIL import Image, ImageEnhance
from typing import Tuple, List, Dict, Any

class RemoteSensingAugmentations:
    """
    Nadir and off-nadir spatial transforms suitable for satellite and aerial imagery.
    Unlike natural images, aerial scenes have 360-degree rotational symmetry.
    """
    def __init__(self, p_flip: float = 0.5, p_rot90: float = 0.5):
        self.p_flip = p_flip
        self.p_rot90 = p_rot90

    def __call__(self, image: Image.Image, mask: np.ndarray = None) -> Tuple[Image.Image, np.ndarray]:
        # 1. Random Orthogonal Rotation (0, 90, 180, 270 degrees)
        if random.random() < self.p_rot90:
            k = random.choice([1, 2, 3])
            image = image.rotate(k * 90)
            if mask is not None:
                mask = np.rot90(mask, k)

        # 2. Random Horizontal Flip
        if random.random() < self.p_flip:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)
            if mask is not None:
                mask = np.fliplr(mask)

        # 3. Random Vertical Flip
        if random.random() < self.p_flip:
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            if mask is not None:
                mask = np.flipud(mask)

        # 4. Radiometric Jitter (Simulate seasonal/atmospheric solar variation)
        if random.random() < 0.3:
            factor = random.uniform(0.85, 1.15)
            image = ImageEnhance.Brightness(image).enhance(factor)
            image = ImageEnhance.Contrast(image).enhance(factor)

        return image, mask
