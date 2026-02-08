# Quick Start

This guide will help you start using **Remote Sensing Satellite Downloader** in minutes.

---

## Installation

```bash
pip install sat_download
```

Or from source code:

```bash
git clone https://github.com/Aouei/remote-sensing-satellite-downloader.git
cd remote-sensing-satellite-downloader
pip install -e .
```

---

## Prerequisites

### For Sentinel (Copernicus)

1. Create account at [Copernicus Data Space](https://dataspace.copernicus.eu/)
2. Note your email and password

### For Landsat (USGS)

1. Create account at [USGS Earth Explorer](https://ers.cr.usgs.gov/)
2. Generate API Token:
   - Go to "My Profile" → "Access"
   - Generate "Application Token"
   - Copy the token

---

## First Example: Sentinel-2

```python
from sat_download.api.odata import ODataAPI
from sat_download.services.downloader import SatelliteImageDownloader
from sat_download.data_types.search import SearchFilters
from sat_download.enums import COLLECTIONS

# 1. Configure Copernicus API
api = ODataAPI(
    username="your_email@example.com",
    password="your_password"
)

# 2. Create downloader
downloader = SatelliteImageDownloader(api, verbose=1)

# 3. Define search
filters = SearchFilters(
    collection=COLLECTIONS.SENTINEL_2.value,
    processing_level="L2A",
    start_date="2024-01-01",
    end_date="2024-01-31",
    tile_id="30TWM"  # Madrid, Spain
)

# 4. Search for images
print("Searching for images...")
results = downloader.search(filters)
print(f"Found {len(results)} images")

# 5. Display information
for image in results.values():
    print(f"- {image.date}: {image.sensor} {image.tile}")

# 6. Download (optional)
if results:
    print("\nDownloading images...")
    paths = downloader.bulk_download(results, outdir="./sentinel2_madrid")
    print(f"Downloaded {len([p for p in paths if p])} images")
```

---

## First Example: Landsat 8

```python
from sat_download.api.usgs import USGSAPI
from sat_download.services.downloader import SatelliteImageDownloader
from sat_download.data_types.search import SearchFilters
from sat_download.enums import COLLECTIONS

# 1. Configure USGS API (use API Token, not password)
api = USGSAPI(
    username="your_username",
    password="your_api_token_here"
)

# 2. Create downloader
downloader = SatelliteImageDownloader(api, verbose=1)

# 3. Define search
filters = SearchFilters(
    collection=COLLECTIONS.LANDSAT_8.value,
    processing_level="T1",  # Tier 1 (highest quality)
    start_date="2024-01-01",
    end_date="2024-01-31",
    tile_id="203033"  # Path 203, Row 033
)

# 4. Search for images
print("Searching for images...")
results = downloader.search(filters)
print(f"Found {len(results)} images")

# 5. Download
if results:
    print("\nDownloading images...")
    paths = downloader.bulk_download(results, outdir="./landsat8")
    print(f"Downloaded {len([p for p in paths if p])} images")
```

---

## Key Concepts

### SearchFilters

Define which images to search for:

```python
filters = SearchFilters(
    collection="SENTINEL-2",        # Which satellite
    start_date="2024-01-01",        # From when
    end_date="2024-01-31",          # Until when
    processing_level="L2A",         # Processing level (optional)
    tile_id="30TWM",                # Specific tile (optional)
    geometry="POINT(-3.7 40.4)"     # Coordinates (optional)
)
```

### SearchResults

Dictionary of found images:

```python
results = downloader.search(filters)

# Iterate over results
for product_id, image in results.items():
    print(f"{image.date}: {image.filename}")

# Count results
print(f"Total: {len(results)}")
```

### SatelliteImage

Object with image metadata:

```python
image = results[list(results.keys())[0]]

print(image.sensor)      # "Sentinel-2"
print(image.date)        # "20240115"
print(image.tile)        # "30TWM"
print(image.filename)    # "S2A_MSIL2A_...zip"
```

---

## Search by Location

### By Tile ID

**Sentinel-2 (MGRS system)**:
```python
# Find your tile: https://eatlas.org.au/data/uuid/f7468d15-12be-4e3f-a246-b2882a324f59
filters = SearchFilters(
    collection=COLLECTIONS.SENTINEL_2.value,
    start_date="2024-01-01",
    end_date="2024-01-31",
    tile_id="30TWM"  # Madrid
)
```

**Landsat 8 (WRS-2 Path/Row system)**:
```python
# Find Path/Row: https://landsat.usgs.gov/landsat_acq
filters = SearchFilters(
    collection=COLLECTIONS.LANDSAT_8.value,
    start_date="2024-01-01",
    end_date="2024-01-31",
    tile_id="203033"  # Path 203, Row 033
)
```

### By Coordinates

```python
# Madrid (lon, lat in WGS84)
filters = SearchFilters(
    collection=COLLECTIONS.SENTINEL_2.value,
    start_date="2024-01-01",
    end_date="2024-01-31",
    geometry="POINT(-3.7037902 40.4167754)"
)
```

### By Area (Polygon)

```python
# Bounding box around Barcelona
bbox = "POLYGON((2.05 41.32, 2.25 41.32, 2.25 41.45, 2.05 41.45, 2.05 41.32))"

filters = SearchFilters(
    collection=COLLECTIONS.SENTINEL_2.value,
    start_date="2024-01-01",
    end_date="2024-01-31",
    geometry=bbox
)
```

---

## Image Filtering

### By Processing Level

**Sentinel-2**:
```python
# L2A = Surface reflectance (recommended)
filters = SearchFilters(
    collection=COLLECTIONS.SENTINEL_2.value,
    processing_level="L2A",
    ...
)

# L1C = Top-of-atmosphere reflectance
filters = SearchFilters(
    collection=COLLECTIONS.SENTINEL_2.value,
    processing_level="L1C",
    ...
)
```

**Landsat 8**:
```python
# T1 = Tier 1 (highest quality)
filters = SearchFilters(
    collection=COLLECTIONS.LANDSAT_8.value,
    processing_level="T1",
    ...
)

# T2 = Tier 2 (standard quality)
filters = SearchFilters(
    collection=COLLECTIONS.LANDSAT_8.value,
    processing_level="T2",
    ...
)
```

### By Name Content

```python
# Filter by strings in filename
filters = SearchFilters(
    collection=COLLECTIONS.SENTINEL_2.value,
    start_date="2024-01-01",
    end_date="2024-01-31",
    tile_id="30TWM",
    contains=["MSIL2A", "N0510"]  # Only L2A with version N0510
)
```

---

## Selective Download

### Download Only Most Recent

```python
from datetime import datetime

# Search
results = downloader.search(filters)

# Sort by date
sorted_images = sorted(
    results.items(),
    key=lambda x: x[1].date,
    reverse=True  # Most recent first
)

# Take only the 3 most recent
recent = dict(sorted_images[:3])

# Download
paths = downloader.bulk_download(recent, "./recent_images")
```

### Download Only from One Satellite

```python
# Search
results = downloader.search(filters)

# Filter by Sentinel-2A
s2a_only = {
    k: v for k, v in results.items()
    if v.brother == "A"
}

# Download
paths = downloader.bulk_download(s2a_only, "./sentinel2a")
```

---

## Searching Large Date Ranges

For date ranges > 1 month, use `bulk_search()`:

```python
# Search entire year
filters = SearchFilters(
    collection=COLLECTIONS.SENTINEL_2.value,
    start_date="2023-01-01",
    end_date="2023-12-31",
    tile_id="30TWM"
)

# bulk_search automatically splits the range
results = downloader.bulk_search(filters)
print(f"Total: {len(results)} images")
```

---

## Common Error Handling

### Error: Incorrect Credentials

**Sentinel-2**:
```
Keycloak token creation failed
```

**Solution**: Verify email and password at https://dataspace.copernicus.eu/

**Landsat 8**:
```
Authentication error
```

**Solution**: Verify that you use API Token (not password) from https://ers.cr.usgs.gov/profile/access

### Error: No Images Found

```python
results = downloader.search(filters)
if not results:
    print("No images found")
    # Check:
    # - Valid date range
    # - Correct Tile ID
    # - Correct Collection
```

### Error: Download Failed

```python
paths = downloader.bulk_download(results, "./images")

# Check which ones failed
for idx, (product_id, image) in enumerate(results.items()):
    if paths[idx] is None:
        print(f"Failed: {image.filename}")
        # Retry individually if necessary
```

---

## Next Steps
- **[Architecture](../architecture/overview.md)**: Understand the design
- **[API Reference](../api/base.md)**: Detailed documentation

---

## Complete Example Script

Save as `download_sentinel.py`:

```python
#!/usr/bin/env python3
"""
Example script to download Sentinel-2 images.
"""

from sat_download.api.odata import ODataAPI
from sat_download.services.downloader import SatelliteImageDownloader
from sat_download.data_types.search import SearchFilters
from sat_download.enums import COLLECTIONS

def main():
    # Configuration
    USERNAME = "your_email@example.com"
    PASSWORD = "your_password"
    TILE_ID = "30TWM"
    START_DATE = "2024-01-01"
    END_DATE = "2024-01-31"
    OUTPUT_DIR = "./sentinel2_images"
    
    # Create API and downloader
    print("Connecting to Copernicus Data Space...")
    api = ODataAPI(username=USERNAME, password=PASSWORD)
    downloader = SatelliteImageDownloader(api, verbose=1)
    
    # Define search
    filters = SearchFilters(
        collection=COLLECTIONS.SENTINEL_2.value,
        processing_level="L2A",
        start_date=START_DATE,
        end_date=END_DATE,
        tile_id=TILE_ID
    )
    
    # Search
    print(f"\nSearching for L2A images from tile {TILE_ID}...")
    results = downloader.search(filters)
    
    if not results:
        print("No images found.")
        return
    
    print(f"\nFound {len(results)} images:")
    for image in results.values():
        print(f"  - {image.date}: {image.filename}")
    
    # Confirm download
    response = input(f"\nDownload {len(results)} images? (y/n): ")
    if response.lower() != 'y':
        print("Download cancelled.")
        return
    
    # Download
    print(f"\nDownloading to {OUTPUT_DIR}...")
    paths = downloader.bulk_download(results, OUTPUT_DIR)
    
    # Report
    successful = len([p for p in paths if p is not None])
    print(f"\n✓ Completed: {successful}/{len(results)} successful downloads")

if __name__ == "__main__":
    main()
```

Run:

```bash
python download_sentinel.py
```

---

## Help and Support

- **Issues**: [GitHub Issues](https://github.com/Aouei/remote-sensing-satellite-downloader/issues)
- **Documentation**: This documentation
- **Copernicus Support**: [Forum](https://forum.dataspace.copernicus.eu/)
- **USGS Support**: [Contact](https://www.usgs.gov/centers/eros/contact-us)
