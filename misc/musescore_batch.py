from multiprocessing import Pool
import os
import subprocess
from AugmentedNet.common import ANNOTATIONSCOREDUPLES

musescore_bin = "/home/fricke/MuseScore-4.1.1.232071203-x86_64.AppImage"

def mscore(inout):
    inn, out = inout
    print(f"Processing file: {inn}")
    env = os.environ.copy()
    env["SKIP_LIBJACK"] = "1"
    subprocess.run([musescore_bin, inn, "-o", out], env=env)

def check(inout):
    _, out = inout
    if not os.path.exists(out):
        print(f"File {out} failed to process!")

if __name__ == "__main__":
    target_format = ".mid"
    files = []
    for nick, (a, s) in ANNOTATIONSCOREDUPLES.items():
        print(nick, s)
        inn = s
        out = s.replace(".mxl", target_format).replace(".krn", target_format).replace(".musicxml", target_format)
        if os.path.exists(inn):
            files.append((inn, out))

    print(f"Number of files: {len(files)}")

    with Pool(8) as p:
        p.map(mscore, files)

    print("Checking...")
    for f in files:
        check(f)