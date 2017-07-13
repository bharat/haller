#!/usr/bin/env python3
import argparse
import random
import sys
import time

import config
from nanoleaf import Aurora
from random import randint

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


def streaming_spread(a):
    panel_ids = [x['panelId'] for x in a.rotated_panel_positions]
    s = a.effect_stream()

    for p in panel_ids:
        s.panel_prepare(p, 0, 0, 0, transition_time=0)

    sequence = [
        [129],
        [3, 176],
        [107, 66, 36],
        [172, 167, 25],
        [2, 9],
        [138, 78, 127],
        [30, 68, 240],
        [48, 37, 49],
        [215, 33, 57, 144, 90],
        [194, 108, 12],
        [209, 140]
    ]

    c = [randint(0, 4) * 60 + 10, randint(0, 4) * 60 + 10, randint(0, 4) * 60 + 10]
    mutate_index = 0
    while True:
        mutate_index = (mutate_index + 1) % 3
        mutate_amount = random.choice([-60, 60])
        if c[mutate_index] == 250:
            mutate_amount = -60
        elif c[mutate_index] == 10:
            mutate_amount = 60
        c[mutate_index] = max(min(c[mutate_index] + mutate_amount, 255), 0)

        for group in sequence:
            for panel_id in group:
                s.panel_prepare(panel_id, c[0], c[1], c[2], transition_time=3)
            s.panel_strobe()
            time.sleep(.3)
        sequence.reverse()


def streaming_conway(a):
    panel_ids = [x['panelId'] for x in a.rotated_panel_positions]
    s = a.effect_stream()

    for p in panel_ids:
        s.panel_prepare(p, 0, 0, 0, transition_time=0)
    s.panel_strobe()
    adjacency = {209: [12, 0, 0],
                 12: [33, 209, 0, 0],
                 33: [49, 12, 0, 0],
                 49: [215, 33, 30, 0, 0],
                 215: [49, 0, 0],
                 30: [49, 138, 0, 0],
                 138: [30, 2, 0, 0],
                 2: [138, 167, 0, 0],
                 167: [2, 66, 0, 0],
                 66: [167, 176, 0, 0],
                 176: [66, 36, 129, 0, 0],
                 36: [176, 172, 0, 0],
                 172: [36, 0, 0],
                 129: [176, 3, 0, 0],
                 3: [107, 129, 0, 0],
                 107: [3, 25, 0, 0],
                 25: [107, 9, 0, 0],
                 9: [25, 127, 78, 0, 0],
                 127: [9, 240, 0, 0],
                 240: [127, 37, 0, 0],
                 37: [240, 90, 0, 0],
                 90: [194, 37, 0, 0],
                 194: [90, 0, 0],
                 78: [9, 68, 0, 0],
                 68: [48, 78, 0, 0],
                 48: [57, 68, 144, 0, 0],
                 57: [48, 0, 0],
                 144: [48, 108, 0, 0],
                 108: [144, 140, 0, 0],
                 140: [108, 0, 0]}
    start_panel = random.choice(panel_ids)
    s.panel_prepare(start_panel, 255, 131, 0, transition_time = 0)
    adjacency[start_panel][-1] = 1
    s.panel_strobe()
    time.sleep(1)
    while True:
        for p in panel_ids:
            if adjacency[p][len(adjacency[p])-1] == 1:
                for i in range(0, len(adjacency[p])-2):
                    adjacency[adjacency[p][i]][len(adjacency[adjacency[p][i]])-2] += 1
        for p in panel_ids:
            if adjacency[p][len(adjacency[p])-2] == 1:
                adjacency[p][len(adjacency[p])-1] = 1
                s.panel_prepare(p, 255, 131, 0, transition_time = 1)
            else:
                s.panel_prepare(p, 0, 0, 0, transition_time = 1)
                adjacency[p][len(adjacency[p])-1] = 0
        s.panel_strobe()
        time.sleep(1)
        for p in panel_ids:
            adjacency[p][len(adjacency[p])-2] = 0

def streaming_eq(a):
    panel_ids = [x['panelId'] for x in a.rotated_panel_positions]
    s = a.effect_stream()

    for p in panel_ids:
        s.panel_prepare(p, 0, 0, 0, transition_time=0)

    sequence = [
        [129],
        [3, 176],
        [107, 66, 36],
        [172, 167, 25],
        [2, 9],
        [138, 78, 127],
        [30, 68, 240],
        [48, 37, 49],
        [215, 33, 57, 144, 90],
        [194, 108, 12],
        [209, 140]
    ]

    delta = [
        0, 1, 1, 0, -1, -1, 0, 1, 1, 0, 1, 1, -1, -1, 0, 0, 1, 1, -4,
        5, 1, 1, 1, -1, -1, -1, -1, -4
    ]

    m = len(sequence) - 1
    white = [255, 255, 255]
    black = [0, 0, 0]
    level = randint(0, m)
    d = 0

    while True:
        if random.random() > 0.6:
            level += delta[d]
            d = (d + 1) % len(delta)

        for i in range(0, m + 1):
            if i <= level:
                c = white
            else:
                c = black
            for panel_id in sequence[i]:
                s.panel_prepare(panel_id, c[0], c[1], c[2], transition_time=1)
            s.panel_strobe()
        time.sleep(.1)


def streaming_dimmer(a):
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
    min_x = min(x)
    max_x = max(x)
    band = min_x
    while True:
        for p in panels:
            if p['x'] >= band and p['x'] <= band + 100:
                c = red
                tt = 0
            else:
                c = black
                tt = 4
            s.panel_prepare(p['panelId'], c[0], c[1], c[2], transition_time=tt)
        s.panel_strobe()
        # Aurora can only handle 10 updates a second.
        time.sleep(.05)
        band += delta
        if band > max_x or band < min_x - 4 * abs(delta):
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
