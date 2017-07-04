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
    while True:
        for panel_id in panel_ids:
            s.panel_set(panel_id,
                        random.randint(0, 255),
                        random.randint(0, 255),
                        random.randint(0, 255))
            # Aurora can only handle 10 updates a second.
            time.sleep(0.2)


def display(a, args):
    if args.streaming == 'random':
        streaming_random(a)

    elif args.streaming == 'wipe':
        streaming_wipe(a)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--streaming', dest='streaming')
    args = parser.parse_args()

    aurora = config.aurora()
    display(aurora, args)


if __name__ == '__main__':
    main(sys.argv)
