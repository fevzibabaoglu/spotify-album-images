import numpy as np
import os
import re
import requests
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from skimage import io
from skimage.color import rgb2lab
from skimage.transform import resize
from typing import List, Callable, Generator, Union


# Suppress low contrast warnings
warnings.filterwarnings("ignore", message=".*is a low contrast image.*")


class ImageHandler:
    def __init__(self, output_dir: str, max_workers: int = 1):
        """General-purpose image handler for downloading, saving, and processing images."""
        self.output_dir = output_dir
        self.max_workers = max_workers # Number of threads for parallel processing

    @staticmethod
    def download_image(url: str) -> np.ndarray:
        """Download an image from a URL and return it as a NumPy array."""
        try:
            # Download the image data
            response = requests.get(url)
            response.raise_for_status()

            # Read the image into a NumPy array
            image = io.imread(BytesIO(response.content))

            # Ensure the image is in RGB format
            if image.ndim == 2:  # Grayscale image (2D array)
                image = np.stack([image] * 3, axis=-1)
            elif image.ndim == 3 and image.shape[-1] == 1:  # Single-channel image
                image = np.concatenate([image] * 3, axis=-1)
            elif image.ndim == 3 and image.shape[-1] == 4:  # RGBA image
                image = image[..., :3]
            elif image.ndim != 3 or image.shape[-1] != 3:  # Unexpected format
                raise ValueError(f"Unsupported image format with shape: {image.shape}")

            return image
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to download image from {url}: {e}")

    @staticmethod
    def save_image(image: np.ndarray, save_path: str):
        """Save an RGB NumPy array image to a file."""
        # Rescale to uint8 format for saving
        if image.dtype != np.uint8:
            image = (image * 255).astype(np.uint8)
        io.imsave(save_path, image)

    @staticmethod
    def rgb_to_lab(image: np.ndarray) -> np.ndarray:
        """Convert an RGB image to LAB color space."""
        # Normalize image to [0, 1] if it's not already
        if image.dtype != np.float32 and image.dtype != np.float64:
            image = image / 255.0
        return rgb2lab(image)
    
    @staticmethod
    def downscale(image: np.ndarray, output_shape=(32, 32)) -> np.ndarray:
        """Downscale an image to a target shape."""
        return resize(
            image,
            output_shape,
            anti_aliasing=True,
            preserve_range=True,  # Preserve LAB value range
        )

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Replace invalid characters."""
        filename = re.sub(r'"', "'", filename)
        filename = re.sub(r'[<>:/\\|?*]', '_', filename)
        return filename

    def create_folder(self, folder_name: str) -> str:
        """Create a folder in the output directory."""
        path = os.path.join(self.output_dir, folder_name)
        os.makedirs(path, exist_ok=True)
        return path

    def process_images(
        self,
        items: Union[List, Generator],
        process_func: Callable[[np.ndarray, int], np.ndarray],
        save_func: Callable[[np.ndarray, int], None] = None,
    ) -> List[np.ndarray]:
        """
        General-purpose method to process items in parallel.
        :param items: List of items or a generator to process.
        :param process_func: Function to process an item.
        :param save_func: Optional function to save an item.
        :return: List of processed items.
        """
        results = []
        futures = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for idx, item in enumerate(items):
                futures.append(executor.submit(process_func, item, idx))

            for future in as_completed(futures):
                result, save_data = future.result()
                if save_func and save_data:
                    save_func(*save_data)
                results.append(result)
        return results
