import glob
import sys
# Imports from other files in this directory:
from corpusreader import CHILDESMorphFileReader
from match import Matcher, SentenceMatcher
from visualize import visualize


DATA_PATH = 'data'
AGE_ERROR_MSG = 'Age is None. Skipping file'


def analyze_sentence(speaker, matcher, sent, verbose):
    occ = 0
    if isinstance(matcher, SentenceMatcher):
        if matcher.match(sent):
            occ += 1
            if verbose:
                print(speaker, ':', ' '.join([word.form for word in sent]))
                print(sent)
    else:
        for entry in sent:
            if matcher.match(entry):
                occ += 1
                if verbose:
                    print(speaker, ':', ' '.join([word.form for word in sent]))
                    print(sent)
    return occ


def count_occurrences(corpus, matcher, results, verbose=True):
    age = corpus.age(month=True)[0]  # age in months
    if verbose:
        print(matcher)
        print(corpus.fileids(), age)
    if age is None:
        print(AGE_ERROR_MSG)
        sys.stderr.write('{}(s) {}.\n'.format(AGE_ERROR_MSG, corpus.fileids()))
        return results
    if age > 60:  # Data sparsity.
        print('Skipping file (age > 60 months).')
        return results

    n_utt_chi = 0  # number of utterances by the child
    n_occ_chi = 0  # number of occurrences of the feature in the child's speech
    for sent in corpus.tagged_morph_sents(speaker='CHI',
                                          strip_space=True
                                          ):
        n_utt_chi += 1
        n_occ_chi += analyze_sentence('CHI', matcher, sent, verbose)

    n_utt_par = 0  # number of utterances by the parent(s)
    n_occ_par = 0  # number of occurrences of the feature in the parent's speech
    for sent in corpus.tagged_morph_sents(speaker=['MOT', 'FAT'],
                                          strip_space=True
                                          ):
        n_utt_par += 1
        n_occ_par += analyze_sentence('PAR', matcher, sent, verbose)

    # Add the numbers of utterances/occurrences to the results dictionary.
    if n_utt_chi > 0:
        matcher_str = matcher.label
        try:  # Try to update an existing entry.
            prev_counts = results[matcher_str][age]
            results[matcher_str][age] = \
                [sum(x) for x in zip(prev_counts,
                                     (n_occ_chi, n_utt_chi,
                                      n_occ_par, n_utt_par))]
        except KeyError:  # New entry for results[matcher_str][age].
            try:
                results[matcher_str][age] = [n_occ_chi, n_utt_chi,
                                             n_occ_par, n_utt_par]
            except KeyError:  # New entry for results[matcher_str].
                results[matcher_str] = \
                    {age: [n_occ_chi, n_utt_chi, n_occ_par, n_utt_par]}

    if verbose:
        print('CHI: {} occurrences | {} utterances | ratio: {}'
              .format(n_occ_chi, n_utt_chi, n_occ_chi / n_utt_chi
                      if n_utt_chi > 0 else -1))
        print('PAR: {} occurrences | {} utterances | ratio: {}'
              .format(n_occ_par, n_utt_par, n_occ_par / n_utt_par
                      if n_utt_par > 0 else -1))
        print()
    return results


matchers = [Matcher('1. present participle', infl='PRESP'),
            Matcher('2./3. in', form='in'),
            Matcher('2./3. out', form='on'),
            Matcher('4. plural (regular)', infl_affix='PL', suffix='s'),
            Matcher('5. simple past (irregular)', infl_fusion='PAST'),
            Matcher('6. possessive -\'s/-s\'', post_rel='POSS',
                    suffix=['\'s', 's\'']),
            SentenceMatcher(Matcher('7. copula \'be\' (uncontractible)',
                                    tag='cop', stem='be',
                                    rel=['ROOT', 'COMP', 'INCROOT']),
                            'uncontractible'),
            Matcher('8. articles', form=['the', 'a', 'an']),
            Matcher('9. simple past (regular)', infl_affix='PAST',
                    suffix='ed'),
            Matcher('10. 3.SG.PRES (regular)', infl_affix='3S', suffix='s'),
            Matcher('11. 3.SG.PRES (irregular)', tag='v', infl_fusion='3S'),
            SentenceMatcher(Matcher('12. auxiliary \'be\' (uncontractible)',
                                    tag='aux', stem='be'),
                            'uncontractible'),
            Matcher('13. copula \'be\' (contractible)', sfx_tag='cop',
                    sfx='be', post_rel=['ROOT', 'COMP', 'INCROOT']),
            Matcher('14. auxiliary \'be\' (contractible)', sfx_tag='aux',
                    sfx='be', post_rel='AUX')
            ]

# Results:
# {query -> {age -> [n_occ_chi, n_utt_chi, n_occ_par, n_utt_par]}}
results = {}
for f in glob.glob('data/**/*.xml'):
    f = f.replace('\\', '/')[5:]
    sys.stderr.write('Reading {}.'.format(f))  # TODO delete
    for matcher in matchers:
        results = count_occurrences(CHILDESMorphFileReader(DATA_PATH, f),
                                    matcher,
                                    results)

visualize(results, compare_adult=False, filename='output/total', display=False)
visualize(results, compare_adult=True, filename='output/compare', display=False)
