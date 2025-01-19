import numpy as np
from collections import Counter
from PIL import Image
from skimage.color import lab2rgb
from sklearn.cluster import KMeans
from typing import List, Literal, Optional, Tuple


class Clustering:
    def __init__(
        self, 
        n_clusters: int, 
        init: Literal['k-means++', 'random'] = "k-means++",
        max_iter: int = 300,
        tol: float = 0.0001,
        random_state: Optional[int] = None,
        algorithm: Literal['lloyd', 'elkan', 'auto', 'full'] = "lloyd",
    ):
        """Initialize the clustering object with K-means configuration."""
        self.kmeans = KMeans(
            n_clusters=n_clusters,
            init=init,
            max_iter=max_iter,
            tol=tol,
            random_state=random_state,
            algorithm=algorithm,
        )

    def preprocess_images(self, images: List[np.ndarray]) -> np.ndarray:
        """Preprocess the LAB images for clustering.
        Flattens the images and combines all pixels into a single dataset."""
        flattened_pixels = [image.reshape(-1, 3) for image in images]
        return np.vstack(flattened_pixels)

    def fit(self, images: List[np.ndarray]):
        """Fit the K-medoids model on the LAB images."""
        # Preprocess the images to get a flat array of LAB pixels
        data = self.preprocess_images(images)
        # Fit the K-medoids model
        self.kmeans.fit(data)

    def get_cluster_centers(self) -> np.ndarray:
        """Get the cluster centers in LAB color space."""
        if not hasattr(self.kmeans, 'cluster_centers_'):
            raise ValueError("The model has not been fitted yet. Call 'fit' first.")
        return self.kmeans.cluster_centers_
    
    def get_cluster_centers_by_proportions(self) -> List[Tuple[List[int], float]]:
        """Get cluster centers in RGB color space sorted by their proportions."""
        # Compute the proportion for each cluster
        labels = self.kmeans.labels_
        color_counts = Counter(labels)
        total_pixels = len(labels)
        color_proportions = [count / total_pixels for count in color_counts.values()]

        # Convert LAB cluster centers to RGB
        cluster_centers = self.get_cluster_centers()
        cluster_centers_rgb = lab2rgb(cluster_centers[np.newaxis, :, :])[0]
        cluster_centers_rgb = (cluster_centers_rgb * 255).astype(np.uint8).tolist()

        # Sort clusters by their proportions in descending order
        sorted_clusters = sorted(
            zip(cluster_centers_rgb, color_proportions), 
            key=lambda x: x[1], 
            reverse=True,
        )
        return sorted_clusters
    
    def get_cluster_image(self, output_shape=(100, 100)):
        """Create an image representing the cluster centers."""
        height, width = output_shape

        # Create an empty array for the image
        image_array = np.zeros((height, width, 3), dtype=np.uint8)

        # Get the cluster centers and their proportions
        data = self.get_cluster_centers_by_proportions()

        # Calculate cumulative proportions to ensure exact coverage
        cumulative_proportions = np.cumsum([proportion for _, proportion in data])
        cumulative_pixels = (cumulative_proportions * width).round().astype(int)

        # Fill the image with vertical bars based on the percentages
        start_x = 0
        for i, (color, _) in enumerate(data):
            end_x = cumulative_pixels[i]
            image_array[:, start_x:end_x, :] = color
            start_x = end_x

        # Create the PIL image from the array
        return Image.fromarray(image_array, mode="RGB")
