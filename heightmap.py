#!/usr/bin/python
from os import path
from pyproj import Proj
import numpy
from srtm import VFPTile
from PIL import Image, ImageDraw
import json

class HeightMap(object):
    def __init__(self, lat, lng, resolution, size, proj):
        self.size = size
        self.psize = size * resolution
        self.proj = proj
        cx, cy = proj(lng, lat)

        self.bounds = (
            cx - self.psize / 2,
            cy - self.psize / 2,
            cx + self.psize / 2,
            cy + self.psize / 2,
            )

        w, s = proj(self.bounds[0], self.bounds[1], inverse=True)
        e, n = proj(self.bounds[2], self.bounds[3], inverse=True)

        self.ll_bounds = (s, w, n, e)
        self.heights = numpy.zeros((size, size), dtype=float)

    def to_image(self):
        data = self.heights
        rescaled = (255.0 / data.max() * (data - data.min())).astype(numpy.uint8)
        return Image.fromarray(rescaled)

    def _latLngToIndex(self, lat, lng):
        x, y = self.proj(lng, lat)
        return (
            (x - self.bounds[0]) / self.psize * self.size,
            (y - self.bounds[1]) / self.psize * self.size)

class OSMHeightMap(HeightMap):
    def __init__(self, lat, lng, resolution, size, proj, f):
        HeightMap.__init__(self, lat, lng, resolution, size, proj)

        img = Image.new('F', (size, size))
        draw = ImageDraw.Draw(img)
        fc = json.load(f)
        for f in fc['features']:
            h = float(f['properties']['height']) if f['properties'].has_key('height') else 10
            coords = map(lambda ll: self._latLngToIndex(ll[1], ll[0]), f['geometry']['coordinates'][0])
            draw.polygon(coords, fill=h)

        self.heights = numpy.array(img)

class SrtmHeightMap(HeightMap):
    def __init__(self, lat, lng, resolution, size, proj, data_dir):
        HeightMap.__init__(self, lat, lng, resolution, size, proj)

        tiles = {}

        for y in xrange(0, size):
            cy = self.bounds[1] + y / float(size) * self.psize
            for x in xrange(0, size):
                cx = self.bounds[0] + x / float(size) * self.psize
                lng, lat = proj(cx, cy, inverse=True)

                tile_key = SrtmHeightMap._tileKey(lat, lng)
                if not tiles.has_key(tile_key):
                    tiles[tile_key] = SrtmHeightMap._loadTile(data_dir, lat, lng)
                    print 'Loaded tile', tile_key

                v = tiles[tile_key].getAltitudeFromLatLon(lat, lng)
                self.heights[y,x] = v
    @staticmethod
    def _tileKey(lat, lng):
        return '%s%02d%s%03d.hgt' % (
            'N' if lat >= 0 else 'S',
            int(lat),
            'E' if lng >= 0 else 'W',
            int(lng))

    @staticmethod
    def _loadTile(data_dir, lat, lng):
        p = path.join(data_dir, SrtmHeightMap._tileKey(lat, lng))
        with open(p, 'rb') as f:
            return VFPTile(f, int(lat), int(lng))

if __name__ == '__main__':
    from sys import argv

    lat = float(argv[1])
    lng = float(argv[2])
    resolution = float(argv[3])
    size = int(argv[4])

    proj = Proj(init='epsg:3006')

    elev = SrtmHeightMap(lat, lng, resolution, size, proj, 'data')
    with open('data/gbg.geojson', 'r') as f:
        buildings = OSMHeightMap(lat, lng, resolution, size, proj, f)

    hm = HeightMap(lat, lng, resolution, size, proj)
    hm.heights = elev.heights + buildings.heights

    hm.to_image().transpose(Image.FLIP_TOP_BOTTOM).save('a.png')