class Matcher:

    __slots__ = ['form', 'infl', 'infl_affix', 'infl_fusion',
                 'suffix', 'rel', 'post_rel', 'sfx', 'sfx_tag',
                 'tag', 'stem']

    def __init__(self,
                 form=None, infl=None, infl_affix=None, infl_fusion=None,
                 suffix=None, rel=None, sfx=None, sfx_tag=None,
                 post_rel=None, tag=None, stem=None):
        self.form = form
        self.infl = infl
        self.infl_affix = infl_affix
        if infl_affix:
            self.infl = infl_affix
        self.infl_fusion = infl_fusion
        if infl_fusion:
            self.infl = infl_fusion
        self.suffix = suffix
        self.rel = rel
        self.post_rel = post_rel
        self.tag = tag
        self.stem = stem
        self.sfx = sfx
        self.sfx_tag = sfx_tag

    def match(self, entry):
        if entry.replacement:
            return False
        for attr in self.__slots__:
            if not getattr(self, attr):  # Value is None/False -> skip.
                continue
            try:
                if not getattr(self, 'match_' + attr)(entry):
                    return False
            except AttributeError:
                pass
        return True

    def check_identity_or_in(self, entry, attr):
        comp = getattr(self, attr)
        entry_comp = getattr(entry, attr)
        if isinstance(comp, str):
            return comp == entry_comp
        for elem in comp:
            if elem == entry_comp:
                return True
        return False

    def match_form(self, entry):
        return self.check_identity_or_in(entry, 'form')

    def match_tag(self, entry):
        return self.check_identity_or_in(entry, 'tag')

    def match_sfx_tag(self, entry):
        return self.check_identity_or_in(entry, 'sfx_tag')

    def match_stem(self, entry):
        return self.check_identity_or_in(entry, 'stem')

    def match_suffix(self, entry):
        if isinstance(self.suffix, str):
            return entry.form.endswith(self.suffix)
        for sfx in self.suffix:
            if entry.form.endswith(sfx):
                return True
        return False

    def match_rel(self, entry):
        return self.check_identity_or_in(entry, 'rel')

    def match_post_rel(self, entry):
        return self.check_identity_or_in(entry, 'post_rel')

    # https://talkbank.org/manuals/MOR.html#Mor_Markers_Suffix
    def match_infl(self, entry, infl_type=None):
        return self.check_identity_or_in(entry, 'infl')

    # Morphologically/phonologically distinct inflectional affix.
    # https://talkbank.org/manuals/MOR.html#Mor_Markers_Suffix
    def match_infl_affix(self, entry):
        return entry.infl_type == 'sfx'

    # Inflectional morpheme(s) that is (are) fused with the stem.
    # https://talkbank.org/manuals/MOR.html#Mor_Markers_Suffix_Fusional
    def match_infl_fusion(self, entry):
        return entry.infl_type == 'sfxf'

    def __str__(self):
        attributes = []
        for attr in self.__slots__:
            val = getattr(self, attr)
            if val is None:
                continue
            attributes.append('{}={}'.format(attr, val))
        return 'Matcher{}'.format(attributes)


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
