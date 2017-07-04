#!/usr/bin/env python3
import sys
import random

from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, DataRange1d, Plot, LinearAxis, Grid
from bokeh.models.glyphs import Text

import configparser
import argparse
from nanoleaf import Aurora
from nanoleaf import setup

def aurora():
    config = configparser.ConfigParser()
    config.read('aurora.ini')

    if not 'device' in config:
        config['device'] = {}

    if not 'ip' in config['device']:
        print('Finding device...')
        addrs = setup.find_auroras(seek_time=5)
        if addrs:
            config['device']['ip'] = addrs[0]

    if 'ip' in config['device'] and not 'token' in config['device']:
        print('Authenticating...')
        config['device']['token'] = setup.generate_auth_token(config['device']['ip'])

    config.write(open('aurora.ini', 'w'))
    return Aurora(config['device']['ip'], config['device']['token'])


def plot(a):
    x = [x['x'] for x in a.panel_positions]
    y = [x['y'] for x in a.panel_positions]
    ids = [x['panelId'] for x in a.panel_positions]
    angles = [x['o'] for x in a.panel_positions]

    output_file('plot.html')
    plot = figure(x_range=(min(x)-100, max(x)+100), y_range=(min(y)-100,max(y)+100))

    source = ColumnDataSource(dict(x=x, y=y, text=ids))
    glyph = Text(x="x", y="y", text="text", angle=0, text_align='center', text_color='#96deb3')
    plot.add_glyph(source, glyph)
    plot.triangle(x, y, angle=angles, angle_units='deg', size=70, fill_color=None, line_width=4)

    show(plot)


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--plot', dest='plot', action='store_true')
    parser.add_argument('--on', dest='on_off', action='store_true')
    parser.add_argument('--off', dest='on_off', action='store_false')
    args = parser.parse_args()
    print(args)

    a = aurora()
    if args.on_off != a.on:
        a.on = args.on_off

    if args.plot:
        plot(a)



if __name__ == '__main__':
    main(sys.argv)
