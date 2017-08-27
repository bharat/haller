# haller
Fun with Nanoleaf Aurora

## What is it?
Haller is a wrapper around https://github.com/bharat/nanoleaf (a fork of https://github.com/software-2/nanoleaf) that provides some additional, higher level functionality to control your Nanoleaf Aurora

## What can it do?
1. automatically find and connect to your Aurora
1. Turn on/off your Aurora from a script
1. Handle rotation of your Aurora (so that you can script "left to right" type effects)
1. Real-time display effects (including some samples)
1. Audio visualization effects (including some samples)

## How do I use it?

### Requirements
1. Python3
1. Python modules: bokeh, pyaudio, numpy, scipy

### Quick start
1. `git clone git@github.com:bharat/nanoleaf.git` inside the haller directory
1. `pip3 install bokeh pyaudio numpy scipy`
1. Hit the pairing button on your Aurora
1. run `config.py`. It will discover your Aurora, pair with it and create a file called `aurora.ini` containing config data.

#### Configure your panel layout
1. `config.py --plot` will create an HTML file called `plot.html` that contains a visual representation of your panel layout
1. `config.py --rotate <degrees>` will calculate a new rotation of your panel layout. Use this with `--plot` to visualize to make sure that your panel rotation matches your physical layout. The results of this rotation are cached in `aurora.ini` for the future.

### Effects
1. `effect.py --list` to list all effects
1. `effect.py --set <name>` to choose an effect
1. `effect.py --create` creates a hardcoded effect called `Scripted`. Work in progress here.

### Streaming

This uses the `External Control` feature of Aurora to allow dynamic effects. There are a few hardcoded ones, but the code is an example for what you can do. Try `display.py --streaming wipe` to see one of them.

### Visualization

Using the streaming interface, you can turn your Aurora into a music visualizer. Try `visualizer.py --viz amplitude` for yourself. You can see what it looks like here: https://www.youtube.com/watch?v=nnojsRrwK4c
