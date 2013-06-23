import os
import math
from itertools import chain, izip

from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.listview import SelectableView
from kivy.properties import DictProperty
from kivy.properties import ListProperty
from kivy.properties import NumericProperty
from kivy.properties import OptionProperty
from kivy.properties import ObjectProperty

from kivy.graphics import Line

from kivy.lang import Builder

Builder.load_file(str(os.path.join(os.path.dirname(__file__), 'graphics.kv')))

# Abbreviation used in this file: cp == connection point

# TODO: Why use .1 margins on the unit cell for shape unit coordinates? The
#       margin for shapes can be handled in the drawing, eh? (And would not
#       be hard-coded, hey).


def cartesian_distance(x1, y1, x2, y2):
    '''Cartesian distance formula
    From:

      ftp://lnnr.lummi-nsn.gov/GIS_Scripts/CreatePointsAlongALine/DivideLine.py

    which has a print line with:

      "A Two-Bit Algorithms product
      Copyright 2011 Gerry Gabrisch
      gerry@gabrisch.us"

      (Code link: ftp://lnnr.lummi-nsn.gov/GIS_Scripts/)
    '''

    return float(math.pow(((math.pow((x2 - x1), 2)) +
                 (math.pow((y2 - y1), 2))), .5))


def cartesian_to_polar(xy1, xy2):
    '''
    From:

      ftp://lnnr.lummi-nsn.gov/GIS_Scripts/CreatePointsAlongALine/DivideLine.py

    which has a print line with:

      "A Two-Bit Algorithms product
      Copyright 2011 Gerry Gabrisch
      gerry@gabrisch.us"

    (Code link: ftp://lnnr.lummi-nsn.gov/GIS_Scripts/)

    Given coordinate pairs as two lists or tuples, return the polar
    coordinates with theta in radians. Values are in true radians along the
    unit-circle, for example, 3.14 and not -0 like a regular python
    return.'''
    try:
        x1, y1, x2, y2 = \
                float(xy1[0]), float(xy1[1]), float(xy2[0]), float(xy2[1])
        xdistance, ydistance = x2 - x1, y2 - y1
        distance = math.pow(((math.pow((x2 - x1), 2)) +
                            (math.pow((y2 - y1), 2))), .5)
        if xdistance == 0:
            if y2 > y1:
                theta = math.pi / 2
            else:
                theta = (3 * math.pi) / 2
        elif ydistance == 0:
            if x2 > x1:
                theta = 0
            else:
                theta = math.pi
        else:
            theta = math.atan(ydistance / xdistance)
            if xdistance > 0 and ydistance < 0:
                theta = 2 * math.pi + theta
            if xdistance < 0 and ydistance > 0:
                theta = math.pi + theta
            if xdistance < 0 and ydistance < 0:
                theta = math.pi + theta
        return [distance, theta]
    except:
        print"Error in cartesian_to_polar()"


def polar_to_cartesian(polarcoords):
    '''
    From:

      ftp://lnnr.lummi-nsn.gov/GIS_Scripts/CreatePointsAlongALine/DivideLine.py

    which has a print line with:

      "A Two-Bit Algorithms product
      Copyright 2011 Gerry Gabrisch
      gerry@gabrisch.us"

    (Code link: ftp://lnnr.lummi-nsn.gov/GIS_Scripts/)

    A tuple, or list, of polar values(distance, theta in radians)are
    converted to cartesian coords'''
    r = polarcoords[0]
    theta = polarcoords[1]
    x = r * math.cos(theta)
    y = r * math.sin(theta)
    return [x, y]


class ConnectionPoint(Widget):

    shapes = ListProperty()

    def __init__(self, **kwargs):
        super(ConnectionPoint, self).__init__(**kwargs)

    def can_connect(self, shape):
        if not shape in self.shapes:
            return True
        return False

    def connect(self, shape):
        if self.can_connect(shape):
            self.shapes.append(shape)
        shape.connect(self)


class Shape(SelectableView, Widget):

    shape = ObjectProperty()

    stroke_width = NumericProperty(2.0)
    stroke_color = ListProperty([0, 0, 0, 0])
    fill_color = ListProperty([0, 0, 0, 0])

    x = NumericProperty(10.0)
    y = NumericProperty(10.0)
    width = NumericProperty(10.0)
    height = NumericProperty(10.0)

    edit_button = ObjectProperty(None)

    def __init__(self, **kwargs):

        super(Shape, self).__init__(**kwargs)

        self.size_hint = (None, None)

        self.bind(is_selected=self.selection_changed)

    def selection_changed(self, *args):

        if self.is_selected:

            c = self.center()

            self.edit_button = Button(
                    pos=(c[0] + 5, c[1] - 5),
                    size=(10, 10),
                    text='E')

            self.add_widget(self.edit_button)

        else:

            self.remove_widget(self.edit_button)

    def center(self):
        pass
        #return self.x + (self.width / 2.0), self.y + (self.height / 2.0)


