import os
import pretty_midi
import pandas as pd
import numpy as np

def get_events_seconds(mid):
    events = {}
    for instrument in mid.instruments:
        for note in instrument.notes:
            if note.velocity > 0:
                t = note.start
                if t not in events:
                    events[t] = []
                events[t].append(note.pitch)
    return events

def get_quarters(mid, start_time=0.0):
    tempo_change_times, tempi = mid.get_tempo_changes()
    quarters = [start_time]

    tempo_idx = 0
    while (tempo_idx < tempo_change_times.shape[0] - 1 and quarters[-1] > tempo_change_times[tempo_idx + 1]):
        tempo_idx += 1

    end_time = mid.get_end_time()
    while quarters[-1] < end_time:
        tempo = tempi[tempo_idx] # in quarters per minute

        next_quarter = quarters[-1] + 60.0/tempo
        if (tempo_idx < tempo_change_times.shape[0] - 1 and next_quarter > tempo_change_times[tempo_idx + 1]):
            next_quarter = quarters[-1]
            quarter_remaining = 1.0
            while (tempo_idx < tempo_change_times.shape[0] - 1 and next_quarter + quarter_remaining*60.0/tempo >= tempo_change_times[tempo_idx + 1]):
                overshot_ratio = (tempo_change_times[tempo_idx + 1] - next_quarter)/(60.0/tempo)
                next_quarter += overshot_ratio*60.0/tempo
                quarter_remaining -= overshot_ratio
                tempo_idx = tempo_idx + 1
                tempo = tempi[tempo_idx]
            next_quarter += quarter_remaining*60.0/tempo
        quarters.append(next_quarter)
    quarters = np.array(quarters[:-1])
    return quarters

def find_quarterLength(quarters, time):
    tempo_change_times, tempi = mid.get_tempo_changes()

    tempo_idx = 0
    while (tempo_idx < tempo_change_times.shape[0] - 1 and time > tempo_change_times[tempo_idx + 1]):
        tempo_idx += 1
    tempo = tempi[tempo_idx] # in quarters per minute

    for i, q in enumerate(quarters):
        if q > time:
            return i - ((q - time) / (60.0/tempo))
    return len(quarters) - 1 - ((quarters[-1] - time) / (60.0/tempo))

def get_events_quarterLength(mid):
    events = {}

    quarters = get_quarters(mid)
    for instrument in mid.instruments:
        for note in instrument.notes:
            if note.velocity > 0:
                t = note.start
                q = round(find_quarterLength(quarters, t), 3)

                if q not in events:
                    events[q] = []
                events[q].append(note.pitch)
    return events


if __name__ == "__main__":
    midi_files = []
    for (root, dirs, files) in os.walk("audio"):
        for name in files:
            if name.endswith(".mid"):
                midi_files.append(os.path.join(root, name))

    for midi in midi_files:
        print(midi)
        out = midi.replace(".mid", ".tsv")
        mid = pretty_midi.PrettyMIDI(midi)

        secs = get_events_seconds(mid)
        qs = get_events_quarterLength(mid)

        dfdict = {"m_offset": [], "m_offsetInSeconds": [], "m_notes": []}
        if len(secs) != len(qs):
            print(f"\t\tERROR: Different sequence length!!! ({len(secs)}, {len(qs)})")
        for (s, notes), (q, notes2) in zip(
            sorted(secs.items()), sorted(qs.items())
        ):
            if notes != notes2:
                print("\t\tERROR: Note list does not match!!!")
            dfdict["m_offset"].append(q)
            dfdict["m_offsetInSeconds"].append(s)
            dfdict["m_notes"].append(notes)
        
        df = pd.DataFrame(dfdict)
        df.set_index("m_offset", inplace=True)
        df.to_csv(out, sep="\t")
