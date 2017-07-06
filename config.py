#!/usr/bin/env python3
import argparse
import configparser
import json
import numpy
import random
import sys

from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, DataRange1d, Plot, LinearAxis, Grid
from bokeh.models.glyphs import Text
from scipy import ndimage

from nanoleaf import Aurora
from nanoleaf import setup

class AuroraWrapper(Aurora):
    def __init__(self, config):
        self.config = config
        super(AuroraWrapper, self).__init__(config['device']['ip'], config['device']['token'])

    @property
    def rotated_panel_positions(self):
        return json.loads(self.config['device']['panel_positions'])

    @property
    def rotation(self):
        return int(self.config['device']['rotation'])


def aurora():
    config = configparser.ConfigParser()
    config.read('aurora.ini')
    need_save = False

    if not 'device' in config:
        config['device'] = {}
        need_save = True

    if not 'ip' in config['device']:
        print('Finding device...')
        addrs = setup.find_auroras(seek_time=5)
        if addrs:
            config['device']['ip'] = addrs[0]
            need_save = True

    if 'ip' in config['device'] and not 'token' in config['device']:
        print('Authenticating...')
        config['device']['token'] = setup.generate_auth_token(config['device']['ip'])
        need_save = True

    a = AuroraWrapper(config)

    if not 'panel_positions' in config['device']:
        config['device']['rotation'] = '0'
        config['device']['panel_positions'] = json.dumps(a.panel_positions)
        need_save = True

    if need_save:
        config.write(open('aurora.ini', 'w'))
    return a


def __dump(label, image):
    """
    debug function I used to dump out images as I did rotation. keeping it around
    for now since I'm not 100% sure that rotation works as intended
    """
    print("== ", label)
    seen = {}
    for (y, x) in numpy.transpose(numpy.nonzero(image)):
        k = image[y][x]
        if k in seen:
            print("Dupe: %s at (%d, %d)" % (k, y, x))
        else:
            seen[k] = (y, x)
    print("Found: ", len(seen))
    for k in sorted(seen.keys()):
        v = seen[k]
        print("[%s] => (%d, %d)" % (k, v[0], v[1]))


def rotate(a, args):
    """
    Rotate panel layout by an arbitrary degree around the origin.
    """

    # Create a matrix that fits all panels and puts the origin at the center.
    # Downscale the matrix by 10x to reduce computation. Also scipy.ndimage.rotate
    # seems to have issues with large matrices where some elements get duplicated
    panels = {p['panelId']: p for p in a.panel_positions}
    for pid in panels:
        panels[pid]['x'] //= 10
        panels[pid]['y'] //= 10

    # calculate the max dimension of our bounding box, and make sure that our
    # resulting image can handle 2x the image size, in case we rotate 45 degrees
    dim = 2 * max([max(abs(p['x']), abs(p['y'])) for p in panels.values()])
    image = numpy.zeros(shape=(2 * dim, 2 * dim))

    # Put all panels in the matrix and rotate
    for (k, v) in panels.items():
        image[v['y'] + dim][v['x'] + dim] = k

    # Rotate
    r = args.rotate % 360
    rotated = ndimage.rotate(image, r, order=0, reshape=False)
    for (y, x) in numpy.transpose(numpy.nonzero(rotated)):
        p = panels[rotated[y][x]]
        p['x'] = int(x) - dim
        p['y'] = int(y) - dim
        p['o'] = (p['o'] + r) % 360

    # Cache the result for the future, along with the rotation we used
    config = configparser.ConfigParser()
    config.read('aurora.ini')
    config['device']['rotation'] = str(args.rotate % 360)
    config['device']['panel_positions'] = json.dumps(list(panels.values()))
    config.write(open('aurora.ini', 'w'))


def plot(a):
    panels = a.rotated_panel_positions
    x = [x['x'] for x in panels]
    y = [x['y'] for x in panels]
    ids = [x['panelId'] for x in panels]
    angles = [x['o'] for x in panels]

    pad_x = (max(x) - min(x)) * .1
    pad_y = (max(y) - min(y)) * .1
    output_file('plot.html')
    plot = figure(x_range=(min(x) - pad_x, max(x) + pad_x),
                  y_range=(min(y) - pad_y, max(y) + pad_y))
    source = ColumnDataSource(dict(x=x, y=y, text=ids))
    plot.triangle(x, y, angle=angles, angle_units='deg', size=70, color='#cccccc', fill_color=None, line_width=4)
    glyph = Text(x='x', y='y', text='text', angle=0, text_align='center', text_color='#FF0000')
    plot.add_glyph(source, glyph)
    show(plot)


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--plot', dest='plot', action='store_true')
    parser.add_argument('--on', dest='on_off', action='store_true')
    parser.add_argument('--off', dest='on_off', action='store_false')
    parser.add_argument('--brightness', dest='brightness', type=int, choices=range(0,100))
    parser.add_argument('--rotate', dest='rotate', type=int, choices=range(-360,360))
    args = parser.parse_args()

    a = aurora()
    if args.on_off != a.on:
        a.on = args.on_off

    if args.brightness is not None:
        a.brightness = args.brightness

    if args.rotate is not None:
        rotate(a, args)

    if args.plot:
        plot(a)


if __name__ == '__main__':
    main(sys.argv)
