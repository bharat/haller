#!/usr/bin/env python3
import argparse
import random
import sys
import time

import config
from nanoleaf import Aurora

def streaming_random(a):
    panel_ids = [x['panelId'] for x in a.panel_positions]
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

def streaming_flash(a):
    panel_ids = [x['panelId'] for x in a.panel_positions]
    s = a.effect_stream()

    brt_delta = 1
    brt_max = 90
    brt_min = 30
    brt = int((brt_max + brt_min) / 2)
    while True:
        a.brightness = brt
        s.panel_set(random.choice(panel_ids),
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255))
        # Aurora can only handle 10 updates a second.
        time.sleep(0.2)
        brt = brt + brt_delta
        if brt > brt_max or brt < brt_min:
            brt_delta = -brt_delta


def streaming_wipe(a):
    panel_ids = [x['panelId'] for x in sorted(a.panel_positions, key=lambda k: k['x'])]
    s = a.effect_stream()
    a.brightness = 70

    # random
    c = [
        (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
        (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
        (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    ]

    # green
    c = [
        (  0, 255, 0),
        (  0, 192, 0),
        (  0, 128, 0),
        (  0,  64, 0),
        (  0,   0, 0)
    ]

    idx = [0,
           int(len(panel_ids) / len(c)),
           int(len(panel_ids) / len(c) * 2),
           int(len(panel_ids) / len(c) * 3),
           int(len(panel_ids) / len(c) * 4)
       ]
    while True:
        for i in range(len(c)):
            s.panel_prepare(panel_ids[idx[i]], c[i][0], c[i][1], c[i][2], transition_time=30)
            idx[i] = (idx[i] + 1) % len(panel_ids)
        s.panel_strobe()
        # Aurora can only handle 10 updates a second.
        time.sleep(.8)


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
