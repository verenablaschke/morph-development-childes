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
from word import Word  # Import from this repository.

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
            # VB: Removed 'relation' keyword.
            strip_space=True,
            # VB: Removed 'replace' keyword since it appears to be broken.
        ):
        # VB: Updated description.
            """
            :return: the given file(s) as a list of
                sentences, each encoded as a list of ``(word,tag,stem,infl)`` tuples.
            :param speaker: If specified, select specific speaker(s) defined
                in the corpus. Default is 'ALL' (all participants). Common choices
                are 'CHI' (the child), 'MOT' (mother), ['CHI','MOT'] (exclude
                researchers)
            :param strip_space: If true, then strip trailing spaces from word
                tokens. Otherwise, leave the spaces on the tokens.
            :rtype: list(list(Word))
            """
            # VB: Removed 'sent = True', 'pos = True'
            if not self._lazy:
                return [
                    self._get_morph_words(  # VB: Changed method from _get_words.
                        fileid, speaker, strip_space
                    )
                    for fileid in self.abspaths(fileids)
                ]

            get_words = lambda fileid: self._get_morph_words(  # VB: Changed method from _get_words.
                fileid, speaker, strip_space
            )
            return LazyConcatenation(LazyMap(get_words, self.abspaths(fileids)))


    # NLTK's _get_words method.
    def _get_morph_words(
            self, fileid, speaker, strip_space  # VB: Removed stem/sent/pos/relation/replace keywords.
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
                skip = False  # VB: Skip replacements.
                # select speakers
                if speaker == 'ALL' or xmlsent.get('who') in speaker:
                    for xmlword in xmlsent.findall('.//{%s}w' % NS):

                        # VB: Added the following two 'if' blocks.
                        # VB: If a word is a replacement, update the previous
                        # entry with the replacement info, but do not add the
                        # current word as an entry.
                        if skip:
                            skip = False
                            entry = sents[-1]
                            entry.replacement = xmlword.text
                            sents[-1] = entry
                            continue
                        if xmlword.find('.//{%s}replacement' % NS):
                            skip = True

                        infl = None
                        suffixStem = None
                        suffixTag = None
                        # VB: Removed block for getting replaced words.
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
                            infl_type = ''  # VB: Added infl_type and the try/except clause.
                            try:
                                infl_type = xmlinfl.attrib['type']
                            except ValueError:
                                pass
                            infl = xmlinfl.text  # VB: Originally word += '-' + xmlinfl.text
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
                        # Removed 'if relation or pos:' check that encloses the code up until the 'relational' comment
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
                        word = Word(word, tag, stem, infl, infl_type)  # VB: Originally 'word = [word, tag]'
                        # relational
                        # the gold standard is stored in
                        # <mor></mor><mor type="trn"><gra type="grt">
                        # VB: Removed 'if relation == True:' block.
                        for xmlstem_rel in xmlword.findall(  # VB: From the original 'if relation == True:' block
                            './/{%s}mor/{%s}gra' % (NS, NS)
                        ):
                            word.rel = xmlstem_rel.get('relation')  # VB: Added.
                        try:
                            for xmlpost_rel in xmlword.findall(  # VB: From the original 'if relation == True:' block
                                './/{%s}mor/{%s}mor-post/{%s}gra' % (NS, NS, NS)
                            ):
                                word.post_rel = xmlpost_rel.get('relation')  # VB: Added.
                        except:
                            pass
                        sents.append(word)
                    # VB: Replaced the sent/relation check:
                    # if sent or relation:
                    #     results.append(sents)
                    # else:
                    #     results.extend(sents)
                    results.append(sents)
            return LazyMap(lambda x: x, results)
