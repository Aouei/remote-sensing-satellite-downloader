# Enumerations

## Overview

The `sat_download.enums` module defines enumerations for standardized identifiers used throughout the library.

---

## API Reference

::: sat_download.enums.COLLECTIONS
    options:
      show_root_heading: true
      show_source: true
      members_order: source

---

## Collection Values

| Enum Member | Value | Provider | Satellite |
|-------------|-------|----------|-----------|
| `SENTINEL_2` | `"SENTINEL-2"` | Copernicus | Sentinel-2A/2B |
| `SENTINEL_3` | `"SENTINEL-3"` | Copernicus | Sentinel-3A/3B |
| `LANDSAT_8` | `"landsat_ot_c2_l1"` | USGS | Landsat 8/9 |

---

## Usage Examples

### Basic Usage

```python
from sat_download.enums import COLLECTIONS

# Access collection value
collection = COLLECTIONS.SENTINEL_2
print(collection.value)  # "SENTINEL-2"

# Use in filters
from sat_download.data_types.search import SearchFilters

filters = SearchFilters(
    collection=COLLECTIONS.SENTINEL_2.value,
    start_date="2024-01-01",
    end_date="2024-01-31"
)
```

### Iterating Collections

```python
from sat_download.enums import COLLECTIONS

# List all available collections
for collection in COLLECTIONS:
    print(f"{collection.name}: {collection.value}")

# Output:
# SENTINEL_2: SENTINEL-2
# SENTINEL_3: SENTINEL-3
# LANDSAT_8: landsat_ot_c2_l1
```

### Check Collection Type

```python
from sat_download.enums import COLLECTIONS

def get_api_for_collection(collection: COLLECTIONS):
    """Return appropriate API based on collection."""
    if collection in [COLLECTIONS.SENTINEL_2, COLLECTIONS.SENTINEL_3]:
        from sat_download.api.odata import ODataAPI
        return ODataAPI
    elif collection == COLLECTIONS.LANDSAT_8:
        from sat_download.api.usgs import USGSAPI
        return USGSAPI
    else:
        raise ValueError(f"Unknown collection: {collection}")
```

---

## Collection Details

### Sentinel-2

| Property | Value |
|----------|-------|
| **Enum** | `COLLECTIONS.SENTINEL_2` |
| **Value** | `"SENTINEL-2"` |
| **Provider** | Copernicus Data Space |
| **API** | `ODataAPI` |
| **Satellites** | Sentinel-2A, Sentinel-2B |
| **Resolution** | 10m, 20m, 60m |
| **Bands** | 13 spectral bands |
| **Processing Levels** | L1C, L2A |

### Sentinel-3

| Property | Value |
|----------|-------|
| **Enum** | `COLLECTIONS.SENTINEL_3` |
| **Value** | `"SENTINEL-3"` |
| **Provider** | Copernicus Data Space |
| **API** | `ODataAPI` |
| **Satellites** | Sentinel-3A, Sentinel-3B |
| **Resolution** | 300m (OLCI), 1km (SLSTR) |
| **Instruments** | OLCI, SLSTR, SRAL |

### Landsat 8

| Property | Value |
|----------|-------|
| **Enum** | `COLLECTIONS.LANDSAT_8` |
| **Value** | `"landsat_ot_c2_l1"` |
| **Provider** | USGS Earth Explorer |
| **API** | `USGSAPI` |
| **Satellites** | Landsat 8, Landsat 9 |
| **Resolution** | 15m (pan), 30m (multispectral) |
| **Bands** | 11 bands |
| **Processing Levels** | T1, T2, RT |

---

## Collections by Application

| Application | Recommended Collection |
|-------------|------------------------|
| Agriculture & Vegetation | `SENTINEL_2` (10m, NDVI) |
| Ocean & Marine | `SENTINEL_3` (OLCI) |
| Land Cover Mapping | `SENTINEL_2`, `LANDSAT_8` |
| Time Series Analysis | `LANDSAT_8` (longest archive) |
| High Frequency Monitoring | `SENTINEL_2` (5-day revisit) |

---

## References

- [Search Types](search.md) - Using collections in SearchFilters
- [Copernicus Data Space](https://dataspace.copernicus.eu/)
- [USGS Landsat](https://www.usgs.gov/landsat-missions)
