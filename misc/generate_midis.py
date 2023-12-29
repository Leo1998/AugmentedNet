from multiprocessing import Pool
import os
from AugmentedNet.common import ANNOTATIONSCOREDUPLES
import music21

def generate(inn, out):
    print(f"Converting file: {inn} to {out}")
    try:
        score = music21.converter.parse(inn, format="musicxml", forceSource=True)

        #remove all repeats
        for r in score.flat.getElementsByClass("RepeatMark"):
            score.remove(r, recurse=True)

        mf = music21.midi.translate.streamToMidiFile(score)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        mf.open(out, 'wb')
        mf.write()
        mf.close()
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