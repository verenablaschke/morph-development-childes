class Matcher:

    __slots__ = ['condition', 'form', 'infl', 'suffix', 'post_rel']

    def __init__(self, condition,
                 form=None, infl=None, suffix=None, post_rel=None):
        self.condition = condition
        self.form = form
        self.infl = infl
        self.suffix = suffix
        self.post_rel = post_rel

    def match(self, entry):
        return getattr(self, 'match_' + self.condition)(entry)

    def match_form(self, entry):
        return entry.form == self.form

    def match_suffix(self, entry):
        if isinstance(self.suffix, str):
            return entry.form.endswith(self.suffix)
        for sfx in self.suffix:
            if entry.form.endswith(sfx):
                return True
        return False

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
        return self.match_infl(entry, infl_type='sfxf') \
            and entry.replacement == ''

    def match_infl_suffix_expl(self, entry):
        return self.match_suffix(entry) and self.match_infl_affix(entry)

    def match_copula_uncontractible(self, entry):
        return entry.tag == 'cop' and entry.rel in ['ROOT', 'COMP'] \
            and entry.replacement == ''

    def match_3sg_irregular(self, entry):
        return entry.tag == 'v' and self.match_infl_fusion(entry)

    def match_postrel(self, entry):
        return entry.post_rel == self.post_rel

    def match_suffix_postrel(self, entry):
        return self.match_suffix(entry) and self.match_postrel(entry)

    def __str__(self):
        return 'Matcher({}, form={}, infl={}, suffix={})' \
               .format(self.condition, self.form, self.infl, self.suffix)


class SentenceMatcher:

    __slots__ = ['matcher', 'condition']

    def __init__(self, matcher, condition):
        self.matcher = matcher
        self.condition = condition

    def match(self, sent):
        return getattr(self, 'match_' + self.condition)(sent)

    def match_copula_uncontractible(self, sent):
        match = -1
        for i, entry in enumerate(sent):
            if self.matcher.match(entry):
                match = i
                break

        # No uncontracted copula.
        if match == - 1:
            return False

        # Sentence-initial/final copula.
        sent_last = len(sent) - 1
        if match == 0 or match == sent_last \
           or (match == sent_last - 1 and sent[-1].tag == 'PUNCT'):
            return True

        subj_pos = -1
        for i, entry in enumerate(sent):
            if entry.tag == 'SUBJ':
                subj_pos = i
                break

        # No subject; sentence is probably ungrammatical.
        if subj_pos == -1:
            return False

        # Probably a question with inversion.
        return match < subj_pos and sent[-1].form == '?'

    def __str__(self):
        return 'SentenceMatcher({}, {})' \
               .format(self.matcher, self.condition)
