#!/usr/bin/env python3
import argparse
import random
import sys
import time
import pyaudio
import numpy as np
import config

from collections import deque
from nanoleaf.nanoleaf import Aurora
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

    last_strobe = time.time()
    noise_floor = 0
    while True:
        data = np.fromstring(stream.read(chunk_size),dtype=np.int16)
        now = time.time()

        if now - last_strobe < 0.1:
            continue

        max_amplitude = np.amax(np.absolute(data))
        max_amplitude = max(max_amplitude - noise_floor, 0)
        thresh = max_amplitude / 2**14

        for (i, panel_id) in enumerate(panel_ids):
            if i / len(panel_ids) < thresh:
                c = colors[int(i / len(panel_ids) * len(colors))]
                s.panel_prepare(panel_id, c[0], c[1], c[2], transition_time=0)
            else:
                s.panel_prepare(panel_id, 0, 0, 0, transition_time=5)

        s.panel_strobe()
        last_strobe = now



def viz_freq(a):
    panel_ids = [x['panelId'] for x in sorted(a.rotated_panel_positions, key=lambda k: k['y'])]
    s = a.effect_stream()

    # panels start off black
    for p in panel_ids:
        s.panel_prepare(p, 0, 0, 0, transition_time=0)
    s.panel_strobe()

    # set a palette that fades from blue to red
    colors = [
        [  0,   0, 255],
        [ 32,   0, 224],
        [ 64,   0, 192],
        [ 96,   0, 160],
        [128,   0, 128],
        [160,   0,  96],
        [192,   0,  64],
        [224,   0,  32],
    ]

    p = pyaudio.PyAudio()
    chunk_size = 512
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    input=True,
                    frames_per_buffer=chunk_size)

    # Much of the frequency math comes from this document:
    #   http://samcarcagno.altervista.org/blog/basic-sound-processing-python/
    #
    # which in turn is based on:
    #   https://web.archive.org/web/20120615002031/http://www.mathworks.com/support/tech-notes/1700/1702.html

    last_strobe = time.time()
    noise_floor = 0
    while True:
        # We can only strobe at 10hz so gather data for about 100ms
        # before rendering. There's probably a better way to do this.
        chan1 = np.fromstring(stream.read(chunk_size),dtype=np.int16)
        while True:
            now = time.time()
            elapsed = now - last_strobe

            if elapsed < 0.09:
                chan1 += np.fromstring(stream.read(chunk_size),dtype=np.int16)
            else:
                break

        chan1_size = len(chan1)
        assert chan1_size % 2 == 0, "bytes read must be even"

        # convert values to -1.0 to 1.0, then run FFT on it
        chan1 = chan1 / (2**15)
        power = np.fft.fft(chan1)

        # only the first half is relevant due to hermitian symmetry, and
        # we only care about magnitude so take the absolute value
        power = power[:int(chan1_size/2)]
        power = abs(power)

        # scale by the number of samples actually captured, and square it to
        # get the actual power
        power = power / float(chan1_size)
        power = power ** 2

        # we dropped half of the FFT so we have to double all the values to
        # maintain the same energy.
        power *= 2

        # Zero out the DC Component to avoid visual noise
        power[0] = 0

        # Create 8 bins
        bins = power[:int(chan1_size/2)].reshape(8, -1).mean(1)
        # print("  ", ["%0.5f " % x for x in bins])

        # Strobe our panels according to bin energy
        per_bin = len(panel_ids) / len(colors)
        for (i, panel_id) in enumerate(panel_ids):
            bin_index = int(i // per_bin)
            bs = bins[bin_index]
            if bs > 0.00005: # is this bin active enough?
                # print (i, bin_index, bs, bin_colors[bin_index], colors[bin_colors[bin_index]])
                c = colors[bin_index]
                #print(c)
                s.panel_prepare(panel_id, c[0], c[1], c[2], transition_time=0)
            else:
                s.panel_prepare(panel_id, 0, 0, 0, transition_time=5)
        s.panel_strobe()

        # print(now - last_strobe)
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
