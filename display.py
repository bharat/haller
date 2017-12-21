#!/usr/bin/env python3
import argparse
import random
import sys
import time
import webcolors

import config
from nanoleaf.aurora import Aurora
from random import randint, choice

def streaming_rain(a):
    panel_ids = [x['panelId'] for x in a.rotated_panel_positions]
    s = a.effect_stream()

    adjacency = {
        209: [12],
        12: [33, 209],
        33: [49, 12],
        49: [215, 33, 30],
        215: [49],
        30: [49, 138],
        138: [30, 2],
        2: [138, 167],
        167: [2, 66],
        66: [167, 176],
        176: [66, 36, 129],
        36: [176, 172],
        172: [36],
        129: [176, 3],
        3: [107, 129],
        107: [3, 25],
        25: [107, 9],
        9: [25, 127, 78],
        127: [9, 240],
        240: [127, 37],
        37: [240, 90],
        90: [194, 37],
        194: [90],
        78: [9, 68],
        68: [48, 78],
        48: [57, 68, 144],
        57: [48],
        144: [48, 108],
        108: [144, 140],
        140: [108]
    }

    # set all panels to random colors
    c = {}

    orig = 48
    for p in panel_ids:
        c[p] = [orig] * 3
    target = sum([sum(x) for x in c.values()])

    drops = [
        [255,   0,   0],
        [255, 255,   0],
        [255,   0, 255],
        [0,   255,   0],
        [0,   255, 255],
        [0,     0, 255]
    ]

    # Average the colors of the adjacent panels
    while True:
        # average colors for neighbors
        new_c = {}
        for p, v in adjacency.items():
            new_c[p] = [0, 0, 0]
            for i in range(3):
                new_c[p][i] = int(sum([c[n][i] for n in v] + [c[p][i]]) / (len(v) + 1))
        c = new_c

        # default transition time is 1 second
        tt = {p: 10 for p in panel_ids}

        # randomly drop in a raindrop
        if random.random() > 0.5:
            p = choice(panel_ids)
            c[p] = choice(drops)
            tt[p] = 0

        # update all panels
        for p in panel_ids:
            s.panel_prepare(p, c[p][0], c[p][1], c[p][2], transition_time=tt[p])
        s.panel_strobe()

        # drain the pool back to target saturation
        total = sum([sum(x) for x in c.values()])
        to_drain = max(total - target, 0)
        while to_drain > 0:
            p = choice(panel_ids)
            i = choice([0, 1, 2])
            if c[p][i] > orig:
                c[p][i] -= 1
                to_drain -= 1
        time.sleep(1)


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
        mutate_amount = choice([-60, 60])
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

def streaming_epilepsy(a):
    s = a.effect_stream()
    panel_ids = [x['panelId'] for x in a.rotated_panel_positions]
    while True:
        for p in panel_ids:
            s.panel_prepare(p, 255, 255, 255, transition_time = 0)
        s.panel_strobe()
        time.sleep(.1)
        for p in panel_ids:
            s.panel_prepare(p, 0, 0, 0, transition_time = 0)
        s.panel_strobe()
        time.sleep(.1)

def streaming_mesmer(a):
    s = a.effect_stream()

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
    colors = [[0, 0, 0]] * len(sequence)
    mutate_multiplier = [1, 1, 1]
    c = [0, 0, 0]
    color_starter = random.randint(0, 2)
    for i in range (0, 2):
        c[(i + color_starter)%3] = random.randint(0, 2) * 10 + (i + 1) * 60
    mutate_index = 0
    gen = 0
    mutate_amount = 0
    while True:
        gen += 1
        if gen % 2 == 0:
            mutate_index = (mutate_index + 1) % 3
            if c[mutate_index] == 250:
                mutate_multiplier[mutate_index] = -1
            elif c[mutate_index] == 10:
                mutate_multiplier[mutate_index] = 1
            mutate_amount = 10*mutate_multiplier[mutate_index]
            c[mutate_index] = max(min(c[mutate_index] + mutate_amount, 255), 0)
        colors.insert(0, list(c))
        del(colors[len(sequence):])

        for i, group in enumerate(sequence):
            for panel_id in group:
                s.panel_prepare(panel_id, colors[i][0], colors[i][1], colors[i][2],
                                transition_time=1)
            s.panel_strobe()
        time.sleep(0.2)


def streaming_conway(a):
    panel_ids = [x['panelId'] for x in a.rotated_panel_positions]
    s = a.effect_stream()

    for panel in panel_ids:
        s.panel_prepare(panel, 0, 0, 0, transition_time=0)
    s.panel_strobe()
    adjacency = {
        209: [12],
        12: [33, 209],
        33: [49, 12],
        49: [215, 33, 30],
        215: [49],
        30: [49, 138],
        138: [30, 2],
        2: [138, 167],
        167: [2, 66],
        66: [167, 176],
        176: [66, 36, 129],
        36: [176, 172],
        172: [36],
        129: [176, 3],
        3: [107, 129],
        107: [3, 25],
        25: [107, 9],
        9: [25, 127, 78],
        127: [9, 240],
        240: [127, 37],
        37: [240, 90],
        90: [194, 37],
        194: [90],
        78: [9, 68],
        68: [48, 78],
        48: [57, 68, 144],
        57: [48],
        144: [48, 108],
        108: [144, 140],
        140: [108]
    }
    state = {}
    for panel in panel_ids:
        state[panel] = [0, 0]

    start_panel = choice(panel_ids)
    s.panel_prepare(start_panel, 255, 131, 0, transition_time = 0)
    state[start_panel][0] = 1
    s.panel_strobe()
    time.sleep(1)
    while True:
        for panel in panel_ids:
            if state[panel][0] == 1:
                for adjacent_panel in adjacency[panel]:
                    state[adjacent_panel][1] += 1
        for panel in panel_ids:
            if state[panel][1] == 1:
                state[panel][0] = 1
                s.panel_prepare(panel, 255, 131, 0, transition_time = 1)
            else:
                s.panel_prepare(panel, 0, 0, 0, transition_time = 1)
                state[panel][0] = 0
        s.panel_strobe()
        time.sleep(1)
        for panel in panel_ids:
            state[panel][1] = 0


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


def streaming_fill(a, args):
    panels = a.rotated_panel_positions
    s = a.effect_stream()

    for color in args.colors:
        color = webcolors.name_to_rgb(color)
        panel_ids = [x['panelId'] for x in sorted(a.rotated_panel_positions, key=lambda k: k['y'])]

        for (i, p_id) in enumerate(panel_ids):
            s.panel_prepare(p_id, color[0], color[1], color[2], transition_time=int((i / 10)*5))
            s.panel_strobe()

        time.sleep(2.5)

    for (i, p_id) in enumerate(reversed(panel_ids)):
        s.panel_set(p_id, 0, 0, 0, transition_time=int((i / 10)*5))


def display(a, args):
    fn = 'streaming_%s' % args.streaming
    if fn in globals():
        globals()[fn](a, args)
    else:
        print('No such display effect: %s' % args.streaming)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--streaming', dest='streaming')
    parser.add_argument('--colors', nargs='*')
    args = parser.parse_args()

    aurora = config.aurora()
    display(aurora, args)


if __name__ == '__main__':
    main(sys.argv)
