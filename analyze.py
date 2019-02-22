import glob
from enum import Enum
# Imports from other files in this directory:
from corpusreader import CHILDESMorphFileReader
from match import Matcher


DATA_PATH = 'data'


def count_occurrences(corpus, matcher, results, verbose=True):
    age = corpus.age(month=True)[0]
    if verbose:
        print(corpus.fileids(), age)
    n_sents = 0
    n_occ = 0
    for sent in corpus.tagged_morph_sents(speaker='CHI',
                                          strip_space=True,
                                          ):
        n_sents += 1
        for entry in sent:
            if matcher.match(entry):
                n_occ += 1
            print(sent)
    if n_sents > 0:
        matcher_str = matcher.__str__()
        try:
            prev_counts = results[matcher_str][age]
            results[matcher_str][age] = \
                [sum(x) for x in zip(prev_counts, (n_occ, n_sents))]
        except KeyError:
            try:
                results[matcher_str][age] = [n_occ, n_sents]
            except KeyError:
                results[matcher_str] = \
                    {age: [n_occ, n_sents]}

    if verbose:
        print(n_occ, n_sents, n_occ / n_sents if n_sents > 0 else 0)
        print()
    return results


# TODO traverse each file only once, i.e. one corpus reader per file


# queries = [('PRESP', Condition.INFL),  # -ing
#            ('in', Condition.MATCH),
#            ('on', Condition.MATCH)]


# results:
# {(query_word, query condition) -> {age -> [n_occ, n_sent]}}
results = {}
i = 0  # TODO del
for f in glob.glob('data/Brown/Adam/*.xml'):
    f = f.replace('\\', '/')[5:]
    results = count_occurrences(CHILDESMorphFileReader(DATA_PATH, f),
                                Matcher('infl', 'PRESP'),
                                results)
    results = count_occurrences(CHILDESMorphFileReader(DATA_PATH, f),
                                Matcher('form', 'in'),
                                results)
    results = count_occurrences(CHILDESMorphFileReader(DATA_PATH, f),
                                Matcher('form', 'on'),
                                results)
    i += 1  # TODO del
    if i > 3:
        break

for r in results:
    print(r, results[r])
