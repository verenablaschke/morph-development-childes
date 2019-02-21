# A modified version of NLTK's CHILDESCorpusReader that returns the originally
# used words as well as their stemmed and morphologically analyzed versions at
# the same time. Instead of calling tagged_sents() twice (once with stem=True
# and once with stem=False) and thus traversing the corpus twice, it is suffi-
# cient to only call tagged_morph_sents() once.

# This mode contains modified parts NLTK's source code, which can be found
# here: <http://www.nltk.org/_modules/nltk/corpus/reader/childes.html>.
# The original code and this version are both distributed under an
# Apache 2.0 License <https://github.com/nltk/nltk/blob/develop/LICENSE.txt>,
# <http://www.apache.org/licenses/LICENSE-2.0>.
# NLTK's parts of the code are marked in this document. The same applies to my
# modifications of the code, which are marked with comments starting with 'VB'.

# Header of the nltk.corpus.reader.childes file:

# CHILDES XML Corpus Reader

# Copyright (C) 2001-2019 NLTK Project
# Author: Tomonori Nagano <tnagano@gc.cuny.edu>
#         Alexis Dimitriadis <A.Dimitriadis@uu.nl>
# URL: <http://nltk.org/>
# For license information, see LICENSE.TXT


from nltk.corpus.reader import CHILDESCorpusReader
from nltk.corpus.reader.xmldocs import ElementTree
from nltk.util import LazyMap, LazyConcatenation

# From nltk.corpus.reader.childes:
# to resolve the namespace issue
NS = 'http://www.talkbank.org/ns/talkbank'


