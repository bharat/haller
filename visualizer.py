#!/usr/bin/env python3
import argparse
import random
import sys
import time
import pyaudio
import numpy as np
import config

from collections import deque
from nanoleaf import Aurora
from random import randint, choice


def viz_amplitude(a):
    panel_ids = [x['panelId'] for x in sorted(a.rotated_panel_positions, key=lambda k: k['y'])]
    s = a.effect_stream()

    for p in panel_ids:
        s.panel_prepare(p, 0, 0, 0, transition_time=0)
    s.panel_strobe()

    # fade from blue to red
    colors = [
        [  0,   0, 255],
        [ 64,   0, 192],
        [128,   0, 128],
        [192,   0,  64],
        [255,   0,   0]
    ]

    p = pyaudio.PyAudio()
    chunk_size = 512
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    input=True,
                    frames_per_buffer=chunk_size)

    peaks = deque(maxlen=100)
    last_strobe = time.time()
    noise_floor = 2500
    while True:
        data = np.fromstring(stream.read(chunk_size),dtype=np.int16)
        now = time.time()

        if now - last_strobe < .1:
            continue

        max_amplitude = np.amax(np.absolute(data))
        peaks.append(max_amplitude)
        max_peak = (sum(peaks) / len(peaks) * 1.5)
        max_amplitude = max(max_amplitude - noise_floor, 0)
        thresh = max_amplitude / 2**14 # max_peak
        print(max_amplitude, max_peak)

        for (i, panel_id) in enumerate(panel_ids):
            if i / len(panel_ids) < thresh:
                c = colors[int(i / len(panel_ids) * len(colors))]
                s.panel_prepare(panel_id, c[0], c[1], c[2], transition_time=0)
            else:
                s.panel_prepare(panel_id, 0, 0, 0, transition_time=5)

        s.panel_strobe()
        last_strobe = now


def display(a, args):
    fn = 'viz_%s' % args.viz
    if fn in globals():
        globals()[fn](a)
    else:
        print('No such visualizer: %s' % args.viz)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--viz', dest='viz')
    args = parser.parse_args()

    aurora = config.aurora()
    display(aurora, args)


if __name__ == '__main__':
    main(sys.argv)