class ConnectedShape(Shape):

    connection_points = ListProperty([])
    connections = ListProperty([])

    def __init__(self, **kwargs):

        super(ConnectedShape, self).__init__(**kwargs)

    def generate_connection_points(self, step_distance=10):
        pass

    def find_connection(self, shape):
        pass

    def adjust_connections(self, dx, dy):
        for connection in self.connections:
            connection.adjust(self, dx, dy)


class LabeledShape(ConnectedShape):

    label = ObjectProperty()

    label_placement = OptionProperty('constrained',
                                     options=('freeform', 'constrained'))

    # label_containment is either ``inside`` or ``outside`` the element.
    label_containment = OptionProperty('inside', options=('inside', 'outside'))

    # label_anchor is the anchor position chosen from the available set of
    # locations in the inside_label_anchor_points or
    # outside_label_anchor_points dicts.
    label_anchor = OptionProperty('center', options=('center', 'top_middle',
        'bottom_middle', 'left_middle', 'right_middle', 'nw_corner',
        'ne_corner', 'se_corner', 'sw_corner'))

    # label_anchor_points is a list of texture locations specific to the given
    # shape used. For example, if a triangular shape is used, this list would
    # be set to appropriate (x, y, halign, valign) values within the unit
    # texture space, for each of the possible label locations. There are two
    # sets, one for locations inside the shape, one for those outside.
    label_data = DictProperty({
        'in_center': (0.5, 0.5, 'center', 'middle'),
        'in_top_middle': (0.5, 0.5, 'center', 'middle'),
        'in_bottom_middle': (0.5, 0.5, 'center', 'middle'),
        'in_left_middle': (0.5, 0.5, 'center', 'middle'),
        'in_right_middle': (0.5, 0.5, 'center', 'middle'),
        'in_nw_corner': (0.5, 0.5, 'center', 'middle'),
        'in_ne_corner': (0.5, 0.5, 'center', 'middle'),
        'in_se_corner': (0.5, 0.5, 'center', 'middle'),
        'in_sw_corner': (0.5, 0.5, 'center', 'middle'),

        'out_center': (0.5, 0.5, 'center', 'middle'),
        'out_top_middle': (0.5, 0.5, 'center', 'middle'),
        'out_bottom_middle': (0.5, 0.5, 'center', 'middle'),
        'out_left_middle': (0.5, 0.5, 'center', 'middle'),
        'out_right_middle': (0.5, 0.5, 'center', 'middle'),
        'out_nw_corner': (0.5, 0.5, 'center', 'middle'),
        'out_ne_corner': (0.5, 0.5, 'center', 'middle'),
        'out_se_corner': (0.5, 0.5, 'center', 'middle'),
        'out_sw_corner': (0.5, 0.5, 'center', 'middle')})

    label_offset = ListProperty([0.0, 0.0])

    def __init__(self, **kwargs):

        super(LabeledShape, self).__init__(**kwargs)

        if 'label' in kwargs:
            self.label.text = kwargs['label']

        if self.label_placement == 'freeform':
            if 'label_offset' in kwargs:
                self.label_offset = kwargs['label_offset']
            else:
                self.label_offset = [0.0, 0.0]
        else:
            label_key = "{0}{1}".format(
                    'in_' if self.label_containment == 'inside' else 'out_',
                    self.label_anchor)

            x_multiplier, y_multiplier, halign, valign = \
                    self.label_data[label_key]

            self.label.halign = halign
            self.label.valign = valign

            if halign == 'left':
                self.label_offset = [
                        self.size[0] * x_multiplier,
                        self.size[1] * y_multiplier]
            elif halign == 'center':
                self.label_offset = [
                        (self.size[0] * x_multiplier) - int(self.width / 2.),
                        self.size[1] * y_multiplier]
            elif halign == 'right':
                self.label_offset = [
                        (self.size[0] * x_multiplier) - self.width,
                        self.size[1] * y_multiplier]


