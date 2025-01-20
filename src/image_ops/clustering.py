import numpy as np
from collections import Counter
from PIL import Image
from skimage.color import lab2rgb
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.utils import shuffle
from typing import List, Literal, Optional, Tuple


class Clustering:
    def __init__(
        self, 
        n_clusters: int, 
        init: Literal['k-means++', 'random'] = "k-means++",
        max_iter: int = 300,
        tol: float = 0.0001,
        random_state: Optional[int] = None,
        algorithm: Literal['lloyd', 'elkan'] = "lloyd",
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

    @staticmethod
    def preprocess_images(images: List[np.ndarray]) -> np.ndarray:
        """Preprocess the LAB images for clustering.
        Flattens the images and combines all pixels into a single dataset."""
        flattened_pixels = [image.reshape(-1, 3) for image in images]
        return np.vstack(flattened_pixels)

    def fit(self, data: np.ndarray):
        """Fit the K-medoids model on the LAB image dataset."""
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

    @classmethod
    def get_optimal_kmeans(
        cls,
        images: List[np.ndarray], 
        n_clusters_range: Tuple[int, int] = (2, 10), 
        init: Literal['k-means++', 'random'] = "k-means++",
        max_iter: int = 300,
        tol: float = 0.0001,
        random_state: Optional[int] = None,
        algorithm: Literal['lloyd', 'elkan'] = "lloyd",
        n_subsamples: int = 5,
        subset_size: int = 10000,
        alpha: float = 0.5,
    ) -> int:
        """
        Determine the optimal number of clusters using a custom metric balancing silhouette 
        score and cluster count, averaged over subsamples.

        Parameters
        ----------
        images : List[np.ndarray]
            List of LAB images to cluster.
        n_clusters_range : Tuple[int, int]
            Range of cluster numbers to test.
        n_subsamples : int, default=5
            Number of random subsamples to calculate silhouette scores for each cluster count.
        subset_size : int, default=10000
            Number of samples to use per subsample.

        Returns
        -------
        Clustering
            A Clustering object initialized with the optimal number of clusters.
        """
        image_data = cls.preprocess_images(images)
        scores = []

        for n_clusters in range(n_clusters_range[0], n_clusters_range[1] + 1):
            subsample_scores = []
            
            for _ in range(n_subsamples):
                # Randomly select a subset of data
                subset_data = shuffle(image_data, random_state=random_state)[:subset_size]

                # Initialize and fit clustering
                clustering = cls(
                    n_clusters=n_clusters,
                    init=init,
                    max_iter=max_iter,
                    tol=tol,
                    random_state=random_state,
                    algorithm=algorithm,
                )
                clustering.fit(subset_data)

                # Compute silhouette score
                score = silhouette_score(subset_data, clustering.kmeans.labels_)
                subsample_scores.append(score)

            # Compute average silhouette score
            avg_score = np.mean(subsample_scores)
        
            # Compute custom metric
            log_scale = np.log(n_clusters) / np.log(n_clusters_range[1])
            custom_metric = avg_score * (1 + alpha * log_scale)

            scores.append((n_clusters, avg_score, custom_metric))
            print(f"For {n_clusters} clusters, avg silhouette score: {avg_score:.4f}, avg custom score: {custom_metric:.4f}")

        # Find the number of clusters with the highest custom metric
        optimal_clusters, best_score, best_metric = max(scores, key=lambda x: x[2])
        print(f"Optimal number of clusters: {optimal_clusters} with avg silhouette score: {best_score:.4f}, avg custom score: {best_metric:.4f}")

        return cls(
            n_clusters=optimal_clusters,
            init=init, 
            max_iter=max_iter, 
            tol=tol, 
            random_state=random_state, 
            algorithm=algorithm,
        )