class CHILDESMorphFileReader(CHILDESCorpusReader):

    # NLTK's tagged_sents method.
    def tagged_morph_sents(  # VB: Changed method name.
            self,
            fileids=None,
            speaker='ALL',
            # VB: Removed 'stem' keyword.
            relation=None,
            strip_space=True,
            replace=False,
        ):
        # VB: Updated description of the returned tuple to include stem, infl.
            """
            :return: the given file(s) as a list of
                sentences, each encoded as a list of ``(word,tag,stem,infl)`` tuples.
            :rtype: list(list(tuple(str,str)))

            :param speaker: If specified, select specific speaker(s) defined
                in the corpus. Default is 'ALL' (all participants). Common choices
                are 'CHI' (the child), 'MOT' (mother), ['CHI','MOT'] (exclude
                researchers)
            :param relation: If true, then return tuples of ``(str,pos,relation_list)``.
                If there is manually-annotated relation info, it will return
                tuples of ``(str,pos,test_relation_list,str,pos,gold_relation_list)``
            :param strip_space: If true, then strip trailing spaces from word
                tokens. Otherwise, leave the spaces on the tokens.
            :param replace: If true, then use the replaced (intended) word instead
                of the original word (e.g., 'wat' will be replaced with 'watch')
            """
            sent = True
            pos = True
            if not self._lazy:
                return [
                    self._get_morph_words(  # VB: Changed method from _get_words.
                        fileid, speaker, sent, relation, pos, strip_space, replace
                    )
                    for fileid in self.abspaths(fileids)
                ]

            get_words = lambda fileid: self._get_morph_words(  # VB: Changed method from _get_words.
                fileid, speaker, sent, relation, pos, strip_space, replace
            )
            return LazyConcatenation(LazyMap(get_words, self.abspaths(fileids)))


    # NLTK's _get_words method.
    def _get_morph_words(
            self, fileid, speaker, sent, relation, pos, strip_space, replace  # VB: Removed 'stem' keyword.
        ):
            if (
                isinstance(speaker, str) and speaker != 'ALL'  # VB: Changed six.string_types to str.
            ):  # ensure we have a list of speakers
                speaker = [speaker]
            xmldoc = ElementTree.parse(fileid).getroot()
            # processing each xml doc
            results = []
            for xmlsent in xmldoc.findall('.//{%s}u' % NS):
                sents = []
                # select speakers
                if speaker == 'ALL' or xmlsent.get('who') in speaker:
                    for xmlword in xmlsent.findall('.//{%s}w' % NS):
                        infl = None
                        suffixStem = None
                        suffixTag = None
                        # getting replaced words
                        if replace and xmlsent.find('.//{%s}w/{%s}replacement' % (NS, NS)):
                            xmlword = xmlsent.find(
                                './/{%s}w/{%s}replacement/{%s}w' % (NS, NS, NS)
                            )
                        elif replace and xmlsent.find('.//{%s}w/{%s}wk' % (NS, NS)):
                            xmlword = xmlsent.find('.//{%s}w/{%s}wk' % (NS, NS))
                        # get text
                        if xmlword.text:
                            word = xmlword.text
                        else:
                            word = ''
                        # strip tailing space
                        if strip_space:
                            word = word.strip()
                        # stem
                        infl, stem = '', ''  # VB: Added.
                        # VB: Removed 'if' clause testing for stem==True.
                        try:
                            xmlstem = xmlword.find('.//{%s}stem' % NS)
                            stem = xmlstem.text  # VB: Changed 'word' to 'stem'.
                        except AttributeError as e:
                            pass
                        # if there is an inflection
                        try:
                            xmlinfl = xmlword.find(
                                './/{%s}mor/{%s}mw/{%s}mk' % (NS, NS, NS)
                            )
                            infl = '-' + xmlinfl.text  # VB: Originally word += '-' + xmlinfl.text
                        except:
                            pass
                        # if there is a suffix
                        try:
                            xmlsuffix = xmlword.find(
                                './/{%s}mor/{%s}mor-post/{%s}mw/{%s}stem'
                                % (NS, NS, NS, NS)
                            )
                            suffixStem = xmlsuffix.text
                        except AttributeError:
                            suffixStem = ""
                        if suffixStem:
                            word += "~" + suffixStem
                        # pos
                        if relation or pos:
                            try:
                                xmlpos = xmlword.findall(".//{%s}c" % NS)
                                xmlpos2 = xmlword.findall(".//{%s}s" % NS)
                                if xmlpos2 != []:
                                    tag = xmlpos[0].text + ":" + xmlpos2[0].text
                                else:
                                    tag = xmlpos[0].text
                            except (AttributeError, IndexError) as e:
                                tag = ""
                            try:
                                xmlsuffixpos = xmlword.findall(
                                    './/{%s}mor/{%s}mor-post/{%s}mw/{%s}pos/{%s}c'
                                    % (NS, NS, NS, NS, NS)
                                )
                                xmlsuffixpos2 = xmlword.findall(
                                    './/{%s}mor/{%s}mor-post/{%s}mw/{%s}pos/{%s}s'
                                    % (NS, NS, NS, NS, NS)
                                )
                                if xmlsuffixpos2:
                                    suffixTag = (
                                        xmlsuffixpos[0].text + ":" + xmlsuffixpos2[0].text
                                    )
                                else:
                                    suffixTag = xmlsuffixpos[0].text
                            except:
                                pass
                            if suffixTag:
                                tag += "~" + suffixTag
                            word = (word, tag, stem, infl)  # VB: Added stem, infl.
                        # relational
                        # the gold standard is stored in
                        # <mor></mor><mor type="trn"><gra type="grt">
                        # VB: Did not change the following part to keep the inflec-
                        # tion information, as it is not necessary for my current
                        # project.
                        if relation == True:
                            for xmlstem_rel in xmlword.findall(
                                './/{%s}mor/{%s}gra' % (NS, NS)
                            ):
                                if not xmlstem_rel.get('type') == 'grt':
                                    word = (
                                        word[0],
                                        word[1],
                                        xmlstem_rel.get('index')
                                        + "|"
                                        + xmlstem_rel.get('head')
                                        + "|"
                                        + xmlstem_rel.get('relation'),
                                    )
                                else:
                                    word = (
                                        word[0],
                                        word[1],
                                        word[2],
                                        word[0],
                                        word[1],
                                        xmlstem_rel.get('index')
                                        + "|"
                                        + xmlstem_rel.get('head')
                                        + "|"
                                        + xmlstem_rel.get('relation'),
                                    )
                            try:
                                for xmlpost_rel in xmlword.findall(
                                    './/{%s}mor/{%s}mor-post/{%s}gra' % (NS, NS, NS)
                                ):
                                    if not xmlpost_rel.get('type') == 'grt':
                                        suffixStem = (
                                            suffixStem[0],
                                            suffixStem[1],
                                            xmlpost_rel.get('index')
                                            + "|"
                                            + xmlpost_rel.get('head')
                                            + "|"
                                            + xmlpost_rel.get('relation'),
                                        )
                                    else:
                                        suffixStem = (
                                            suffixStem[0],
                                            suffixStem[1],
                                            suffixStem[2],
                                            suffixStem[0],
                                            suffixStem[1],
                                            xmlpost_rel.get('index')
                                            + "|"
                                            + xmlpost_rel.get('head')
                                            + "|"
                                            + xmlpost_rel.get('relation'),
                                        )
                            except:
                                pass
                        sents.append(word)
                    if sent or relation:
                        results.append(sents)
                    else:
                        results.extend(sents)
            return LazyMap(lambda x: x, results)
