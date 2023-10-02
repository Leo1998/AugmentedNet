"""Generate pkl files for every tsv training example."""

import os
import pandas as pd
import numpy as np
import tensorflow as tf

from . import cli
from . import joint_parser
from .cache import TransposeKey, m21IntervalStr
from .common import DATASETSUMMARYFILE
from .feature_representation import (
    TRANSPOSITIONKEYS,
    INTERVALCLASSES,
    INTERVAL_ENHARMONICS,
)
from .input_representations import (
    available_representations as availableInputs,
)
from .output_representations import (
    available_representations as availableOutputs,
)
from .utils import padToSequenceLength, DynamicArray


def _getTranspositions(df, transpositionKeys=TRANSPOSITIONKEYS):
    tonicizedKeys = df.a_localKey.to_list() + df.a_tonicizedKey.to_list()
    tonicizedKeys = set(tonicizedKeys)
    ret = []
    for interval in INTERVALCLASSES:
        transposed = [TransposeKey(k, interval) for k in tonicizedKeys]
        # Transpose to this interval if every modulation lies within
        # the set of KEY classes that we can classify
        if set(transposed).issubset(set(transpositionKeys)):
            ret.append(interval)
    return ret


def initializeArrays(inputRepresentations, outputRepresentations):
    """Each array becomes a dict entry with the name of the input/output"""
    outputArrays = {}
    for split in ["training", "validation"]:
        for x in inputRepresentations:
            outputArrays[split + f"_X_{x}"] = []
        for y in outputRepresentations:
            outputArrays[split + f"_y_{y}"] = []
    return outputArrays


def scrutinize(df, qualityThresh=0.75, bassThresh=0.8):
    """Filter 'bad quality' annotations."""
    originalIndex = len(df.index)
    df = df[
        (df.qualitySquaredSum < qualityThresh)
        & (df.measureMisalignment == False)
        & (df.incongruentBass < bassThresh)
    ]
    filteredIndex = len(df.index)
    print(f"\t({originalIndex}, {filteredIndex})")


def correctSplit(split, testSetOn):
    """Correct the split of this file according to 'testSetOn' parameter."""
    if testSetOn:
        if split == "validation":
            return "training"
        elif split == "test":
            return "validation"
    return split


