#!/usr/bin/env python3

from multiprocessing import Pool
import os
import subprocess

sonic_annotator = "/home/fricke/sonic-annotator-1.6-linux64-static/sonic-annotator"
nnlschroma = "/home/fricke/sonic-annotator-1.6-linux64-static/nnls_bothchroma.n3"
nnlssemitone = "/home/fricke/sonic-annotator-1.6-linux64-static/nnls_semitonespectrum.n3"

def chroma(wav):
    transform = nnlssemitone
    subprocess.run([sonic_annotator, "-t", transform, wav, "-w", "csv"])

if __name__ == "__main__":
    audio_files = []
    for (root, dirs, files) in os.walk("audio"):
        for name in files:
            if name.endswith(".flac") or name.endswith(".wav"):
                audio_files.append(os.path.join(root, name))
                
    with Pool(8) as p:
        p.map(chroma, audio_files)
