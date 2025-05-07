from typing import Dict
from dataclasses import dataclass


@dataclass
class SatelliteImage:
    """Class representing the metadata of a satellite image for processing it"""
    
    uuid : str
    date : str
    sensor : str
    brother : str
    identifier : str
    filename : str
    tile : str
    zone : str | None = None
    acolite_file : str | None = None
    clipped_folder : str | None = None
    plot_folder : str | None = None


@dataclass
class SearchFilters:
    collection : str
    start_date : str
    end_date : str
    processing_level : str = None
    geometry : str = None
    tile_id : str = None

    def is_set(self, value : str) -> bool:
        return self.__dict__.get(value, None) is not None
    

SearchResults = Dict[str, SatelliteImage]