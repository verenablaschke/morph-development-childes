class Word:

    __slots__ = ['form', 'tag', 'stem', 'infl', 'infl_type', 'replacement',
                 'rel', 'post_rel', 'sfx_form', 'sfx_tag']

    def __init__(self, form, tag, stem, infl, infl_type,
                 replacement='', rel='', post_rel=''):
        # Deal with cases like 'what's~be'.
        if '~' in form:
            morphs = form.split('~')
            self.form = morphs[0]
            self.sfx_form = morphs[1]
        # Deal with cases like 'pro:int~cop'.
        else:
            self.form = form
            self.sfx_form = ''
        if '~' in tag:
            morphs = tag.split('~')
            self.tag = morphs[0]
            self.sfx_tag = morphs[1]
        else:
            self.tag = tag
            self.sfx_tag = ''
        self.stem = stem
        self.infl = infl
        self.infl_type = infl_type
        self.replacement = replacement
        self.rel = rel
        self.post_rel = post_rel

    def __str__(self):
        return '<{}, {}, {} | {}, {} | {} | {}, {} | {}, {}>' \
               .format(self.form, self.tag, self.stem, self.infl,
                       self.infl_type, self.replacement, self.rel,
                       self.post_rel, self.sfx_form, self.sfx_tag)

    def __repr__(self):
        return self.__str__()