class LabeledVectorShape(LabeledShape):

    points = ListProperty([])
    unit_circle_points = ListProperty([])
    cp_slices_for_edges = ListProperty([])

    def __init__(self, **kwargs):
        super(LabeledVectorShape, self).__init__(**kwargs)

        self.bind(size=self.recalculate_points)

    def shift_unit_circle_points_to_origin(self):

        x_values = self.unit_circle_points[::2]
        y_values = self.unit_circle_points[1::2]

        min_x = min(x_values)
        min_y = min(y_values)

        min_x = 0 if min_x > 0 else min_x * -1.

        min_y = 0 if min_y > 0 else min_y * -1.

        return list(chain.from_iterable(izip([x + min_x for x in x_values],
                                             [y + min_y for y in y_values])))

    def recalculate_points(self, *args):
        pass

    # http://stackoverflow.com/...
    #   questions/849211/shortest-distance-between-a-point-and-a-line-segment
    def dist(self, x1, y1, x2, y2, x3, y3):  # x3,y3 is the point
        px = x2 - x1
        py = y2 - y1

        something = px * px + py * py

        u = ((x3 - x1) * px + (y3 - y1) * py) / float(something)

        if u > 1:
            u = 1
        elif u < 0:
            u = 0

        x = x1 + u * px
        y = y1 + u * py

        dx = x - x3
        dy = y - y3

        # Note: If the actual distance does not matter,
        # if you only want to compare what this function
        # returns to other results of this function, you
        # can just return the squared distance instead
        # (i.e. remove the sqrt) to gain a little performance

        dist = math.sqrt(dx * dx + dy * dy)

        return dist

    def point_on_polygon(self, x, y, min_dist):
        x, y = self.to_local(x, y)
        poly = self.points

        n = len(poly)
        p1x = poly[0]
        p1y = poly[1]

        for i in xrange(2, n + 2, 2):
            p2x = poly[i % n]
            p2y = poly[(i + 1) % n]

            dist = self.dist(p1x, p1y, p2x, p2y, x, y)
            print '    distance', dist, p1x, p1y, '-->', p2x, p2y
            if dist < min_dist:
                return True
            p1x, p1y = p2x, p2y

        return False

    def closest_edge(self, x, y):
        x, y = self.to_local(x, y)
        poly = self.points

        n = len(poly)
        p1x = poly[0]
        p1y = poly[1]

        # edge here is the index into poly.

        minimum_and_edge = [100000, 0]

        for i in xrange(2, n + 2, 2):
            p2x = poly[i % n]
            p2y = poly[(i + 1) % n]

            dist = self.dist(p1x, p1y, p2x, p2y, x, y)
            print '        possible distance', dist, p1x, p1y, '-->', p2x, p2y
            if dist < minimum_and_edge[0]:
                minimum_and_edge = [dist, i]
            p1x, p1y = p2x, p2y

        return minimum_and_edge

    def point_inside_polygon(self, x, y, poly):
        '''Taken from http://www.ariel.com.au/a/python-point-int-poly.html
        '''
        n = len(poly)
        inside = False
        p1x = poly[0]
        p1y = poly[1]

        for i in xrange(2, n + 2, 2):

            p2x = poly[i % n]
            p2y = poly[(i + 1) % n]

            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = \
                                    (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside

            p1x, p1y = p2x, p2y

        return inside

    def collide_point(self, x, y):
        x, y = self.to_local(x, y)
        return self.point_inside_polygon(x, y, self.points)

    def center(self):
        x_values = self.points[::2]
        y_values = self.points[1::2]

        min_x = min(x_values)
        max_x = max(x_values)
        min_y = min(y_values)
        max_y = max(y_values)

        return (self.pos[0] + ((max_x - min_x) / 2.),
                self.pos[1] + ((max_y - min_y) / 2.))

    def generate_connection_points(self, step_distance=10):
        poly = self.points

        n = len(poly)
        x1 = poly[0]
        y1 = poly[1]

        self.connection_points.append([x1, y1])

        distance_remaining = []

        # Reference:
        #
        # A Two-Bit Algorithms product
        # Copyright 2011 Gerry Gabrisch
        # gerry@gabrisch.us"
        #
        # http://forums.arcgis.com/threads/9118- ...
        #   Placing-points-automatically-along-line-based-on-length-attribute
        # (Code link: ftp://lnnr.lummi-nsn.gov/GIS_Scripts/)

        step_distance = float(step_distance)

        counter = 0

        for i in xrange(2, n + 2, 2):
            x2 = poly[i % n]
            y2 = poly[(i + 1) % n]

            try:
                distance_along_line = cartesian_distance(x1, y1, x2, y2) + \
                                      distance_remaining[counter - 1]
            except:
                distance_along_line = cartesian_distance(x1, y1, x2, y2)

            if distance_along_line == step_distance:

                # If the line segment is short, matching exactly the
                # step_distance, we only need to store the start and end of the
                # line segment as a single point (there is only one connection
                # point -- the end of the line segment, which we add first).

                self.connection_points.append([x2, y2])
                self.cp_slices_for_edges.append(
                        (len(self.connection_points) - 1,
                         len(self.connection_points) - 1))
                distance_remaining.append(0)

            elif distance_along_line > step_distance:

                # If the line segment is longer than step_distance, there are
                # connection points along the line segment. We create these
                # points and set the start and end indices.

                number_divisions = int(distance_along_line / step_distance)
                distance_remaining.append(
                    distance_along_line - (number_divisions * step_distance))
                polarcoord = cartesian_to_polar((x1, y1), (x2, y2))

                cps_start_index = len(self.connection_points)

                counter2 = 1
                while counter2 <= number_divisions:
                    if len(distance_remaining) > 1:
                        adjustment = polar_to_cartesian([
                            ((step_distance * counter2) -
                                    distance_remaining[counter - 1]),
                            polarcoord[1]])
                    else:
                        adjustment = polar_to_cartesian([
                            ((step_distance * counter2)),
                            polarcoord[1]])
                    self.connection_points.append(
                            [x1 + adjustment[0], y1 + adjustment[1]])
                    counter2 += 1

                cps_end_index = len(self.connection_points) - 1

                self.cp_slices_for_edges.append(
                        (cps_start_index, cps_end_index))

            elif distance_along_line < step_distance:

                # If the distance along the line segment is shorter than the
                # step_distance, store the short remainder distance for use in
                # the next line segment's calculations.

                if len(distance_remaining) < 1:
                    distance_remaining.append(distance_along_line)
                else:
                    distance_remaining.append(distance_along_line)

            x1, y1 = x2, y2

    def closest_cp_to_center_line(self, shape2):
        '''Return the index of the closest cp to the center line between self
        and shape2.
        '''

        center1 = self.center()
        center2 = shape2.center()

        min_distance = 100000.

        for i, cp in enumerate(self.connection_points):

            dist = self.dist(
                    center1[0], center1[1], center2[0], center2[1],
                    cp[0], cp[1])

            if dist < min_distance:
                min_distance = dist
                closest_cp = i

        return closest_cp

        #for point in self.connection_points:
        #    if (point.pos[0]
        #          < shape.label.pos[0] and
        #        point.pos[0]
        #          > shape.label.pos[0] + shape.label.texture.size[0] and
        #        point.pos[1]
        #          < shape.label.pos[1] and
        #        point.pos[1]
        #          > shape.label.pos[1] + shape.label.texture.size[1]):
        #        print point

    def draw_connection_points(self):
        for cp in self.connection_points:
            Line(circle=(cp[0], cp[1], 5))

    def draw_connection_point(self, index):
        cp = self.connection_points[index]
        Line(circle=(cp[0], cp[1], 5))


class ConnectionLVS(LabeledVectorShape):
    shape = ListProperty([.9, .9])
    shape1 = ObjectProperty(None)
    shape2 = ObjectProperty(None)
    shape1_cp_index = NumericProperty()
    shape2_cp_index = NumericProperty()

    def __init__(self, **kwargs):

        super(LabeledVectorShape, self).__init__(**kwargs)

        if 'text' in kwargs:
            self.label.text = kwargs['text']
        else:
            self.label.text = 'unknown'

        self.points.append(
                self.shape1.connection_points[self.shape1_cp_index][0])
        self.points.append(
                self.shape1.connection_points[self.shape1_cp_index][1])
        self.points.append(
                self.shape2.connection_points[self.shape2_cp_index][0])
        self.points.append(
                self.shape2.connection_points[self.shape2_cp_index][1])

    def on_touch_down(self, touch):
        print 'connection touch', touch.pos
        return super(LabeledVectorShape, self).on_touch_down(touch)

    def adjust(self, shape, dx, dy):
        connection_point1 = self.shape1.connection_points[self.shape1_cp_index]
        self.pos[0] = connection_point1[0]
        self.pos[1] = connection_point1[1]

        if shape == self.shape1:
            self.x += dx
            self.y += dy

        self.points[0] = self.pos[0]
        self.points[1] = self.pos[1]

        connection_point2 = self.shape2.connection_points[self.shape2_cp_index]

        self.width = connection_point2[0] - connection_point1[0]
        self.height = connection_point2[1] - connection_point1[1]

        self.points[2] = self.pos[0] + self.width
        self.points[3] = self.pos[1] + self.height

        self.size = (self.width, self.height)

    def recalculate_points(self, *args):

        # needed?

        self.points[0] = self.pos[0] + int(float(self.size[0]) * self.shape[0])
        self.points[1] = self.pos[1] + int(float(self.size[1]) * self.shape[1])

    def connection_point1(self):
        return self.shape1.connection_points[self.shape1_cp_index]

    def connection_point2(self):
        return self.shape2.connection_points[self.shape2_cp_index]

    def bump_connection_point1(self):

        old_connection_point = \
                self.shape1.connection_points[self.shape1_cp_index]

        if self.shape1_cp_index < len(self.shape1.connection_points) - 1:
            self.shape1_cp_index += 1
        else:
            self.shape1_cp_index = 0

        new_connection_point = \
                self.shape1.connection_points[self.shape1_cp_index]

        dx = new_connection_point[0] - old_connection_point[0]
        dy = new_connection_point[1] - old_connection_point[1]

        self.adjust(self.shape1, dx, dy)

    def bump_connection_point2(self):

        old_connection_point = \
                self.shape2.connection_points[self.shape2_cp_index]

        if self.shape2_cp_index < len(self.shape2.connection_points) - 1:
            self.shape2_cp_index += 1
        else:
            self.shape2_cp_index = 0

        new_connection_point = \
                self.shape2.connection_points[self.shape2_cp_index]

        dx = new_connection_point[0] - old_connection_point[0]
        dy = new_connection_point[1] - old_connection_point[1]

        self.adjust(self.shape2, dx, dy)


class TriangleLVS(LabeledVectorShape):
    points = ListProperty([0] * 6)
    unit_circle_points = ListProperty([0, 1., .866, -.5, -.866, -.5])

    def __init__(self, **kwargs):
        super(TriangleLVS, self).__init__(**kwargs)

        self.recalculate_points()

    def recalculate_points(self, *args):

        self.unit_circle_points = self.shift_unit_circle_points_to_origin()

        self.points[0] = self.pos[0] + int(float(self.size[0]) * self.unit_circle_points[0])
        self.points[1] = self.pos[1] + int(float(self.size[1]) * self.unit_circle_points[1])
        self.points[2] = self.pos[0] + int(float(self.size[0]) * self.unit_circle_points[2])
        self.points[3] = self.pos[1] + int(float(self.size[1]) * self.unit_circle_points[3])
        self.points[4] = self.pos[0] + int(float(self.size[0]) * self.unit_circle_points[4])
        self.points[5] = self.pos[1] + int(float(self.size[1]) * self.unit_circle_points[5])


class RectangleLVS(LabeledVectorShape):
    points = ListProperty([0] * 8)
    unit_circle_points = ListProperty([-.707, .707, .707, .707, .707, -.707, -.707, -.707])

    def __init__(self, **kwargs):
        super(RectangleLVS, self).__init__(**kwargs)

        self.recalculate_points()

    def recalculate_points(self, *args):

        self.unit_circle_points = self.shift_unit_circle_points_to_origin()

        self.points[0] = self.pos[0] + int(float(self.size[0]) * self.unit_circle_points[0])
        self.points[1] = self.pos[1] + int(float(self.size[1]) * self.unit_circle_points[1])
        self.points[2] = self.pos[0] + int(float(self.size[0]) * self.unit_circle_points[2])
        self.points[3] = self.pos[1] + int(float(self.size[1]) * self.unit_circle_points[3])
        self.points[4] = self.pos[0] + int(float(self.size[0]) * self.unit_circle_points[4])
        self.points[5] = self.pos[1] + int(float(self.size[1]) * self.unit_circle_points[5])
        self.points[6] = self.pos[0] + int(float(self.size[0]) * self.unit_circle_points[6])
        self.points[7] = self.pos[1] + int(float(self.size[1]) * self.unit_circle_points[7])


class PentagonLVS(LabeledVectorShape):
    points = ListProperty([0] * 10)

    # For pentagon vertex coordinates calculation, see:
    #
    #     http://www2.mae.ufl.edu/~uhk/NSIDED-POLYGONS.pdf
    #
    unit_circle_points = ListProperty([0,
                          1.,
                          math.sqrt(2. + 1.618033989) / 2.,
                          (1.618033989 - 1.) / 2.,
                          math.sqrt(3. - 1.818033989) / 2.,
                          (-1.618033989) / 2.,
                          (math.sqrt(3. - 1.818033989) / 2.) * -1.,
                          ((-1.618033989) / 2.),
                          (math.sqrt(2. + 1.618033989) / 2.) * -1,
                          (1.618033989 - 1.) / 2.])

    def __init__(self, **kwargs):
        super(PentagonLVS, self).__init__(**kwargs)

        self.recalculate_points()

    def recalculate_points(self, *args):

        self.unit_circle_points = self.shift_unit_circle_points_to_origin()

        self.points[0] = self.pos[0] + int(float(self.size[0]) * self.unit_circle_points[0])
        self.points[1] = self.pos[1] + int(float(self.size[1]) * self.unit_circle_points[1])
        self.points[2] = self.pos[0] + int(float(self.size[0]) * self.unit_circle_points[2])
        self.points[3] = self.pos[1] + int(float(self.size[1]) * self.unit_circle_points[3])
        self.points[4] = self.pos[0] + int(float(self.size[0]) * self.unit_circle_points[4])
        self.points[5] = self.pos[1] + int(float(self.size[1]) * self.unit_circle_points[5])
        self.points[6] = self.pos[0] + int(float(self.size[0]) * self.unit_circle_points[6])
        self.points[7] = self.pos[1] + int(float(self.size[1]) * self.unit_circle_points[7])
        self.points[8] = self.pos[0] + int(float(self.size[0]) * self.unit_circle_points[8])
        self.points[9] = self.pos[1] + int(float(self.size[1]) * self.unit_circle_points[9])


class LabeledImageShape(LabeledShape):
    def __init__(self, **kwargs):
        super(LabeledImageShape, self).__init__(**kwargs)

        if 'shape' in kwargs:
            self.shape.source = kwargs['shape']


class RectangleLIS(LabeledImageShape):
    pass


class CircleLIS(LabeledImageShape):

    radius = NumericProperty(5.0)

    def __init__(self, **kwargs):

        super(CircleLIS, self).__init__(**kwargs)

        if 'radius' in kwargs:
            self.radius = kwargs['radius']


class PointLIS(CircleLIS):

    def __init__(self, **kwargs):

        if not 'radius' in kwargs:
            kwargs['radius'] = 0.0

        super(PointLIS, self).__init__(**kwargs)

        if 'x' in kwargs:
            self.x = kwargs['x']

        if 'y' in kwargs:
            self.y = kwargs['y']


class LineLIS(LabeledImageShape):

    x1 = NumericProperty(0.0)
    y1 = NumericProperty(0.0)

    def __init__(self, **kwargs):

        super(LineLIS, self).__init__(**kwargs)

        if 'x1' in kwargs:
            self.x1 = kwargs['x1']
        if 'y1' in kwargs:
            self.y1 = kwargs['y1']


class TriangleLIS(LineLIS):

    x2 = NumericProperty(0.0)
    y2 = NumericProperty(0.0)

    def __init__(self, **kwargs):

        super(TriangleLIS, self).__init__(**kwargs)

        if 'x2' in kwargs:
            self.x2 = kwargs['x2']
        if 'y2' in kwargs:
            self.y2 = kwargs['y2']


class DiamondLIS(LineLIS):

    x3 = NumericProperty(0.0)
    y3 = NumericProperty(0.0)

    def __init__(self, **kwargs):

        super(DiamondLIS, self).__init__(**kwargs)

        if 'x3' in kwargs:
            self.x3 = kwargs['x3']
        if 'y3' in kwargs:
            self.y3 = kwargs['y3']


class PentagonLIS(DiamondLIS):

    x4 = NumericProperty(0.0)
    y4 = NumericProperty(0.0)

    def __init__(self, **kwargs):

        super(DiamondLIS, self).__init__(**kwargs)

        if 'x4' in kwargs:
            self.x4 = kwargs['x4']
        if 'y4' in kwargs:
            self.y4 = kwargs['y4']


class HexagonLIS(PentagonLIS):

    x5 = NumericProperty(0.0)
    y5 = NumericProperty(0.0)

    def __init__(self, **kwargs):

        super(HexagonLIS, self).__init__(**kwargs)

        if 'x5' in kwargs:
            self.x5 = kwargs['x5']
        if 'y5' in kwargs:
            self.y5 = kwargs['y5']
