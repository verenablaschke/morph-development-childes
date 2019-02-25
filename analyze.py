import glob
import sys
# Imports from other files in this directory:
from corpusreader import CHILDESMorphFileReader
from match import Matcher
from visualize import visualize


DATA_PATH = 'data'
AGE_ERROR_MSG = 'Age is None. Skipping file'


def count_occurrences(corpus, matcher, results, verbose=True):
    age = corpus.age(month=True)[0]
    if verbose:
        print(matcher)
        print(corpus.fileids(), age)
    if age is None:
        print(AGE_ERROR_MSG)
        sys.stderr.write('{}(s) {}.\n'.format(AGE_ERROR_MSG, corpus.fileids()))
        return results
    n_sents = 0
    n_occ = 0
    for sent in corpus.tagged_morph_sents(speaker='CHI',
                                          strip_space=True,
                                          ):
        n_sents += 1
        for entry in sent:
            if matcher.match(entry):
                n_occ += 1
                if verbose:
                    print(sent)
    n_adult = 0
    for sent in corpus.tagged_morph_sents(speaker=['MOT', 'FAT', 'INV'],
                                          strip_space=True,
                                          ):
        for entry in sent:
            if matcher.match(entry):
                n_adult += 1
                if verbose:
                    print('ADULT:', sent)
    if n_sents > 0:  # TODO smooth?
        matcher_str = matcher.__str__()
        try:
            prev_counts = results[matcher_str][age]
            results[matcher_str][age] = \
                [sum(x) for x in zip(prev_counts, (n_occ, n_adult, n_sents))]
        except KeyError:
            try:
                results[matcher_str][age] = [n_occ, n_adult, n_sents]
            except KeyError:
                results[matcher_str] = \
                    {age: [n_occ, n_adult, n_sents]}

    if verbose:
        print(n_occ, n_adult, n_sents,
              n_occ / n_sents if n_sents > 0 else -1,
              n_occ / n_adult if n_adult > 0 else -1)
        print()
    return results


matchers = [Matcher('infl', infl='PRESP'),                       # 1. -ing
            Matcher('form', form='in'),                          # 2./3. in
            Matcher('form', form='on'),                          # 2./3. on
            Matcher('infl_suffix_expl', infl='PL', suffix='s'),  # 4. PL -s
            Matcher('infl_fusion', infl='PAST'),                 # 5. irregular PAST
            # TODO fix POSS query
            # Matcher('infl_suffix_expl', infl='POSS', suffix='\'s'),  # 6. POSS 's
            # TODO: 7. is, are when uncontractable  -> only verb in sentence, maybe can also be determined via dependency info?
            Matcher('form', form='the'),                         # 8. the, a
            Matcher('form', form='a'),                           # 8. the, a
            Matcher('infl_suffix_expl', infl='PAST', suffix='ed'),  # 9. regular PAST
            Matcher('infl_suffix_expl', infl='3S', suffix='s')  # 10. 3.SG -s
            ]

# results:
# {query -> {age -> [n_occ, n_sent]}}
results = {}
for f in glob.glob('data/*/*/*.xml'):
    f = f.replace('\\', '/')[5:]
    for matcher in matchers:
        results = count_occurrences(CHILDESMorphFileReader(DATA_PATH, f),
                                    matcher,
                                    results)

visualize(results, compare_total=True, filename='output/total.png')
visualize(results, compare_total=False, filename='output/adult.png')
