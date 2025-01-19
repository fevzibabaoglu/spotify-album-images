import argparse
import os

from api import SpotifyAPI, Playlist
from image_ops import ImageHandler, TrackImage, Clustering


def main(playlist_id, max_workers):
    # Setup output directory
    output_dir = os.path.join(os.getcwd(), 'output')

    # Initialize Spotify API and authenticate
    spotifyAPI = SpotifyAPI()
    spotifyAPI.authenticate()

    # Initialize ImageHandler and TrackImage
    image_handler = ImageHandler(output_dir=output_dir, max_workers=max_workers)
    track_image = TrackImage(image_handler=image_handler)

    # Get playlist data
    playlist = Playlist(spotifyAPI, playlist_id)

    # Download and process the images
    images = track_image.handle_images(playlist, output_shape=(256, 256))

    # Initialize and apply clustering
    n_clusters = 5  # Adjust as needed
    clustering = Clustering(
        n_clusters=n_clusters,
        init='k-means++',
        max_iter=300,
        tol=0,
        random_state=None,
        algorithm='lloyd',
    )
    clustering.fit(images)

    # Get cluster image in RGB space
    cluster_image = clustering.get_cluster_image(output_shape=(640, 640))

    # Save cluster image in RGB space
    if track_image.save_album_images:
        playlist_folder = image_handler.create_folder(playlist.playlist_id)
        filename = image_handler.sanitize_filename('clustered_image.jpg')
        save_path = os.path.join(playlist_folder, filename)
        cluster_image.save(save_path)
        
    # Show cluster image in RGB space
    cluster_image.show()


if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Cluster album images from a Spotify playlist.")
    parser.add_argument('playlist_id', type=str, help="The ID of the Spotify playlist.")
    parser.add_argument('--max_workers', type=int, default=10, help="The number of workers for parallel processing.")
    args = parser.parse_args()

    # Run main with parsed arguments
    main(playlist_id=args.playlist_id, max_workers=args.max_workers)
