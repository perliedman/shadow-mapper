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
    from map import Map
    from heightmap import HeightMap
    import os
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('heightmap', type=str, help='Heightmap file to create background for')
    parser.add_argument('mapnik_xml', type=str, help='Mapnik XML file to render')
    parser.add_argument('output_file', type=str, help='File to output result image to')

    args = parser.parse_args()

    with open(args.heightmap, 'rb') as f:
        hm = Map.load(f)

    cwd = os.getcwd()
    os.chdir(os.path.dirname(args.mapnik_xml))
    renderer = MapRenderer(hm.size, args.mapnik_xml)
    xmin, ymin, xmax, ymax = hm.bounds
    renderer.render_to_file(xmin, ymin, xmax, ymax, os.path.join(cwd, args.output_file))
