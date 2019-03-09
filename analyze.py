import glob
import sys
# Imports from other files in this directory:
from corpusreader import CHILDESMorphFileReader
from match import Matcher, SentenceMatcher
from visualize import visualize


DATA_PATH = 'data'
AGE_ERROR_MSG = 'Age is None. Skipping file'


def count_occurrences(corpus, matcher, results, verbose=True):
    age = corpus.age(month=True)[0]  # age in months
    if verbose:
        print(matcher)
        print(corpus.fileids(), age)
    if age is None:
        print(AGE_ERROR_MSG)
        sys.stderr.write('{}(s) {}.\n'.format(AGE_ERROR_MSG, corpus.fileids()))
        return results

    n_utt_chi = 0  # number of utterances by the child
    n_occ_chi = 0  # number of occurrences of the feature in the child's speech
    for sent in corpus.tagged_morph_sents(speaker='CHI',
                                          strip_space=True
                                          ):
        # print(sent)  # TODO del
        n_utt_chi += 1
        if isinstance(matcher, SentenceMatcher):
            if matcher.match(sent):
                n_occ_chi += 1
                if verbose:
                    print('CHI:', sent)
        else:
            for entry in sent:
                if matcher.match(entry):
                    n_occ_chi += 1
                    if verbose:
                        print('CHI:', sent)

    n_utt_par = 0  # number of utterances by the parent(s)
    n_occ_par = 0  # number of occurrences of the feature in the parent's speech
    for sent in corpus.tagged_morph_sents(speaker=['MOT', 'FAT'],
                                          strip_space=True
                                          ):
        n_utt_par += 1
        for entry in sent:
            if matcher.match(entry):
                n_occ_par += 1
                if verbose:
                    print('ADULT:', sent)

    # Add the numbers of utterances/occurrences to the results dictionary.
    if n_utt_chi > 0:  # TODO smooth?
        matcher_str = matcher.__str__()
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


matchers = [Matcher('infl', infl='PRESP'),                       # 1. -ing
            Matcher('form', form='in'),                          # 2./3. in
            Matcher('form', form='on'),                          # 2./3. on
            Matcher('infl_suffix_expl', infl='PL', suffix='s'),  # 4. regular PL
            Matcher('infl_fusion', infl='PAST'),                 # 5. irregular PAST
            # TODO fix POSS query
            Matcher('infl_suffix_expl', infl='POSS', suffix='\'s'),  # 6. POSS
            SentenceMatcher(Matcher('copula_uncontractible'), 'copula_uncontractible'),  # 7. uncontractible COP
            Matcher('form', form='the'),                         # 8. the, a
            Matcher('form', form='a'),                           # 8. the, a
            Matcher('infl_suffix_expl', infl='PAST', suffix='ed'),  # 9. regular PAST
            Matcher('infl_suffix_expl', infl='3S', suffix='s'),  # 10. regular 3.SG
            Matcher('3sg_irregular', infl='3S'),  # 11. irregular 3.SG
            # 12. uncontractible AUX
            # 13. contractible COP
            # 14. contractible AUX
            ]

# Results:
# {query -> {age -> [n_occ_chi, n_utt_chi, n_occ_par, n_utt_par]}}
results = {}
# for f in glob.glob('data/*/*/*.xml'):
# for f in glob.glob('data/Brown/Adam/*.xml'):
for f in glob.glob('data/test.xml'):
    f = f.replace('\\', '/')[5:]
    for matcher in matchers:
        results = count_occurrences(CHILDESMorphFileReader(DATA_PATH, f),
                                    matcher,
                                    results)

# visualize(results, compare_adult=False)
# visualize(results, compare_adult=True)
# visualize(results, compare_adult=False, filename='output/total.png')
# visualize(results, compare_adult=True, filename='output/adult.png')
