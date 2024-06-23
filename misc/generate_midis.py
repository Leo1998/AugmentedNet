from multiprocessing import Pool
import subprocess
from AugmentedNet.common import ANNOTATIONSCOREDUPLES
import os
import music21

musescore_bin = "/home/god/Downloads/MuseScore-Studio-4.3.1.241490902-x86_64.AppImage"

def generate(inn, out):
    print(f"Converting file: {inn} to {out}")
    try:
        score = music21.converter.parse(inn, format="musicxml", forceSource=True)
        #remove all repeats
        for r in score.recurse().getElementsByClass("RepeatMark"):
            score.remove(r, recurse=True)
        out_mxl = score.write("musicxml")
        #score.write("midi", fp=out)

        os.makedirs(os.path.dirname(out), exist_ok=True)

        env = os.environ.copy()
        env["SKIP_LIBJACK"] = "1"
        subprocess.run([musescore_bin, out_mxl, "-o", out], env=env)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    target_format = ".mid"
    for nick, (a, s) in ANNOTATIONSCOREDUPLES.items():
        print(nick, s)
        inn = s
        out = s.replace(".mxl", target_format).replace(".krn", target_format).replace(".musicxml", target_format)
        out = out.replace("rawdata", "audio")
        if os.path.exists(inn):
            generate(inn, out)
