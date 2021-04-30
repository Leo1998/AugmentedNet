import random


class TextureTemplate(object):
    supported_durations = [4.0, 2.0, 1.0]
    supported_number_of_notes = [3, 4]

    def __init__(self, duration, notes, intervals):
        self.numberOfNotes = len(notes)
        if duration not in self.supported_durations:
            raise ValueError("Wrong duration value for this template.")
        if self.numberOfNotes not in self.supported_number_of_notes:
            raise ValueError(
                "This template doesn't support that number of notes."
            )
        self.duration = duration
        self.notes = notes
        self.intervals = intervals
        self.header = (
            "s_offset,s_duration,s_measure,s_notes,s_intervals,s_isOnset\n"
        )
        if self.numberOfNotes == 3:
            self.template = self.templateTriad
        elif self.numberOfNotes == 4:
            self.template = self.templateSeventh

    def templateTriad(self):
        raise NotImplemented()

    def templateSeventh(self):
        raise NotImplemented()

    def __str__(self):
        return self.header + self.template()

    def __repr__(self):
        return str(self)


class BassSplit(TextureTemplate):
    def templateTriad(self):
        dur = self.duration / 2
        return f"""\
0.0,{dur},,['{self.notes[0]}'],[],[True]
{dur},{dur},,"['{self.notes[1]}', '{self.notes[2]}']",['{self.intervals[2]}'],"[True, True]"
"""

    def templateSeventh(self):
        dur = self.duration / 2
        return f"""\
0.0,{dur},,['{self.notes[0]}'],[],[True]
{dur},{dur},,"['{self.notes[1]}', '{self.notes[2]}', '{self.notes[3]}']","['{self.intervals[3]}', '{self.intervals[4]}']","[True, True, True]"
"""


class Alberti(TextureTemplate):
    def templateTriad(self):
        dur = self.duration / 4
        return f"""\
0.0,{dur},,['{self.notes[0]}'],[],[True]
{dur},{dur},,['{self.notes[2]}'],[],[True]
{dur*2},{dur},,['{self.notes[1]}'],[],[True]
{dur*3},{dur},,['{self.notes[2]}'],[],[True]
"""

    def templateSeventh(self):
        dur = self.duration / 4
        return f"""\
0.0,{dur},,['{self.notes[0]}'],[],[True]
{dur},{dur},,['{self.notes[3]}'],[],[True]
{dur*2},{dur},,['{self.notes[1]}'],[],[True]
{dur*3},{dur},,['{self.notes[2]}'],[],[True]
"""


class Syncopation(TextureTemplate):
    supported_durations = [4.0, 2.0]

    def templateTriad(self):
        dur = self.duration / 4
        return f"""\
0.0,{dur},,['{self.notes[2]}'],[],[True]
{dur},{dur*2},,['{self.notes[0]}'],[],[True]
{dur*3},{dur},,['{self.notes[1]}'],[],[True]
"""

    def templateSeventh(self):
        dur = self.duration / 4
        return f"""\
0.0,{dur},,['{self.notes[3]}'],[],[True]
{dur},{dur*2},,"['{self.notes[0]}', '{self.notes[1]}', '{self.notes[2]}']","['{self.intervals[0]}', '{self.intervals[1]}']","[True, True, True]"
{dur*3},{dur},,"['{self.notes[0]}', '{self.notes[1]}', '{self.notes[2]}']","['{self.intervals[0]}', '{self.intervals[1]}']","[True, True, True]"
"""


class BlockChord(TextureTemplate):
    def templateTriad(self):
        dur = self.duration
        return f"""\
0.0,{dur},,"['{self.notes[0]}', '{self.notes[1]}', '{self.notes[2]}']","['{self.intervals[0]}', '{self.intervals[1]}']","[True, True, True]"
"""

    def templateSeventh(self):
        dur = self.duration
        return f"""\
0.0,{dur},,"['{self.notes[0]}', '{self.notes[1]}', '{self.notes[2]}', '{self.notes[3]}']","['{self.intervals[0]}', '{self.intervals[1]}', '{self.intervals[2]}']","[True, True, True, True]"
"""


available_templates = {
    "BassSplit": BassSplit,
    "Alberti": Alberti,
    "Syncopation": Syncopation,
    "BlockChord": BlockChord,
}

available_durations = list(
    sorted(
        set(
            [
                d
                for t in available_templates.values()
                for d in t.supported_durations
            ]
        )
    )
)

available_number_of_notes = list(
    sorted(
        set(
            [
                n
                for t in available_templates.values()
                for n in t.supported_number_of_notes
            ]
        )
    )
)


def _getRelevantTemplates(duration, numberOfNotes):
    ret = []
    for template in available_templates.values():
        if (
            duration in template.supported_durations
            and numberOfNotes in template.supported_number_of_notes
        ):
            ret.append(template)
    return ret


def applyTextureTemplate(duration, notes, intervals, templateName=None):
    numberOfNotes = len(notes)
    if templateName:
        if templateName not in available_templates:
            raise KeyError()
        else:
            template = available_templates[templateName]
            return str(template(duration, notes, intervals))
    if (
        duration not in available_durations
        or numberOfNotes not in available_number_of_notes
    ):
        raise KeyError()
    relevantTemplates = _getRelevantTemplates(duration, numberOfNotes)
    return str(random.choice(relevantTemplates)(duration, notes, intervals))
