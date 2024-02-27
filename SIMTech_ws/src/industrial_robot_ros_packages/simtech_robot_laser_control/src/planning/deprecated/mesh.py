import os
import re
import time
import struct
import numpy as np

import calculate as calc
import polyline as poly
from devmap import Rays, DevMap

from shapely import geometry, ops

class Mesh:
    def __init__(self, filename):
        self.origin = np.array([.0, .0, .0])
        # Bounding box
        self.position = np.array([.0, .0, .0])
        self.size = np.array([.0, .0, .0])
        # Mesh loading routine
        self.triangles = []
        self.normals = []
        self.devmap = DevMap()
        self.rays = Rays()
        self.min_z_repair = 0
        if self.load_text_mesh(filename) or self.load_binary_mesh(filename):
            self.bounding_box()
            self.resort_triangles()  # Only for calculation
            self.name = os.path.basename(filename)
            self.color = (1.0, 1.0, 0)

    def load_binary_mesh(self, filename):
        try:
            with open(filename, 'rb') as f:
                data = f.read(84)  # skip header
                while data != '':
                    normal_strings = [f.read(4), f.read(4), f.read(4)]
                    if normal_strings[2] != '':
                        normal = [struct.unpack('f', normal_strings[0])[0],
                                  struct.unpack('f', normal_strings[1])[0],
                                  struct.unpack('f', normal_strings[2])[0]]
                        self.normals.append(normal)
                        tri = np.zeros((3, 3))
                        for j in range(3):
                            for i in range(3):
                                data = f.read(4)
                                tri[j, i] = struct.unpack('f', data)[0]
                    else:
                        break
                    data = f.read(2)  # skip the attribute bytes
                    self.triangles.append(tri)
            print "Loaded binary STL:", filename
        except:
            print "Unable to load binary STL"
            return False
        return True

    def load_text_mesh(self, filename):
        template = " *facet normal +(?P<xn>.+) (?P<yn>.+) (?P<zn>.+)\n"
        template += " *outer loop\n"
        template += " *vertex +(?P<x1>.+) (?P<y1>.+) (?P<z1>.+)\n"
        template += " *vertex +(?P<x2>.+) (?P<y2>.+) (?P<z2>.+)\n"
        template += " *vertex +(?P<x3>.+) (?P<y3>.+) (?P<z3>.+)\n"
        template += " *endloop\n"
        template += " *endfacet\n"
        try:
            with open(filename, 'r') as f:
                lines = f.read()
            pattern = re.compile(template, re.MULTILINE)
            results = pattern.findall(lines)
            if results:
                for xn, yn, zn, x1, y1, z1, x2, y2, z2, x3, y3, z3 in results:
                    tri = np.array([[float(x1), float(y1), float(z1)],
                                    [float(x2), float(y2), float(z2)],
                                    [float(x3), float(y3), float(z3)]])
                    self.triangles.append(tri)
            else:
                return False
            print "Loaded binary STL:", filename
        except:
            print "Unable to load text STL"
            return False
        return True

    def load_deviation(self, filename):
        self.devmap.triangles_coords = self.triangles
        self.devmap.normals = self.normals
        self.devmap.load_deviation(filename)
        self.calculate_vectors()
        self.calculate_shift_triangles()

    def calculate_vectors(self):
        self.devmap.calculate_vectors()

    def calculate_shift_triangles(self):
        self.devmap.calculate_shift_triangles()
        self.min_z_repair = np.array(self.devmap.shift_triangles)[:, :, 2].min()
        print 'Zmin to repair: ' + str(self.min_z_repair)
        print 'triangels:'
        print np.array(self.devmap.shift_triangles)
        print 'list'
        print self.devmap.shift_triangles
        self.rays.load_triangles(self.devmap.shift_triangles, delaunay=True)

    def save_stl(self, filename):
        self.devmap.save_stl(filename)

    def divide_segment(self, segment):
        return self.rays.divide_segment(segment)

    def bounding_box(self):
        b1 = [10000, 10000, 10000]
        b2 = [-10000, -10000, -10000]
        for tri in self.triangles:
            for k in range(3):
                for j in range(3):
                    if tri[k, j] < b1[j]:
                        b1[j] = tri[k, j]
                    if tri[k, j] > b2[j]:
                        b2[j] = tri[k, j]
        bpnt1, bpnt2 = np.array(b1), np.array(b2)
        self.position = bpnt1
        self.size = bpnt2 - bpnt1

    def translate(self, point):
        trans = point - self.origin
        for k, tri in enumerate(self.triangles):
            self.triangles[k] = tri + trans
        self.origin = point
        self.bounding_box()
        self.resort_triangles()

    def scale(self, scale):
        for k, tri in enumerate(self.triangles):
            self.triangles[k] = ((tri - self.position) * scale) + self.position
        self.bounding_box()
        self.resort_triangles()

    def resort_triangles(self):
        """Sorts vertices from smaller to greater Z."""
        # Sorting the triangle according to height makes slicing then easier
        self.ctriangles = list(self.triangles)
        for k, tri in enumerate(self.triangles):
            self.ctriangles[k] = tri[tri[:, 2].argsort()]

    def get_range_values(self, v_min, v_max, v_dist):
        n_vals = np.round(((v_max - v_min) + v_dist) / v_dist)
        i_min = ((v_max + v_min) - (n_vals * v_dist)) / 2
        i_max = ((v_max + v_min) + (n_vals * v_dist)) / 2
        return np.arange(i_min, i_max + v_dist, v_dist)

    def get_zlevels(self, zdist, zmin=None, zmax=None):
        if zmin is None and zmax is None:
            zmin, zmax = self.position[2], (self.position + self.size)[2]
        if self.min_z_repair > 0:
            zmin = self.min_z_repair
        print 'Zmin, Zmax:', zmin, zmax
        n_vals = np.round((zmax - zmin) / zdist)
        i_min = zmin #((zmax + zmin) - (n_vals * zdist)) / 2
        i_max = ((zmax + zmin) + (n_vals * zdist)) / 2
        return np.arange(i_min, i_max, zdist) + 0.001

    def get_z_intersect(self, triangle, z_level):
        """Gets the intersection line of the plane in Z with the triangle."""
        # Returns None if the triangle does not intersect.
        point1, point2, point3 = triangle
        (x1, y1, z1), (x2, y2, z2), (x3, y3, z3) = point1, point2, point3
        intersect = None
        if z1 == z_level == z2:
            intersect = np.array([[x1, y1, z_level],
                                      [x2, y2, z_level]])
        elif z3 == z_level == z2:
            intersect = np.array([[x2, y2, z_level],
                                      [x3, y3, z_level]])
        elif z1 < z_level:
            dx21, dy21, dz21 = point2 - point1
            dx31, dy31, dz31 = point3 - point1
            dx32, dy32, dz32 = point3 - point2
            if z2 > z_level:
                xa = x1 + dx21 * (z_level - z1) / dz21
                ya = y1 + dy21 * (z_level - z1) / dz21
                if z3 > z_level:
                    xb = x1 + dx31 * (z_level - z1) / dz31
                    yb = y1 + dy31 * (z_level - z1) / dz31
                else:
                    xb = x2 + dx32 * (z_level - z2) / dz32
                    yb = y2 + dy32 * (z_level - z2) / dz32
                intersect = np.array([[xa, ya, z_level],
                                      [xb, yb, z_level]])
            elif z3 > z_level:
                xa = x1 + dx31 * (z_level - z1) / dz31
                ya = y1 + dy31 * (z_level - z1) / dz31
                xb = x2 + dx32 * (z_level - z2) / dz32
                yb = y2 + dy32 * (z_level - z2) / dz32
                intersect = np.array([[xa, ya, z_level],
                                      [xb, yb, z_level]])
        return intersect

    def get_roll_point(self, polygon):
        roll_point = 0
        xy_dist = np.linalg.norm(polygon[0])
        for i, point in enumerate(polygon):
            d = np.linalg.norm(point)
            if d < xy_dist:
                roll_point = i
                xy_dist = d
        return roll_point

    def get_slice(self, z_level):
        """Calculates the polygons in the slice for a plane."""
        unsorted_lines = []
        local_ctriangles = self.ctriangles
        for triangle in local_ctriangles:
            if (triangle[0, 2] == z_level) and (triangle[2, 2] == z_level):
                print "WARNING: Triangle in z_level!"
            elif triangle[0, 2] < z_level < triangle[2, 2]:
                intersection = self.get_z_intersect(triangle, z_level)
                unsorted_lines.append(intersection)
            elif triangle[1, 2] == z_level:
                intersection = self.get_z_intersect(triangle, z_level)
                unsorted_lines.append(intersection)
        doubles = 0
        for n_line in range(len(unsorted_lines)):
            unsorted_lines[n_line] = np.round(unsorted_lines[n_line],5)
            if np.array_equal(unsorted_lines[n_line][0], unsorted_lines[n_line][1]):
                doubles = doubles +1
        if doubles > 0:
            print 'WARNING: Puntos dobles detectados'
        if not unsorted_lines == []:
            # Arrange the line segments so that each segment leads to the
            # nearest available segment. This is accomplished by using two
            # list of lines, and at each step moving the nearest available
            # line segment from the unsorted pile to the next slot in the
            # sorted pile.
            lines = []
            for line in unsorted_lines:
                lines.append(geometry.LineString(line))
            multiline = geometry.MultiLineString(lines)
            merged_line = ops.linemerge(multiline)
            polygons = []
            try:
                for merged in merged_line:
                    polygons.append(np.array(merged))
            except TypeError:
                # If there is only one contour
                polygons.append(np.array(merged_line))
            # for i, polygon in enumerate(polygons):
            #     roll_point = self.get_roll_point(polygon)
            #     if roll_point != 0:
            #         polygons[i] = polygon[roll_point:] + polygon[:roll_point]
            #     print 'Roll point: ' + str(roll_point)
            return [poly.filter_polyline(polygon, dist=0.05) for polygon in polygons]  # Polygons filter
        else:
            return None

    def get_mesh_slices(self, layer_height):
        #t0 = time.time()
        slices = []
        self.resort_triangles()
        levels = self.get_zlevels(layer_height)
        for z_level in levels:
            slices.append(self.get_slice(z_level))
            #t1 = time.time()
            #print '[%.2f%%] Time to slice at %.1fmm %.3f s.' % ((100.0 * (k + 1)) / len(levels), z_level, t1 - t0)
        return slices


if __name__ == '__main__':
    import argparse
    from mlabplot import MPlot3D

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data', type=str,
                        default='../../data/piece7.stl',
                        help='path to input stl data file')
    args = parser.parse_args()
    filename = args.data

    # Triangle mesh is composed by a set of faces (triangles)
    mesh = Mesh(filename)
    mesh.resort_triangles()

    t0 = time.time()
    slice = mesh.get_slice(0.7)
    t1 = time.time()
    print 'Time for slice:', t1 - t0

    slices = mesh.get_mesh_slices(0.5)

    mplot3d = MPlot3D()
    mplot3d.draw_mesh(mesh)
    mplot3d.draw_slice(slice)
    mplot3d.draw_slices(slices)
    mplot3d.show()
