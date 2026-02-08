# OData API (Copernicus)

## Overview

The `sat_download.api.odata` module provides the `SatelliteAPI` implementation for the **Copernicus Data Space Ecosystem**, allowing searching and downloading of Sentinel-2 and Sentinel-3 images.

---

## API Reference

::: sat_download.api.odata.ODataAPI
    options:
      show_root_heading: true
      show_source: true
      members:
        - __init__
        - search
        - download

---

## Endpoints

| Constant | Value | Description |
|----------|-------|-------------|
| `SEARCH_URL` | `https://catalogue.dataspace.copernicus.eu/odata/v1/Products` | Catalog search endpoint |
| `DOWNLOAD_URL` | `https://download.dataspace.copernicus.eu/odata/v1/Products` | Download endpoint |
| `TOKEN_URL` | `https://identity.dataspace.copernicus.eu/.../token` | OAuth2 token endpoint |

---

## Supported Filters

| Filter | Type | Description | Example |
|--------|------|-------------|---------|
| `collection` | `str` | Satellite collection | `"SENTINEL-2"` |
| `start_date` | `str` | Start date (YYYY-MM-DD) | `"2024-01-01"` |
| `end_date` | `str` | End date (YYYY-MM-DD) | `"2024-01-31"` |
| `processing_level` | `str` | Processing level | `"L2A"` |
| `geometry` | `str` | WKT geometry | `"POINT(-3.7 40.4)"` |
| `tile_id` | `str` | Tile identifier | `"30TWM"` |
| `contains` | `List[str]` | Strings in name | `["MSIL2A"]` |

---

## Usage Examples

### Basic Search

```python
from sat_download.api.odata import ODataAPI
from sat_download.data_types.search import SearchFilters
from sat_download.enums import COLLECTIONS

api = ODataAPI(
    username="your_email@example.com",
    password="your_secure_password"
)

filters = SearchFilters(
    collection=COLLECTIONS.SENTINEL_2.value,
    processing_level="L2A",
    start_date="2024-06-01",
    end_date="2024-06-30",
    tile_id="30TWM"
)

results = api.search(filters)

for product_id, image in results.items():
    print(f"{image.date}: {image.filename}")
```

### Search by Geometry

```python
# Search by point (Madrid, Spain)
filters = SearchFilters(
    collection=COLLECTIONS.SENTINEL_2.value,
    start_date="2024-01-01",
    end_date="2024-01-31",
    geometry="POINT(-3.7037902 40.4167754)"
)

results = api.search(filters)
```

### Search with Polygon

```python
# Search in rectangular area
wkt = "POLYGON((-4 40, -3 40, -3 41, -4 41, -4 40))"

filters = SearchFilters(
    collection=COLLECTIONS.SENTINEL_3.value,
    start_date="2024-01-01",
    end_date="2024-01-31",
    geometry=wkt
)

results = api.search(filters)
```

### Download Images

```python
# Search for images
results = api.search(filters)

# Download the first image
if results:
    first_id = list(results.keys())[0]
    first_image = results[first_id]
    
    filepath = api.download(
        image_id=first_id,
        outname=f"./images/{first_image.filename}",
        verbose=1
    )
    
    if filepath:
        print(f"Downloaded: {filepath}")
```

---

## Authentication

ODataAPI uses **OAuth2** authentication with Copernicus Keycloak:

1. Credentials are stored during initialization
2. Token is requested on-demand when downloading
3. Token is refreshed automatically if expired

!!! info "Account Required"
    Register at [https://dataspace.copernicus.eu/](https://dataspace.copernicus.eu/)

---

## OData Query Syntax

The search method builds OData queries automatically:

```
$filter=Collection/Name eq 'SENTINEL-2' 
    and ContentDate/Start gt 2024-01-01T00:00:00.000Z
    and ContentDate/Start lt 2024-01-31T23:59:59.999Z
    and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' 
        and att/OData.CSC.StringAttribute/Value eq 'S2MSI2A')
```

---

## References

- [Copernicus Data Space](https://dataspace.copernicus.eu/)
- [OData API Documentation](https://documentation.dataspace.copernicus.eu/)
- [Base API](base.md)
