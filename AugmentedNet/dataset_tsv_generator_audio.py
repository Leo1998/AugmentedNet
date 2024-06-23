"""Combine all available (score, annotation) pairs into tsv files."""

import os
import pandas as pd
from pathlib import Path

from . import cli
from .common import (
    ANNOTATIONSCOREDUPLES,
    DATASPLITS,
    DATASETSUMMARYFILE,
)
from .joint_parser import (
    parseAnnotationAndAudio,
)

nnls_chroma_postfix = "_vamp_nnls-chroma_nnls-chroma_bothchroma.csv"
nnls_semitone_postfix = "_vamp_nnls-chroma_nnls-chroma_semitonespectrum.csv"
fixedOffset = 0.04643990929705215419501133786848 # 2048 / 44100


def generateDataset(synthesize=False, texturize=False, tsvDir="dataset"):
    statsdict = {
        "file": [],
        "annotation": [],
        "chromacsv": [],
        "collection": [],
        "split": [],
        # "misalignmentMean": [],
        # "qualityMean": [],
        # "incongruentBassMean": [],
    }
    datasetDir = tsvDir
    Path(datasetDir).mkdir(exist_ok=True)
    for split, files in DATASPLITS.items():
        Path(os.path.join(datasetDir, split)).mkdir(exist_ok=True)
        for nickname in files:
            #if nickname != "abc-op18-no1-4":
                #continue
            print(nickname)
            annotation, score = ANNOTATIONSCOREDUPLES[nickname]
            miditsv = score.replace("rawdata", "audio").replace(".mxl", ".tsv").replace(".krn", ".tsv").replace(".musicxml", ".tsv")

            postfix = f"_piano{nnls_chroma_postfix}"
            chromacsv = score.replace("rawdata", "audio").replace(".mxl", postfix).replace(".krn", postfix).replace(".musicxml", postfix)
            try:
                df = parseAnnotationAndAudio(
                    annotation, chromacsv, miditsv, fixedOffset=fixedOffset
                )
            except Exception as e:
                print("\tErrored.")
                print(e)
                continue
            outpath = os.path.join(datasetDir, split, nickname + ".tsv")
            df.to_csv(outpath, sep="\t")
            collection = nickname.split("-")[0]
            statsdict["file"].append(nickname)
            statsdict["annotation"].append(annotation)
            statsdict["chromacsv"].append(chromacsv)
            statsdict["collection"].append(collection)
            statsdict["split"].append(split)
            # misalignment = round(df.measureMisalignment.mean(), 2)
            # statsdict["misalignmentMean"].append(misalignment)
            # qualitySquaredSum = round(df.qualitySquaredSum.mean(), 2)
            # statsdict["qualityMean"].append(qualitySquaredSum)
            # incongruentBass = round(df.incongruentBass.mean(), 2)
            # statsdict["incongruentBassMean"].append(incongruentBass)
            df = pd.DataFrame(statsdict)
            df.to_csv(os.path.join(datasetDir, DATASETSUMMARYFILE), sep="\t")


if __name__ == "__main__":
    parser = cli.tsv()
    args = parser.parse_args()
    kwargs = vars(args)
    generateDataset(**kwargs)
