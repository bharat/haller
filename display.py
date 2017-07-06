#!/usr/bin/env python3
import argparse
import random
import sys
import time

import config
from nanoleaf import Aurora

def streaming_random(a):
    panel_ids = [x['panelId'] for x in a.rotated_panel_positions]
    s = a.effect_stream()

    brt_delta = 2
    brt_max = 80
    brt_min = 20
    brt = int((brt_max + brt_min) / 2)
    while True:
        a.brightness = brt
        for p in panel_ids:
            s.panel_prepare(p, random.randint(0, 255), random.randint(0, 255), random.randint(0, 255),
                            transition_time=50)
        s.panel_strobe()
        # Aurora can only handle 10 updates a second.
        time.sleep(5)
        brt = brt + brt_delta
        if brt >= brt_max or brt <= brt_min:
            brt_delta = -brt_delta


def streaming_pulse(a):
    panel_ids = [x['panelId'] for x in a.rotated_panel_positions]
    s = a.effect_stream()


    for p in panel_ids:
        s.panel_prepare(p, 93, 100, 213, transition_time=0)
    s.panel_strobe()

    while True:
        a.brightness = random.randint(30, 40)
        time.sleep(random.uniform(0.1, 1))

        a.brightness = random.randint(50, 80)
        time.sleep(random.uniform(0.1, 1))


def streaming_wipe(a):
    panel_ids = [x['panelId'] for x in sorted(a.rotated_panel_positions, key=lambda k: k['x'])]
    s = a.effect_stream()

    c = [
        (  0, 255, 0),
        (  0, 192, 64),
        (  0, 128, 128),
        (  0,  64, 192),
        (  0,   0, 255)
    ]

    delta = 0
    while True:
        for i in range(len(c)):
            s.panel_prepare(
                panel_ids[int(len(panel_ids) / len(c) * i + delta) % len(panel_ids)],
                c[i][0], c[i][1], c[i][2],
                transition_time=120)
        s.panel_strobe()
        # Aurora can only handle 10 updates a second.
        time.sleep(2)
        delta += 1


def streaming_cylon(a):
    panels = a.rotated_panel_positions
    s = a.effect_stream()

    red = (255, 0, 0)
    black = (0, 0, 0)
    x = [x['x'] for x in panels]

    delta = 50
    band = min(x)
    while True:
        for p in panels:
            if p['x'] >= band and p['x'] <= band + 200:
                c = red
            else:
                c = black
            s.panel_prepare(p['panelId'], c[0], c[1], c[2], transition_time=8)
        s.panel_strobe()
        # Aurora can only handle 10 updates a second.
        time.sleep(.3)
        band += delta
        if band > max(x) - 3*delta or band < min(x):
            delta = -delta


def streaming_sunrise(a):
    panels = a.rotated_panel_positions
    s = a.effect_stream()

    red = (255, 0, 0)
    yellow = (255, 255, 0)
    blue = (0, 0, 255)
    y = [x['y'] for x in panels]
    mid_y = (min(y) + max(y)) / 2

    delta = 50
    band = min(y)
    while True:
        for p in panels:
            if p['y'] >= band and p['y'] <= band + 200:
                c = red
            elif p['y'] > mid_y:
                c = blue
            else:
                c = yellow
            s.panel_prepare(p['panelId'], c[0], c[1], c[2], transition_time=3)
        s.panel_strobe()
        # Aurora can only handle 10 updates a second.
        time.sleep(.3)
        band += delta
        if band > max(y) - 3*delta or band < min(y):
            delta = -delta


def display(a, args):
    fn = 'streaming_%s' % args.streaming
    if fn in globals():
        globals()[fn](a)
    else:
        print('No such display effect: %s' % args.streaming)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--streaming', dest='streaming')
    args = parser.parse_args()

    aurora = config.aurora()
    display(aurora, args)


if __name__ == '__main__':
    main(sys.argv)
