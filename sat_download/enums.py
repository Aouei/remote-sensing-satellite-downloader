from enum import Enum


class COLLECTIONS(Enum):
    """
    Enumeration of supported satellite image collections.
    
    This enum defines the standard collection identifiers used by different
    satellite data providers.
    
    Attributes
    ----------
    SENTINEL_2 : str
        Collection identifier for Sentinel-2 imagery (value: 'SENTINEL-2')
    SENTINEL_3 : str
        Collection identifier for Sentinel-3 imagery (value: 'SENTINEL-3')
    LANDSAT_8 : str
        Collection identifier for Landsat 8 imagery (value: 'landsat_ot_c2_l1')
    
    Notes
    -----
    Collection identifiers may differ between data providers and APIs.
    These values represent the standardized identifiers used within this package.
    
    Examples
    --------
    >>> from sat_download.enums import COLLECTIONS
    >>> collection = COLLECTIONS.SENTINEL_2
    >>> print(collection.value)
    'SENTINEL-2'
    """
    
    SENTINEL_2 : str = 'SENTINEL-2'
    SENTINEL_3 : str = 'SENTINEL-3'
    LANDSAT_8 : str = 'landsat_ot_c2_l1'