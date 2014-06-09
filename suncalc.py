#!/usr/bin/python

"""Solar position calculations, adapted from Suncalc, a JS lib
by Vladimir Agafonkin (https://github.com/mourner/suncalc)"""

from math import sin, cos, tan, asin, atan2, pi
from datetime import datetime

rad = pi / 180.0
epochStart = datetime(1970, 1, 1)
J1970 = 2440588
J2000 = 2451545
dayMs = 24 * 60 * 60 * 1000
e = rad * 23.4397 # obliquity of the Earth

def toMillis(date):
    return (date - epochStart).total_seconds() * 1000

def toJulian(date):
    return toMillis(date) / dayMs - 0.5 + J1970

def toDays(date):
    return toJulian(date) - J2000

#function fromJulian(j)  { return new Date((j + 0.5 - J1970) * dayMs); }

def rightAscension(l, b):
    return atan2(sin(l) * cos(e) - tan(b) * sin(e), cos(l))

def declination(l, b):
    return asin(sin(b) * cos(e) + cos(b) * sin(e) * sin(l))

def azimuth(H, phi, dec):
    return atan2(sin(H), cos(H) * sin(phi) - tan(dec) * cos(phi))

def altitude(H, phi, dec):
    return asin(sin(phi) * sin(dec) + cos(phi) * cos(dec) * cos(H))

def siderealTime(d, lw):
    return rad * (280.16 + 360.9856235 * d) - lw

def solarMeanAnomaly(d):
    return rad * (357.5291 + 0.98560028 * d)

def eclipticLongitude(M):
    C = rad * (1.9148 * sin(M) + 0.02 * sin(2 * M) + 0.0003 * sin(3 * M)) # equation of center
    P = rad * 102.9372 # perihelion of the Earth

    return M + C + P + pi

def sunCoords(d):
    M = solarMeanAnomaly(d)
    L = eclipticLongitude(M);

    return {
        'dec': declination(L, 0),
        'ra': rightAscension(L, 0)
    }

def solar_position(date, lat, lng):
    lw  = rad * -lng
    phi = rad * lat
    d   = toDays(date)

    c  = sunCoords(d)
    H  = siderealTime(d, lw) - c['ra']

    return {
        'azimuth': azimuth(H, phi, c['dec']),
        'altitude': altitude(H, phi, c['dec'])
    }

