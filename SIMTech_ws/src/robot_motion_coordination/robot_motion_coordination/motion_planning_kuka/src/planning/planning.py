import time
import numpy as np

import calculate as calc


class Planning:
    def __init__(self):
        # self.orientation = np.array((0.0, 0.0, 0.0, 1.0))
        self.orientation = np.array((0, 0.0, 0.0, 1))  # Cabezal de fio (-0.168924, 0.0, 0.0, 0.985627)
        self.printtest = True
        self.start_point = 'mid'
        self.start_point_dir = 'max'

    def get_range_values(self, v_min, v_max, v_dist):
        # Actualizar que o v_min empeze durante todo o proceso no mesmo valor
        '''n_vals = np.round(((v_max - v_min) + v_dist) / v_dist)
        i_min = ((v_max + v_min) - (n_vals * v_dist)) / 2
        i_max = ((v_max + v_min) + (n_vals * v_dist)) / 2'''
        # return np.arange(v_min - v_dist * 0.5, v_max + v_dist * 1.5, v_dist)
        return np.arange(v_max + v_dist * 0.5, v_min - v_dist * 0.5, -v_dist)

    def get_min_max(self, poly, degrees):
        '''Gets the outer points from a plygon crossed by a stright line'''
        m, b = None, None
        m, b = calc.line2d_angle((0, 0), degrees)
        dist_max = np.max([calc.line2d_point_distance(m, b, (point[0], point[1])) for point in poly])
        dist_min = np.min([calc.line2d_point_distance(m, b, (point[0], point[1])) for point in poly])
        return dist_min, dist_max

    def get_grated(self, slice, dist, one_dir=False, invert=False, degrees=0.0):
        dist = dist - 1e-9
        fill_lines = []
        if 0 > degrees > 180:
            degrees = degrees % 180
        if degrees == 90.0:
            degrees = degrees + 0.1
            #TODO: Correxir bug con 90 grados
        m, b = None, None
        m, b = calc.line2d_angle((0, 0), degrees)
        
        # p1 = np.array([0.0 , 0.0])
        # p2 = np.array([np.cos(np.radians(degrees)) , np.sin(np.radians(degrees))])

        # dist_max = np.max([np.max([np.linalg.norm(np.cross(p2-p1, p1-point[:2]))/np.linalg.norm(p2-p1) for point in poly]) for poly in slice])
        # dist_min = np.min([np.min([np.linalg.norm(np.cross(p2-p1, p1-point[:2]))/np.linalg.norm(p2-p1) for point in poly]) for poly in slice])

        dist_max = np.max([np.max([calc.line2d_point_distance(m, b, (point[0], point[1])) for point in poly]) for poly in slice])
        dist_min = np.min([np.min([calc.line2d_point_distance(m, b, (point[0], point[1])) for point in poly]) for poly in slice])
        
        wide_range = self.get_range_values(dist_min, dist_max, dist)
        if self.start_point == 'max':
            wide_range = np.flip(wide_range)
        elif self.start_point == 'mid':
            if len(wide_range) > 3:
                new_range =[len(wide_range)/2, len(wide_range)/2 - 1, len(wide_range)/2 + 1]
                up = True
                while len(new_range) < len(wide_range):
                    if up:
                        new_range.append(new_range[-2]-1)
                        up = False
                    else:
                        new_range.append(new_range[-2]+1)
                        up = True
                wide_range = wide_range[new_range]
        for x in wide_range:
            points = []
            m_, b_ = calc.parallel_line2d(m, b, x)
            for poly in slice:
                for k in range(len(poly)):
                    point = None
                    pnt1, pnt2 = poly[k - 1], poly[k]
                    d1 = calc.line2d_point_distance(m_, b_, (pnt1[0], pnt1[1]))
                    d2 = calc.line2d_point_distance(m_, b_, (pnt2[0], pnt2[1]))
                    if ((d1 > 0.0) != (d2 > 0.0)) or ((d1 == 0) != (d2 == 0)):
                        # Cortanse
                        my, by = calc.line2d((pnt1[0], pnt1[1]),
                                             (pnt2[0], pnt2[1]))
                        intersec_x, intersec_y = calc.line2d_intersec(m_, b_,
                                                                      my, by)
                        point = np.array([intersec_x, intersec_y, pnt1[2]])
                    elif (d1 == 0) and (d2 == 0):
                        # Coinciden
                        points.append(pnt1)
                        points.append(pnt2)
                    if point is not None:
                        points.append(point)
            if not points == []:
                points = np.array(points)
                if (85 < degrees  < 95):
                    indexes = np.argsort(points[:, 1])
                else:
                    indexes = np.argsort(points[:, 0])
                if len(indexes) % 2:
                    print 'ERROR!', len(indexes), 'tangent element finded'
                    indexes = indexes[:len(indexes)-1]
                if self.start_point_dir == 'min':
                    indexes = np.flip(indexes)
                fill_lines.append(points[indexes])
        i_lines = []
        for line in fill_lines:
            if invert:
                line = np.flipud(line)
            i_lines.append(line)
        if one_dir:
            return i_lines
        # Flips the array to start in the last point of the next line.
        # lines = []
        pair = False
        for line in range(len(i_lines)):
            if pair:
                i_lines[line] = np.flipud(i_lines[line])
            pair = not pair
            # lines.append(line)
        return i_lines

    def get_path_from_fill_lines_old(self, fill_lines):
        tool_path = []
        local_orientation = self.orientation
        for line in fill_lines:
            for k in range(0, len(line), 2):
                pnt1, pnt2 = line[k], line[k+1]
                if len(tool_path):
                    last_point = tool_path[-1][0]
                    if np.all(last_point == pnt1):
                        tool_path[-1] = [pnt2, local_orientation , False]
                    else:
                        tool_path.append([pnt1, local_orientation, True])
                        tool_path.append([pnt2, local_orientation, False])
                else:
                    tool_path.append([pnt1, local_orientation, True])
                    tool_path.append([pnt2, local_orientation, False])
        return tool_path

    def get_path_from_fill_lines(self, fill_lines):
        tool_path = []
        for track in fill_lines:
            if len(track) > 1:
                for k in range(0, len(track)-1):
                    tool_path.append([track[k], self.orientation, True])
                tool_path.append([track[-1], self.orientation, False])
        return tool_path

    def get_path_from_slices(self, slices, track_distance=None, pair=False, focus=0, one_dir=False, invert=False, degrees=None):
        #t0 = time.time()
        path = []
        local_orientation = self.orientation
        #pair = False
        for k, slice in enumerate(slices):
            if slice is not None:
                if track_distance is None:
                    for contour in slice:
