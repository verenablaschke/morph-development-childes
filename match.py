class Matcher:

    __slots__ = ['condition', 'form', 'infl', 'suffix']

    def __init__(self, condition, form=None, infl=None, suffix=None):
        self.condition = condition
        self.form = form
        self.infl = infl
        self.suffix = suffix

    def match(self, entry):
        return getattr(self, 'match_' + self.condition)(entry)

    def match_form(self, entry):
        return entry.form == self.form

    def match_suffix(self, entry):
        return entry.form.endswith(self.suffix)

    # https://talkbank.org/manuals/MOR.html#Mor_Markers_Suffix
    def match_infl(self, entry, infl_type=None):
        return entry.infl == self.infl \
            and (infl_type is None or entry.infl_type == infl_type)

    # Morphologically/phonologically distinct inflectional affix.
    # https://talkbank.org/manuals/MOR.html#Mor_Markers_Suffix
    def match_infl_affix(self, entry):
        return self.match_infl(entry, infl_type='sfx')

    # Inflectional morpheme(s) that is (are) fused with the stem.
    # https://talkbank.org/manuals/MOR.html#Mor_Markers_Suffix_Fusional
    def match_infl_fusion(self, entry):
        return self.match_infl(entry, infl_type='sfxf')

    def match_infl_suffix_expl(self, entry):
        return self.match_suffix(entry) and self.match_infl_affix(entry)

    def match_copula_uncontractible(self, entry):
        return entry.tag == 'cop' and entry.rel in ['ROOT', 'COMP']

    def __str__(self):
        return 'Matcher({}, form={}, infl={}, suffix={})' \
               .format(self.condition, self.form, self.infl, self.suffix)
