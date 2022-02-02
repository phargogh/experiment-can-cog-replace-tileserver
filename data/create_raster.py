import os

import numpy
import pygeoprocessing
from osgeo import gdal
from osgeo import osr

# I'm assuming that our synthetic raster here will cover the globe, just not
# have any real-world values.
# These details are copied from another raster I have, so roughly 5 arcseconds
# resolution
ORIGIN = (-180, 90)
PIXELSIZE = (0.083333333333333, -0.083333333333333)
COLS, ROWS = (4320, 2160)
SRS = osr.SpatialReference()
SRS.ImportFromEPSG(4326)

TARGET_RASTER = os.path.join(os.path.dirname(__file__), 'raster.tif')
GTIFF_OPTIONS = [
    'COMPRESS=LZW',
    'TILED=YES',
    'BLOCKXSIZE=256',
    'BLOCKYSIZE=256',
]
NODATA_INT32 = -9999
NODATA_FLOAT32 = float(numpy.finfo(numpy.float32).min)


def create(target_filepath):
    driver = gdal.GetDriverByName('GTiff')
    target_raster = driver.Create(
        target_filepath, COLS, ROWS, 1, gdal.GDT_Int32, options=GTIFF_OPTIONS)
    target_raster.SetProjection(SRS.ExportToWkt())
    target_raster.SetGeoTransform(
        [ORIGIN[0], PIXELSIZE[0], 0, ORIGIN[1], 0, PIXELSIZE[1]])
    target_band = target_raster.GetRasterBand(1)
    target_band.SetNoDataValue(NODATA_INT32)

    target_band = None
    target_raster = None

    index = 0
    target_raster = gdal.OpenEx(target_filepath, gdal.GA_Update)
    target_band = target_raster.GetRasterBand(1)
    for block_info in pygeoprocessing.iterblocks((target_filepath, 1),
                                                 largest_block=-1,
                                                 offset_only=True):
        array = numpy.full((block_info['win_ysize'], block_info['win_xsize']),
                           index, dtype=numpy.int32)
        array += numpy.random.randint(
            -30, 31, size=array.size).reshape(array.shape)  # make a little noise.
        target_band.WriteArray(array, xoff=block_info['xoff'],
                               yoff=block_info['yoff'])
        index += 5

    target_band = None
    target_raster = None


if __name__ == '__main__':
    create(TARGET_RASTER)
