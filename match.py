class Matcher:

    __slots__ = ['condition', 'query']

    def __init__(self, condition, query):
        self.condition = condition
        self.query = query

    def match(self, entry):
        return getattr(self, 'match_' + self.condition)(entry)

    def match_form(self, entry):
        return entry[0] == self.query

    # https://talkbank.org/manuals/MOR.html#Mor_Markers_Suffix
    def match_infl(self, entry, infl_type=None):
        return entry[3] == self.query \
            and (infl_type is None or entry[4] == infl_type)

    # Morphologically/phonologically distinct inflectional affix.
    # https://talkbank.org/manuals/MOR.html#Mor_Markers_Suffix
    def match_infl_affix(self, entry):
        return self.match_infl(entry, infl_type='sfx')

    # Inflectional morpheme(s) that is (are) fused with the stem.
    # https://talkbank.org/manuals/MOR.html#Mor_Markers_Suffix_Fusional
    def match_infl_fusion(self, entry):
        return self.smatch_infl(entry, infl_type='sfxf')

    def __str__(self):
        return 'Matcher({}, {})'.format(self.condition, self.query)
