#!/usr/bin/python
from heightmap import Map
from PIL import Image
import numpy
from math import sqrt
from sys import stdout

def update_progress(progress):
    progress = int(progress * 100)
    print '\r[{0:<10}] {1}%'.format('='*(progress/10), progress),
    stdout.flush()

class SunMap(Map):
    def __init__(self, lat, lng, resolution, size, proj, sun_x, sun_y, sun_z, heightmap, view_alt):
        Map.__init__(self, lat, lng, resolution, size, proj)
        self.sun_x = sun_x
        self.sun_y = sun_y
        self.sun_z = sun_z
        self.heightmap = heightmap
        self.view_alt = view_alt
        self.max_height = numpy.amax(self.heightmap.heights)
        self.min_height = numpy.amin(self.heightmap.heights)

    def render(self):
        result = numpy.zeros((self.size, self.size), numpy.bool_)
        for y in xrange(0, self.size):
            update_progress(y / float(self.size))
            for x in xrange(0, self.size):
                result[y, x] = 1 if self.is_lit(x, y) else 0

        return result

    def to_image(self):
        data = self.render()
        rescaled = (255.0 / data.max() * (data - data.min())).astype(numpy.uint8)
        return Image.fromarray(rescaled).transpose(Image.FLIP_TOP_BOTTOM)

    def is_lit(self, x0, y0):
        x1 = x0 + self.sun_x * self.size
        y1 = y0 + self.sun_y * self.size
        z = self.heightmap.heights[y0, x0] + self.view_alt
        zv = self.sun_z / sqrt(self.sun_x * self.sun_x + self.sun_y * self.sun_y)

        # Following is a Bresenham's algorithm line tracing.
        # This avoids performing lots of float calculations in
        # favor or integers, which is at least 10x faster.
        # Basic implementation taken from
        # http://stackoverflow.com/questions/2734714/modifying-bresenhams-line-algorithm
        steep = abs(y1 - y0) > abs(x1 - x0)
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        if y0 < y1:
            ystep = 1
        else:
            ystep = -1

        deltax = x1 - x0
        deltay = abs(y1 - y0)
        error = -deltax / 2
        y = y0

        xdir = 1 if x0 < x1 else -1
        x = x0
        while x > 0 and x < self.size and y > 0 and \
            y < self.size and z > self.min_height and z < self.max_height:
            if (steep and self.heightmap.heights[x, y] > z) or \
                (not steep and self.heightmap.heights[y, x] > z):
                return False

            error = error + deltay
            if error > 0:
                y = y + ystep
                error = error - deltax

            x += xdir
            z += zv

        return True

if __name__ == '__main__':
    from sys import argv
    from datetime import datetime
    from heightmap import HeightMap
    from suncalc import solar_position
    from math import sin, cos

    with open('a.pickle', 'rb') as f:
        hm = HeightMap.load(f)

    t = datetime.strptime(argv[1], '%Y-%m-%d %H:%M')
    sunpos = solar_position(t, float(argv[2]), float(argv[3]))
    sun_x = sin(sunpos['azimuth']) * cos(sunpos['altitude'])
    sun_y = -cos(sunpos['azimuth']) * cos(sunpos['altitude'])
    sun_z = sin(sunpos['altitude'])

    sm = SunMap(hm.lat, hm.lng, hm.resolution, hm.size, hm.proj, sun_x, sun_y, sun_z, hm, 1.5)
    sm.to_image().save('b.png')
