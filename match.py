class Matcher:

    __slots__ = ['condition', 'form', 'infl', 'suffix', 'rel', 'post_rel',
                 'tag', 'stem']

    def __init__(self, condition,
                 form=None, infl=None, suffix=None, rel=None,
                 post_rel=None, tag=None, stem=None):
        self.condition = condition
        self.form = form
        self.infl = infl
        self.suffix = suffix
        self.rel = rel
        self.post_rel = post_rel
        self.tag = tag
        self.stem = stem

    # TODO This system works but it could be simplified a lot by deducing the
    # the 'condition' value from the instance variables that aren't None.

    def match(self, entry):
        return getattr(self, 'match_' + self.condition)(entry) \
            and entry.replacement == ''

    def match_form(self, entry):
        if isinstance(self.form, str):
            return entry.form == self.form
        for f in self.form:
            if entry.form == f:
                return True
        return False

    def match_suffix(self, entry):
        if isinstance(self.suffix, str):
            return entry.form.endswith(self.suffix)
        for sfx in self.suffix:
            if entry.form.endswith(sfx):
                return True
        return False

    def match_rel(self, entry):
        if isinstance(self.rel, str):
            return entry.rel == self.rel
        for r in self.rel:
            if entry.rel == r:
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

    def match_tag_rel_stem(self, entry):
        return self.match_tag(entry) and self.match_rel(entry) \
            and self.match_stem(entry)

    def match_tagorrel_stem(self, entry):
        # Used for checking for uncontractible auxiliary 'be'.
        # 'or' instead of 'and' because of tagging inconsistencies.
        return (self.match_tag(entry) or self.match_rel(entry)) \
            and self.match_stem(entry)

    def match_tag_infl_fusion(self, entry):
        return self.match_tag(entry) and self.match_infl_fusion(entry)

    def match_postrel(self, entry):
        return entry.post_rel == self.post_rel

    def match_suffix_postrel(self, entry):
        return self.match_suffix(entry) and self.match_postrel(entry)

    def match_tag(self, entry):
        return entry.tag == self.tag

    def match_stem(self, entry):
        return entry.stem == self.stem

    def __str__(self):
        msg = 'Matcher({}'.format(self.condition)
        for attr in self.__slots__:
            val = getattr(self, attr)
            if val is None:
                continue
            msg += ', {}={}'.format(attr, val)
        return msg + ')'


class SentenceMatcher:

    __slots__ = ['matcher', 'condition']

    def __init__(self, matcher, condition):
        self.matcher = matcher
        self.condition = condition

    def match(self, sent):
        return getattr(self, 'match_' + self.condition)(sent)

    def match_uncontractible(self, sent):
        match = -1
        for i, entry in enumerate(sent):
            if self.matcher.match(entry):
                if entry.sfx_tag == 'neg' or entry.infl == 'PAST':
                    return True
                match = i
                break

        # No uncontracted copula/auxiliary verb.
        if match == - 1:
            return False

        # Sentence-initial/final copula/aux.
        sent_last = len(sent) - 1
        if match == 0 or match == sent_last \
           or (match == sent_last - 1 and sent[-1].tag == 'PUNCT'):
            return True

        # We cannot easily determine whether it's (un)contractible.
        return False

    def __str__(self):
        return 'SentenceMatcher({}, {})' \
               .format(self.matcher, self.condition)
