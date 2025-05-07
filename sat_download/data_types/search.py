from typing import Dict
from dataclasses import dataclass


@dataclass
class SatelliteImage:
    """
    Class representing the metadata of a satellite image.
    
    This class stores standardized metadata about satellite imagery from 
    different sources like Sentinel and Landsat for consistent processing.
    
    Attributes
    ----------
    uuid : str
        Unique identifier for the image
    date : str
        Acquisition date of the image in format 'YYYYMMDD'
    sensor : str
        Sensor or satellite platform name (e.g., 'Sentinel-2', 'Landsat-8')
    brother : str
        Satellite constellation member identifier (e.g., 'A' for Sentinel-2A)
    identifier : str
        Combined satellite and brother identifier (e.g., 'Sentinel-2A')
    filename : str
        Output filename for downloaded image
    tile : str
        Tile or path/row identifier for the image
    
    Notes
    -----
    The structure of attributes is designed to work across different 
    satellite data providers with a consistent interface.
    """
    
    uuid : str
    date : str
    sensor : str
    brother : str
    identifier : str
    filename : str
    tile : str


@dataclass
class SearchFilters:
    """
    Class for specifying search filters for satellite imagery.
    
    This class provides a standardized way to specify search criteria
    across different satellite data providers and APIs.
    
    Parameters
    ----------
    collection : str
        Collection identifier (e.g., 'SENTINEL-2', 'landsat_ot_c2_l1')
    start_date : str
        Start date for the search in format 'YYYY-MM-DD'
    end_date : str
        End date for the search in format 'YYYY-MM-DD'
    processing_level : str, optional
        Processing level filter (e.g., 'L1C', 'L2A')
    geometry : str, optional
        WKT geometry string for spatial filtering (e.g., 'POINT(lon lat)')
    tile_id : str, optional
        Specific tile identifier to filter by
        
    Examples
    --------
    >>> filters = SearchFilters(
    ...     collection="SENTINEL-2",
    ...     processing_level="L1C",
    ...     start_date="2024-10-01",
    ...     end_date="2024-10-31",
    ...     tile_id="30TWM",
    ... )
    >>> filters.is_set('geometry')
    False
    """
    collection : str
    start_date : str
    end_date : str
    processing_level : str = None
    geometry : str = None
    tile_id : str = None

    def is_set(self, value : str) -> bool:
        """
        Check if a filter attribute is set (not None).
        
        Parameters
        ----------
        value : str
            The name of the attribute to check
            
        Returns
        -------
        bool
            True if the attribute exists and is not None, False otherwise
        """
        return self.__dict__.get(value, None) is not None
    

# Type alias for search results
SearchResults = Dict[str, SatelliteImage]
"""
Type alias representing search results from satellite APIs.

A dictionary mapping product IDs (keys) to SatelliteImage objects (values).
"""