#                    if len(slice) == 1:
#                        contour = slice[0]
#                    else:
#                        contour = slice[1]
                        for point in contour[:-1]:
                            path.append([point, local_orientation, True])
                        path.append([contour[-1], local_orientation, False])
                else:
                    fill_lines = self.get_grated(slice, track_distance, one_dir, invert, degrees)
                    #if self.start_point == 'max':
                    #    fill_lines.reverse()
                    if pair:  # Controls the starting point of the next layer
                        fill_lines.reverse()
                    pair = not pair
                    path.extend(self.get_path_from_fill_lines_old(fill_lines))
            #t1 = time.time()
            #print '[%.2f%%] Time to path %.3f s.' % (
            #    (100.0 * (k + 1)) / len(slices), t1 - t0)
        return self.translate_path(path, np.array([0, 0, focus]))

    def translate_path(self, path, position):
        return [(position + pnt, orient, proc) for (pnt, orient, proc) in path]

    def path_length(self, path):
        laser_dist, travel_dist = 0, 0
        for k, (point, orient, process) in enumerate(path[:-1]):
            dist = calc.distance(path[k][0], path[k+1][0])
            if process:
                laser_dist = laser_dist + dist
            else:
                travel_dist = travel_dist + dist
        return laser_dist, travel_dist

    def path_time(self, length, laser_speed, travel_speed):
        laser_dist, travel_dist = length
        time = laser_dist / laser_speed + travel_dist / travel_speed
        return time


if __name__ == '__main__':
    import argparse
    from mesh import Mesh
    from mlabplot import MPlot3D

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data', type=str,
                        default='/home/baltasar/Documentos/celda4/proper/tacos gnc/taco.stl',#/home/baltasar/Documentos/proper/points datapixel/P1DevMap/P1ModelDevMap.stl /home/baltasar/Documentos/celda4/proper/tacos gnc/taco.stl
                        help='path to input stl data file')
    args = parser.parse_args()
    filename = args.data

    # Triangle mesh is composed by a set of faces (triangles)
    mesh = Mesh(filename)
    mesh.resort_triangles()

    slice = mesh.get_slice(7.98)
    # t0 = time.time()
    # slices = mesh.get_mesh_slices(0.5)
    # t1 = time.time()
    # print 'Time for slices:', t1 - t0
    slices = []
    slices.append(slice)
    fp = slice[0][0]
    lp = slice[0][-1]

    planning = Planning()

    t0 = time.time()
    path = planning.get_path_from_slices(slices, 2.16, degrees=45.0)
    t1 = time.time()
    print 'Time for path:', t1 - t0

    import datetime
    length = planning.path_length(path)
    time = planning.path_time(length, 8, 50)
    print 'Laser distance:', length[0]
    print 'Travel distance:', length[1]
    print 'Estimated time:', str(datetime.timedelta(seconds=int(time)))

    # # Get path with frames
    # _path = []
    # for position, orientation, process in path:
    #    frame, t = calc.quatpose_to_pose(position, orientation)
    #    _path.append([position, frame, process])

    mplot3d = MPlot3D()
    #mplot3d.draw_mesh(mesh)
    mplot3d.draw_slices(slices)
    mplot3d.draw_path(path)
    mplot3d.show()
