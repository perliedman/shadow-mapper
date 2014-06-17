#!/usr/bin/env python
import mapnik

class MapRenderer:
    def __init__(self, size, stylesheet):
        self._map = mapnik.Map(size, size)
        mapnik.load_map(self._map, stylesheet)

    def render_to_file(self, xmin, ymin, xmax, ymax, path):
        extent = mapnik.Box2d(xmin, ymin, xmax, ymax)
        self._map.zoom_to_box(extent)
        mapnik.render_to_file(self._map, path)

if __name__ == '__main__':
    from sys import argv
    from heightmap import Map, HeightMap
    import os

    with open(argv[1], 'rb') as f:
        hm = Map.load(f)

    cwd = os.getcwd()
    os.chdir(os.path.dirname(argv[2]))
    renderer = MapRenderer(hm.size, argv[2])
    xmin, ymin, xmax, ymax = hm.bounds
    renderer.render_to_file(xmin, ymin, xmax, ymax, os.path.join(cwd, argv[3]))
