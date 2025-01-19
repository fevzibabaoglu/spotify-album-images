# Spotify Playlist Album Color Clustering

This project analyzes the **most significant colors** in the album covers of a Spotify playlist. By clustering album images based on their dominant colors, it provides insights into color patterns that might reflect aspects of the user's preferences, mental health, or creative ideas.

### Objectives
- **Primary Goal**: Identify and visualize the dominant colors in album covers from a given Spotify playlist.
- **Experimental Insights**: Explore the psychological or emotional associations of colors in relation to the playlist's theme or mood.
- **Fun Application**: Gain a new perspective on your music choices!

---

### Features
1. **Spotify Playlist Integration**:
   - Fetch album covers using the Spotify Web API.
2. **Image Processing**:
   - Convert album images to LAB color space (better suited for human perception).
   - Downscale images for efficient processing.
3. **Clustering**:
   - Uses K-Means to group similar colors and identify cluster centers.
   - Each cluster center represents a dominant color in the playlist.
   - **Warning:** The K-Means algorithm can yield slightly different results on each run due to its randomness in initialization.
4. **Visualization**:
   - Creates a visual representation of the most prominent colors as vertical bars, sized proportionally by their significance.

---

### Clustering Algorithm
- **K-Means**:
  - Chosen for its efficiency and simplicity in color clustering.
  - Provides cluster centers based on the average LAB values of each group.
- **Why not K-Medoids?**:
  - **K-Medoids** offers more accurate cluster centers (actual data points), but its memory-intensive computations (lack of mini-batch support) made it infeasible for large datasets with the available resources.
  - **Suggested Improvement:** Implement a mini-batch version of K-Medoids for more precise clustering without memory limitations.

---

### Requirements
- Python 3.9+
- Libraries: `numpy`, `Pillow`, `skimage`, `scikit-learn`, `requests`, `dotenv`
  - Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
- Spotify API Credentials:
  - Obtain `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` from the [Spotify Developer Dashboard](https://developer.spotify.com/).
  - Set these as environment variables before running the script.

---

### Usage

#### Run the Script
```bash
python ./src/main.py [-h] [--max_workers MAX_WORKERS] [--save_images] playlist_id
```

#### Arguments
1. `playlist_id` (required): Spotify playlist ID to analyze.
2. `--max_workers` (optional, default: `10`): Number of threads for parallel processing.
3. `--save_images` (optional, default: `False`): Save images locally.

#### Example
```bash
python ./src/main.py 0CHBhK7tdXqtB03S26d43z --max_workers 5 --save_images
```

---

### Outputs
1. **Clustered Colors Visualization**:
   - A generated image displaying the most significant colors in the playlist's album covers.
2. **Optional Saved Images**:
   - Both the album images and the generated color cluster image (if `--save_images` is enabled).

---

### Future Improvements
1. **K-Medoids Integration**:
   - Replace K-Means with a memory-efficient K-Medoids implementation for precise clustering.
2. **Enhanced Visualization**:
   - Add interactive or dynamic visualizations for better user insights.
3. **Deeper Analysis**:
   - Investigate emotional or psychological correlations between color patterns and playlist genres.

---

Feel free to experiment with your favorite playlists and explore the colorful world of your music preferences!
