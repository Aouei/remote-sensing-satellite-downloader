from data_types.search import SatelliteImage
from enums import COLLECTIONS


def get_satellite_image(collection : COLLECTIONS, data : dict) -> SatelliteImage:
    if collection == COLLECTIONS.SENTINEL_2:
        result = get_sentinel2(collection.value.lower().capitalize(), data['Name'])
    elif collection == COLLECTIONS.SENTINEL_3:
        result = get_sentinel3(collection.value.lower().capitalize(), data['Name'])
    elif collection == COLLECTIONS.LANDSAT_8:
        result = get_landsat_8('Landsat-8', data['Name'])

    return result


def get_sentinel2(satellite : str, name : str) -> SatelliteImage:
    components = name.split('_')
    satellite_position = 0
    date_position = 2
    tile_position = -2

    date : str = components[date_position].split('T')[0]
    brother : str = components[satellite_position][-1]
    uuid : str = f"{date}_{components[satellite_position]}"
    tile : str = components[tile_position][1:]

    result : SatelliteImage = SatelliteImage(uuid = uuid, date = date, sensor = satellite, 
                                             brother = brother, identifier = f"{satellite}{brother}", 
                                             tile = tile, filename = f"{name.split('.')[0]}.zip")
    return result
    
def get_sentinel3(satellite : str, name : str) -> SatelliteImage:
    components = name.split('_')
    satellite_position = 0
    date_position = 7
    tile_position = 11

    date : str = components[date_position].split('T')[0]
    brother : str = components[satellite_position][-1]
    uuid : str = f"{date}_{components[satellite_position]}"
    tile : str = components[tile_position]

    result : SatelliteImage = SatelliteImage(uuid = uuid, date = date, sensor = satellite, 
                                             brother = brother, identifier = f"{satellite}{brother}", 
                                             tile = tile, filename = f"{name.split('.')[0]}.zip")
    return result
    
def get_landsat_8(satellite : str, name : str) -> SatelliteImage:
    components = name.split('_')
    tile = components[2]
    date = components[3]
    brother = components[0][-1]
    uuid =  f'L{brother}_{date}'
    result : SatelliteImage = SatelliteImage(uuid = uuid, date = date, sensor = satellite, 
                                             brother = brother, identifier = f'{satellite[:-1] + brother}', 
                                             filename = f"{name.split('.')[0]}.tar", tile = tile)

    return result