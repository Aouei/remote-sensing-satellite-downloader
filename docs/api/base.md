# Base API Module

## Overview

The `sat_download.api.base` module provides the abstract base class `SatelliteAPI` that defines the contract all provider API implementations must fulfill.

---

## API Reference

::: sat_download.api.base.SatelliteAPI
    options:
      show_root_heading: true
      show_source: true
      members:
        - __init__
        - search
        - download
        - bulk_search

---

## Available Implementations

| Class | Provider | Collections | Module |
|-------|----------|-------------|--------|
| `ODataAPI` | Copernicus Data Space Ecosystem | Sentinel-2, Sentinel-3 | `sat_download.api.odata` |
| `USGSAPI` | USGS Earth Explorer | Landsat 8 | `sat_download.api.usgs` |

---

## Usage Example

```python
from sat_download.api.odata import ODataAPI
from sat_download.data_types.search import SearchFilters
from sat_download.enums import COLLECTIONS

# Create API instance
api = ODataAPI(username="user", password="pass")

# Define search filters
filters = SearchFilters(
    collection=COLLECTIONS.SENTINEL_2.value,
    start_date="2024-01-01",
    end_date="2024-01-31",
    tile_id="30TWM"
)

# Search for images
results = api.search(filters)
print(f"Found {len(results)} images")

# Download images
for image_id, image in results.items():
    api.download(image_id, f"./images/{image.filename}", verbose=1)
```

---

## Creating a New Implementation

To add support for a new satellite data provider, inherit from `SatelliteAPI`:

```python
from sat_download.api.base import SatelliteAPI
from sat_download.data_types.search import SearchFilters, SearchResults

class NewProviderAPI(SatelliteAPI):
    """Implementation for a new satellite data provider."""
    
    API_URL = "https://api.newprovider.com/v1/"
    
    def __init__(self, username: str, password: str) -> None:
        super().__init__(username, password)
        self._authenticate()
    
    def search(self, filters: SearchFilters) -> SearchResults:
        # Implement provider-specific search
        pass
    
    def download(self, image_id: str, outname: str, verbose: int) -> str | None:
        # Implement provider-specific download
        pass
```

---

## Design Patterns

The base module implements several design patterns:

- **Abstract Factory Pattern**: Defines interface for creating API clients
- **Template Method Pattern**: `bulk_search()` defines algorithm skeleton

See: [Design Patterns](../architecture/design-patterns.md)

---

## Related Types

::: sat_download.data_types.search.SearchFilters
    options:
      show_root_heading: true
      show_source: false
      members: false

::: sat_download.data_types.search.SatelliteImage
    options:
      show_root_heading: true
      show_source: false
      members: false
