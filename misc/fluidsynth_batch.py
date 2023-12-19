#!/usr/bin/env python3

from multiprocessing import Pool
import os
import subprocess

soundfont = "/home/fricke/piano.sf2"
instrument_name = "piano"
out_type = "flac"

def fluidsynth(midi_file):
    out_file = midi_file.replace(".mid", f"_{instrument_name}.{out_type}")
    print(f"Generating audio from MIDI {midi_file} into {out_file}")

    subprocess.call(['fluidsynth', '-T', out_type, '-F', out_file, '-o', 'synth.midi-bank-select=gs', '-ni', soundfont, midi_file])

if __name__ == "__main__":
    midi_files = []
    for (root, dirs, files) in os.walk("audio"):
        for name in files:
            if name.endswith(".mid"):
                midi_files.append(os.path.join(root, name))

    with Pool(8) as p:
        p.map(fluidsynth, midi_files)