def generateDataset(
    synthetic,
    texturizeEachTransposition,
    noTransposition,
    collections,
    testCollections,
    inputRepresentations,
    outputRepresentations,
    sequenceLength,
    scrutinizeData,
    testSetOn,
    tsvDir,
    npzOutput,
    transpositionKeys,
):
    synthetic = False
    texturizeEachTransposition = False
    # dataAugmentation = False
    scrutinizeData = False
    transpositionKeys = [
        "D-",
        "b-",
        "A-",
        "f",
        "E-",
        "c",
        "B-",
        "g",
        "F",
        "d",
        "C",
        "a",
        "G",
        "e",
        "D",
        "b",
        "A",
        "f#",
        "E",
        "c#",
        "B",
        "g#",
        "F#",
        "d#",
    ]
    inputRepresentations = ["Bass19", "Chromagram19"]
    outputArrays = {}
    training = ["training", "validation"] if testSetOn else ["training"]
    validation = ["test"] if testSetOn else ["validation"]
    datasetDir = f"{tsvDir}-synth" if synthetic else tsvDir
    summaryFile = os.path.join(datasetDir, DATASETSUMMARYFILE)
    if not os.path.exists(summaryFile):
        print("You need to generate the tsv files first.")
        exit()
    datasetSummary = pd.read_csv(summaryFile, sep="\t")
    trainingdf = datasetSummary[
        (datasetSummary.collection.isin(collections))
        & (datasetSummary.split.isin(training))
    ]
    validationdf = datasetSummary[
        (datasetSummary.collection.isin(testCollections))
        & (datasetSummary.split.isin(validation))
    ]
    df = pd.concat([trainingdf, validationdf])
    for row in df.itertuples():
        split = correctSplit(row.split, testSetOn)
        if split == "test":
            # Preemptive measure just to avoid a potential disaster
            continue
        print(f"{row.split} -used-as-> {split}", row.file)
        tsvlocation = os.path.join(datasetDir, row.split, f"{row.file}.tsv")
        df = pd.read_csv(tsvlocation, keep_default_na=False, na_values=[], sep="\t")
        df.set_index("j_offset", inplace=True)
        df["c_basschroma"] = df["c_basschroma"].apply(eval)
        df["c_chroma"] = df["c_chroma"].apply(eval)
        df["a_pitchNames"] = df["a_pitchNames"].apply(eval)
        df["a_pcset"] = df["a_pcset"].apply(eval)
        df["s_notes"] = df["s_notes"].apply(eval)
        df["s_intervals"] = df["s_intervals"].apply(eval)
        if scrutinizeData and split == "training":
            df = scrutinize(df)
        if noTransposition or split != "training":
            transpositions = ["P1"]
        else:
            transpositions = _getTranspositions(df, transpositionKeys)
            print("\t", transpositions)
        if synthetic:
            if not texturizeEachTransposition:
                # once per file
                df = joint_parser.retexturizeSynthetic(df)
            else:
                # once per transposition
                dfsynth = df.copy()
        for transposition in transpositions:
            if synthetic and texturizeEachTransposition:
                df = joint_parser.retexturizeSynthetic(dfsynth)
            for inputRepresentation in inputRepresentations:
                if inputRepresentation == "Bass19":
                    column = "c_basschroma"
                elif inputRepresentation == "Chromagram19":
                    column = "c_chroma"
                else:
                    continue

                Xi = np.array(df[column].to_list())
                semitones = m21IntervalStr(transposition).semitones
                Xi = np.roll(Xi, semitones, axis=1)
                if Xi.shape[1] == 12:
                    Xi = np.pad(Xi, ((0, 0), (7, 0)))
                Xi = padToSequenceLength(Xi, sequenceLength)
                npzfile = f"{split}_X_{inputRepresentation}"
                if npzfile not in outputArrays:
                    outputArrays[npzfile] = DynamicArray(
                        shape=Xi.shape, dtype="float32", memmap=f".{npzfile}.mmap"
                    )
                for sequence in Xi:
                    outputArrays[npzfile].update(sequence)

                '''inputLayer = availableInputs[inputRepresentation](df)
                Xi_target = inputLayer.run(transposition=transposition)
                Xi_target = Xi_target [:,7:]
                Xi_target = padToSequenceLength(Xi_target, sequenceLength)
                npzfile = f"{split}_X_{inputRepresentation}_target"
                if npzfile not in outputArrays:
                    outputArrays[npzfile] = DynamicArray(
                        shape=Xi_target.shape, dtype="float32", memmap=f".{npzfile}.mmap"
                    )
                for sequence in Xi_target:
                    outputArrays[npzfile].update(sequence)'''

            for outputRepresentation in outputRepresentations:
                outputLayer = availableOutputs[outputRepresentation](df)
                yi = outputLayer.run(transposition=transposition)
                if outputRepresentation == "HarmonicRhythm7":
                    yi = padToSequenceLength(yi, sequenceLength, value=6)
                else:
                    yi = padToSequenceLength(yi, sequenceLength)
                npzfile = f"{split}_y_{outputRepresentation}"
                if npzfile not in outputArrays:
                    outputArrays[npzfile] = DynamicArray(
                        shape=yi.shape, dtype="int8", memmap=f".{npzfile}.mmap"
                    )
                for sequence in yi:
                    outputArrays[npzfile].update(sequence)
    # drop the extension, we'll overwrite it to .npz
    filename, _ = os.path.splitext(npzOutput)
    outputFile = f"{filename}-synth" if synthetic else filename
    outputArrays = {k: v.finalize() for k, v in outputArrays.items()}
    np.savez_compressed(outputFile, **outputArrays)


if __name__ == "__main__":
    parser = cli.npz()
    args = parser.parse_args()
    generateDataset(**vars(args))
