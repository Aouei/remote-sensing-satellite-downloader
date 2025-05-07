from sat_download.data_types.search import SatelliteImage
from sat_download.enums import COLLECTIONS


def get_satellite_image(collection: COLLECTIONS, data: dict) -> SatelliteImage:
    """
    Factory function to create a SatelliteImage object based on collection type and metadata.
    
    Parameters
    ----------
    collection : COLLECTIONS
        The satellite collection enum indicating the source platform
    data : dict
        Dictionary containing metadata about the satellite image
        
    Returns
    -------
    SatelliteImage
        A standardized satellite image object with extracted metadata
        
    Notes
    -----
    This function delegates to specialized parsers for each collection type.
    The 'Name' field in the data dictionary is required for all collection types.
    """
    if collection == COLLECTIONS.SENTINEL_2:
        result = get_sentinel2(collection.value.lower().capitalize(), data['Name'])
    elif collection == COLLECTIONS.SENTINEL_3:
        result = get_sentinel3(collection.value.lower().capitalize(), data['Name'])
    elif collection == COLLECTIONS.LANDSAT_8:
        result = get_landsat_8('Landsat-8', data['Name'])

    return result


def get_sentinel2(satellite: str, name: str) -> SatelliteImage:
    """
    Parse Sentinel-2 image metadata from filename.
    
    Parameters
    ----------
    satellite : str
        The satellite platform name ('Sentinel-2')
    name : str
        The original filename containing metadata components
        
    Returns
    -------
    SatelliteImage
        A standardized satellite image object with extracted metadata
        
    Notes
    -----
    Extracts date, satellite brother (A/B), UUID, and tile information
    from standard Sentinel-2 filename format.
    """
    components = name.split('_')
    satellite_position = 0
    date_position = 2
    tile_position = -2

    date: str = components[date_position].split('T')[0]
    brother: str = components[satellite_position][-1]
    uuid: str = f"{date}_{components[satellite_position]}"
    tile: str = components[tile_position][1:]

    result: SatelliteImage = SatelliteImage(uuid=uuid, date=date, sensor=satellite, 
                                            brother=brother, identifier=f"{satellite}{brother}", 
                                            tile=tile, filename=f"{name.split('.')[0]}.zip")
    return result
    
def get_sentinel3(satellite: str, name: str) -> SatelliteImage:
    """
    Parse Sentinel-3 image metadata from filename.
    
    Parameters
    ----------
    satellite : str
        The satellite platform name ('Sentinel-3')
    name : str
        The original filename containing metadata components
        
    Returns
    -------
    SatelliteImage
        A standardized satellite image object with extracted metadata
        
    Notes
    -----
    Extracts date, satellite brother (A/B), UUID, and tile information
    from standard Sentinel-3 filename format.
    """
    components = name.split('_')
    satellite_position = 0
    date_position = 7
    tile_position = 11

    date: str = components[date_position].split('T')[0]
    brother: str = components[satellite_position][-1]
    uuid: str = f"{date}_{components[satellite_position]}"
    tile: str = components[tile_position]

    result: SatelliteImage = SatelliteImage(uuid=uuid, date=date, sensor=satellite, 
                                            brother=brother, identifier=f"{satellite}{brother}", 
                                            tile=tile, filename=f"{name.split('.')[0]}.zip")
    return result
    
def get_landsat_8(satellite: str, name: str) -> SatelliteImage:
    """
    Parse Landsat-8 image metadata from filename.
    
    Parameters
    ----------
    satellite : str
        The satellite platform name ('Landsat-8')
    name : str
        The original filename containing metadata components
        
    Returns
    -------
    SatelliteImage
        A standardized satellite image object with extracted metadata
        
    Notes
    -----
    Extracts date, satellite collection number, UUID, and tile information
    from standard Landsat-8 filename format.
    """
    components = name.split('_')
    tile = components[2]
    date = components[3]
    brother = components[0][-1]
    uuid = f'L{brother}_{date}'
    result: SatelliteImage = SatelliteImage(uuid=uuid, date=date, sensor=satellite, 
                                            brother=brother, identifier=f'{satellite[:-1] + brother}', 
                                            filename=f"{name.split('.')[0]}.tar", tile=tile)

    return result