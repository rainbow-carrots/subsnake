# subsnake

subsnake is a polyphonic virtual analog subtractive synthesizer, written in python.

what does it do? well, i'm so very glad you asked.
* it makes sound (yay!)
* it has 12 voices
* it supports midi (input)
* it can save & load patches

ok. sounds neat. what's in a voice?
* 3 sine, polyblep (anti-aliased) sawtooth or pulse generators (+ PWM)
* 1 state-variable filter - using an oversampled Chamberlin topology with feedback saturation & drive
* 2 ADSR envelopes - one for amplitude, one for filter frequency, using leaky integrators
* 4 modulators - 2 LFOs, 2 envelopes, with dedicated assignable attenuverters for every parameter
    * LFOs: sine, triangle, ramp, saw, square, sample & hold | controllable speed & phase
    * envelopes: attack-release, attack-hold-release, loop (attack-release) | controllable attack & release

there's also a stereo delay on the master bus (voices + recorder), and a stereo audio recorder/looper with overdubbing.

what's the midi like?
* it supports device & channel selection (whoa...)
* cc's can be added & removed, and freely assigned to control any parameter
    * cc parameter updates are reflected visually, so the sliders & displays remain in sync
* gate on/off events use sample-accurate timing (works well with sequencers)

ok. sweet. how can i play it?
* since there's no package (yet), you'll need to run it in a python virtual environment. open a terminal (on linux) and do the following:
    * you'll need to install python first, along with pip (usually included - check by typing `pip`)
    * download (or clone) this repo, and open a terminal in the folder
    * type `python -m venv ./.venv`, to create the environment
    * next, type `./.venv/bin/python/activate` - you should now see `.venv` before your command prompt
    * now, type `pip install -r requirements.txt` - this will install the libraries you need to run it
        * PySide6 (Qt) for the GUI
        * sounddevice for audio output
        * numpy/numba for DSP
        * python-rtmidi for midi
        * mido for midi parsing
    * finally, navigate to the project directory and type: `python ./main.py` - and away you shall go

what's on the docket?
* move midi settings to bottom right of module grid (currently hidden in toolbar & shown in bottom left)
* add settings panel to allow saving recorder buffer to (wav) file
* finish delay modulation & enable delay mod dials
* add trigger signals for mod envelopes
* record & restore modulation dial states from patches
* add delay & modulator parameters as cc destinations
* allow UI theming & add more stock themes (dark mode pending)
* add themeable oscilloscope display
* add more "factory" patches
* add ping pong & filter to delay

if you encounter any issues (not listed above), let me know with an issue report. otherwise, enjoy :3

