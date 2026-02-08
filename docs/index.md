# Remote Sensing Satellite Downloader

**Remote Sensing Satellite Downloader** is a Python library designed to facilitate the search and download of satellite images from multiple remote sensing data providers.

## Key Features

✨ **Multiple Providers**: Support for Copernicus Data Space (Sentinel) and USGS Earth Explorer (Landsat)

🔍 **Advanced Search**: Filters by date, geometry, processing level, and tile ID

⬇️ **Bulk Download**: Download multiple images in parallel

🎨 **Unified API**: Consistent interface regardless of data provider

🔧 **Extensible**: Architecture based on design patterns that facilitates adding new providers

## Supported Providers

### Copernicus Data Space Ecosystem
- **Sentinel-2**: High-resolution multispectral imagery
- **Sentinel-3**: Ocean and land data

### USGS Earth Explorer
- **Landsat 8**: Multispectral land imagery

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

## Quick Start

### Basic example with Sentinel-2

```python
from sat_download.api.odata import ODataAPI
from sat_download.services.downloader import SatelliteImageDownloader
from sat_download.data_types.search import SearchFilters
from sat_download.enums import COLLECTIONS

# Configure Copernicus API
api = ODataAPI(username="your_username", password="your_password")
downloader = SatelliteImageDownloader(api, verbose=1)

# Define search filters
filters = SearchFilters(
    collection=COLLECTIONS.SENTINEL_2.value,
    processing_level="L2A",
    start_date="2024-01-01",
    end_date="2024-01-31",
    tile_id="30TWM"
)

# Search for images
results = downloader.search(filters)
print(f"Found {len(results)} images")

# Download images
downloader.bulk_download(results, outdir="./satellite_images")
```

### Example with Landsat 8

```python
from sat_download.api.usgs import USGSAPI
from sat_download.services.downloader import SatelliteImageDownloader
from sat_download.data_types.search import SearchFilters
from sat_download.enums import COLLECTIONS

# Configure USGS API (use API token, not password)
api = USGSAPI(username="your_username", password="your_api_token")
downloader = SatelliteImageDownloader(api, verbose=1)

# Define filters
filters = SearchFilters(
    collection=COLLECTIONS.LANDSAT_8.value,
    processing_level="T1",
    start_date="2024-01-01",
    end_date="2024-01-31",
    tile_id="203033"
)

# Search and download
results = downloader.search(filters)
downloader.bulk_download(results, outdir="./landsat_images")
```

## Project Structure

```
sat_download/
├── api/              # Provider API implementations
│   ├── base.py       # Abstract base class
│   ├── odata.py      # Copernicus API
│   └── usgs.py       # USGS API
├── data_types/       # Data structures
│   └── search.py     # Search filters and results
├── factories/        # Factories for creating objects
│   └── search.py     # Satellite image factory
├── services/         # High-level services
│   └── downloader.py # Download service
└── enums.py          # Enumerations (collections)
```

## Documentation

- **[Architecture](architecture/overview.md)**: System design and components
- **[Design Patterns](architecture/design-patterns.md)**: Patterns used in the project
- **[API Reference](api/base.md)**: Detailed documentation of all modules
- **[Guides](guides/quickstart.md)**: Tutorials and usage examples

## Links

- [GitHub Repository](https://github.com/Aouei/remote-sensing-satellite-downloader)
- [Copernicus Data Space](https://dataspace.copernicus.eu/)
- [USGS Earth Explorer](https://earthexplorer.usgs.gov/)

## License

See the LICENSE file in the repository.
