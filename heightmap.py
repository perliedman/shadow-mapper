#!/usr/bin/python
from os import path
from pyproj import Proj
import numpy
from srtm import VTPTile
from PIL import Image, ImageDraw
import json
from map import Map

class HeightMap(Map):
    def __init__(self, lat, lng, resolution, size, proj):
        Map.__init__(self, lat, lng, resolution, size, proj)
        self.heights = numpy.zeros((size, size), dtype=float)

    def to_image(self):
        data = self.heights
        rescaled = (255.0 / data.max() * (data - data.min())).astype(numpy.uint8)
        return Image.fromarray(rescaled).transpose(Image.FLIP_TOP_BOTTOM)

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
            return VTPTile(f, int(lat), int(lng))

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

    hm.to_image().save('a.png')
    with open('a.pickle', 'wb') as f:
        hm.save(f)
