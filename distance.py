#!/usr/bin/env python
# Read a GPX file and calculate the distance travelled in the first track of the file
# Output distance and mean speed.

import sys
import math
from xml.dom import minidom

def Deg2Rad(x):
    "Degrees to radians."
    return x * (math.pi/180)

def Rad2Deg(x):
    "Radians to degress."
    return x * (180/math.pi)

def CalcRad(lat):
    "Radius of curvature in meters at specified latitude."
    a = 6378.137
    e2 = 0.081082 * 0.081082
    # the radius of curvature of an ellipsoidal Earth in the plane of a
    # meridian of latitude is given by
    #
    # R' = a * (1 - e^2) / (1 - e^2 * (sin(lat))^2)^(3/2)
    #
    # where a is the equatorial radius,
    # b is the polar radius, and
    # e is the eccentricity of the ellipsoid = sqrt(1 - b^2/a^2)
    #
    # a = 6378 km (3963 mi) Equatorial radius (surface to center distance)
    # b = 6356.752 km (3950 mi) Polar radius (surface to center distance)
    # e = 0.081082 Eccentricity
    sc = math.sin(Deg2Rad(lat))
    x = a * (1.0 - e2)
    z = 1.0 - e2 * sc * sc
    y = pow(z, 1.5)
    r = x / y

    r = r * 1000.0	# Convert to meters
    return r

def EarthDistance((lat1, lon1), (lat2, lon2)):
    "Distance in meters between two points specified in degrees."
    x1 = CalcRad(lat1) * math.cos(Deg2Rad(lon1)) * math.sin(Deg2Rad(90-lat1))
    x2 = CalcRad(lat2) * math.cos(Deg2Rad(lon2)) * math.sin(Deg2Rad(90-lat2))
    y1 = CalcRad(lat1) * math.sin(Deg2Rad(lon1)) * math.sin(Deg2Rad(90-lat1))
    y2 = CalcRad(lat2) * math.sin(Deg2Rad(lon2)) * math.sin(Deg2Rad(90-lat2))
    z1 = CalcRad(lat1) * math.cos(Deg2Rad(90-lat1))
    z2 = CalcRad(lat2) * math.cos(Deg2Rad(90-lat2))
    a = (x1*x2 + y1*y2 + z1*z2)/pow(CalcRad((lat1+lat2)/2), 2)
    # a should be in [1, -1] but can sometimes fall outside it by
    # a very small amount due to rounding errors in the preceding
    # calculations (this is prone to happen when the argument points
    # are very close together).  Thus we constrain it here.
    if abs(a) > 1: a = 1
    elif a < -1: a = -1
    return CalcRad((lat1+lat2) / 2) * math.acos(a)

def isotime(s):
    "Convert timestamps in ISO8661 format to and from Unix time."
    if type(s) == type(1):
        return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(s))
    elif type(s) == type(1.0):
        date = int(s)
        msec = s - date
        date = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(s))
        return date + "." + `msec`[2:]
    elif type(s) == type(""):
        if s[-1] == "Z":
            s = s[:-1]
        if "." in s:
            (date, msec) = s.split(".")
        else:
            date = s
            msec = "0"
        # Note: no leap-second correction! 
        return calendar.timegm(time.strptime(date, "%Y-%m-%dT%H:%M:%S")) + float("0." + msec)
    else:
        raise TypeError

class InvalidGPX(Exception): pass

def calculate(gpx):
    doc = minidom.parseString(gpx)
    trk = doc.getElementsByTagName("trk")
    if [] == trk:
        raise InvalidGPX("No <trk> element in data")
    elif len(trk) > 1:
        raise InvalidGPX("More than one <trk> element in data")
    trk = trk[0]

    dist = 0.0
    trkpts = trk.getElementsByTagName("trkpt")
    before = trkpts[0]

    def coord(pt, name):
        return float(pt.attributes[name].value)
    
    for pt in trkpts[1:]:
        dist+=EarthDistance((coord(before, "lat"), coord(before, "lon")),
                            (coord(pt, "lat"), coord(pt, "lon")))
        before = pt
    return dist
        
    
    
if __name__ == "__main__":
    print calculate(open(sys.argv[1]).read())
    


