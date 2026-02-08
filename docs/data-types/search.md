# Search Types

## Overview

The `sat_download.data_types.search` module defines the data structures used to specify search criteria and represent search results.

---

## API Reference

### SatelliteImage

::: sat_download.data_types.search.SatelliteImage
    options:
      show_root_heading: true
      show_source: true
      members_order: source

---

### SearchFilters

::: sat_download.data_types.search.SearchFilters
    options:
      show_root_heading: true
      show_source: true
      members_order: source

---

### SearchResults

::: sat_download.data_types.search.SearchResults
    options:
      show_root_heading: true
      show_source: false

---

## Usage Examples

### Creating SearchFilters

```python
from sat_download.data_types.search import SearchFilters
from sat_download.enums import COLLECTIONS

# Minimal filters (required fields only)
filters = SearchFilters(
    collection=COLLECTIONS.SENTINEL_2.value,
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# Full filters
filters = SearchFilters(
    collection=COLLECTIONS.SENTINEL_2.value,
    start_date="2024-01-01",
    end_date="2024-01-31",
    processing_level="L2A",
    geometry="POINT(-3.7 40.4)",
    tile_id="30TWM",
    contains=["MSIL2A"]
)

# Check if a filter is set
if filters.is_set('tile_id'):
    print(f"Searching for tile: {filters.tile_id}")
```

### Working with SatelliteImage

```python
from sat_download.data_types.search import SatelliteImage

# Images are typically created by the factory
# but can be created manually for testing
image = SatelliteImage(
    uuid="20240115_S2A",
    date="20240115",
    sensor="Sentinel-2",
    brother="A",
    identifier="Sentinel-2A",
    filename="S2A_MSIL2A_20240115T105421.zip",
    tile="30TWM"
)

print(f"Sensor: {image.sensor}")
print(f"Date: {image.date}")
print(f"Tile: {image.tile}")
print(f"File: {image.filename}")
```

### Working with SearchResults

```python
from sat_download.api.odata import ODataAPI
from sat_download.data_types.search import SearchFilters, SearchResults

api = ODataAPI(username="user", password="pass")
filters = SearchFilters(...)

# Search returns SearchResults (Dict[str, SatelliteImage])
results: SearchResults = api.search(filters)

# Iterate over results
for product_id, image in results.items():
    print(f"{product_id}: {image.filename}")

# Get number of results
print(f"Found {len(results)} images")

# Check if results exist
if results:
    first_id = list(results.keys())[0]
    first_image = results[first_id]
```

---

## Filter Reference

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `collection` | `str` | Collection identifier from `COLLECTIONS` enum |
| `start_date` | `str` | Search start date (YYYY-MM-DD format) |
| `end_date` | `str` | Search end date (YYYY-MM-DD format) |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `processing_level` | `str \| None` | `None` | Processing level (L1C, L2A, T1, T2) |
| `geometry` | `str \| None` | `None` | WKT geometry string |
| `tile_id` | `str \| None` | `None` | Tile/path-row identifier |
| `contains` | `List[str] \| None` | `None` | Strings to filter by name |

---

## Geometry Formats

The `geometry` field accepts WKT (Well-Known Text) format:

```python
# Point
geometry = "POINT(-3.7037902 40.4167754)"

# Polygon (rectangle)
geometry = "POLYGON((-4 40, -3 40, -3 41, -4 41, -4 40))"

# Polygon (complex shape)
geometry = "POLYGON((-3.8 40.3, -3.6 40.3, -3.6 40.5, -3.7 40.6, -3.8 40.5, -3.8 40.3))"
```

---

## References

- [Enumerations](enums.md) - Collection identifiers
- [API Reference](../api/base.md) - Using filters with APIs
