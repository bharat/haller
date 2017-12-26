#!/usr/bin/env python3
import sys
import random
import argparse
import bokeh

import config
from nanoleaf.nanoleaf.nanoleaf import Aurora

def effect_scripted():
    palette = [ {
        "hue": random.randint(0, 359),
        "saturation": 100,
        "brightness": random.randint(60, 80)
    } for x in range(1, 10)]

    return {
        "command" : "add",
        "animName" : "Scripted",
        "animType" : "explode",
        "colorType" : "HSB",
        "palette" : palette,
        "transTime" : { "maxValue": 50, "minValue": 50 },
        "delayTime" : { "maxValue": 0,   "minValue": 0 },
        "explodeFactor" : 0.5,
        "direction" : "outwards",
        "loop" : True
    }


def effect(a, args):
    if args.list:
        print('\n'.join(a.effects_list))

    elif args.set:
        if args.set not in a.effects_list:
            print('%s is an invalid effect\n' % args.set)
        a.effect = args.set

    elif args.create:
        effect = effect_scripted()
        a.effect_set_raw(effect)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', dest='list', action='store_true')
    parser.add_argument('--set', dest='set')
    parser.add_argument('--create', dest='create')
    args = parser.parse_args()

    aurora = config.aurora()
    effect(aurora, args)


if __name__ == '__main__':
    main(sys.argv)
