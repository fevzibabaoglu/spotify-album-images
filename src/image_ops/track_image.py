import os
import numpy as np
from typing import List

from .image_handler import ImageHandler


class TrackImage:
    def __init__(self, image_handler: ImageHandler, save_album_images: bool = True):
        """Handles track-specific logic for image downloading and processing."""
        self.image_handler = image_handler
        self.save_album_images = save_album_images

    def handle_image(self, playlist, track, track_index: int, output_shape=(32, 32), file_extension: str = "jpg") -> tuple:
        """Download, save, and process a single track image. Returns the 
        processed image in LAB color space."""
        # Download the image
        image = self.image_handler.download_image(track.album_image_url)

        save_data = None
        if self.save_album_images:
            playlist_folder = self.image_handler.create_folder(playlist.playlist_id)
            filename = f"{track_index + 1:03d}. {track.name} [by {', '.join(track.artist_names)}].{file_extension}"
            filename = self.image_handler.sanitize_filename(filename)
            save_path = os.path.join(playlist_folder, filename)
            save_data = (image, save_path)

        # Convert to LAB and downscale
        image_lab = self.image_handler.rgb_to_lab(image)
        image_downscaled = self.image_handler.downscale(image_lab, output_shape)
        return image_downscaled, save_data

    def handle_images(self, playlist, output_shape=(32, 32), file_extension: str = "jpg") -> List[np.ndarray]:
        """Download, save, and process all track images from the generator in order."""
        tracks_generator = playlist.get_tracks()

        def process_func(track, idx):
            return self.handle_image(playlist, track, idx, output_shape, file_extension)

        def save_func(image, save_path):
            self.image_handler.save_image(image, save_path)

        return self.image_handler.process_images(tracks_generator, process_func, save_func)
