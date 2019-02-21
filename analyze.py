import glob
from enum import Enum
from nltk.corpus.reader import CHILDESCorpusReader


DATA_PATH = 'data'


class Condition(Enum):
    MATCH = 0
    SUFFIX = 1


def match(query_word, query_condition, word):
    if query_condition == Condition.MATCH:
        return word == query_word
    elif query_condition == Condition.SUFFIX:
        return word.endswith('-' + query_word)
    else:
        raise ValueError('Condition {} does not exist.'
                         .format(query_condition))


def count_occurrences(corpus, query_word, query_condition, results, verbose=True):
    age = corpus.age(month=True)[0]
    if verbose:
        print(corpus.fileids(), age)
    n_sents = 0
    n_occ = 0
    for sent in corpus.tagged_morph_sents(speaker='CHI',
                                    strip_space=True,
                                    ):
        n_sents += 1
        for (word, _, stem, infl) in sent:
            if match(query_word, query_condition, word):
                n_occ += 1
        print(sent)
    if n_sents > 0:
        try:
            prev_counts = results[(query_word, query_condition)][age]
            results[(query_word, query_condition)][age] = [sum(x) for x in zip(prev_counts, (n_occ, n_sents))]
        except KeyError:
            try:
                results[(query_word, query_condition)][age] = [n_occ, n_sents]
            except KeyError:
                results[(query_word, query_condition)] = {age: [n_occ, n_sents]}

    if verbose:
        print(n_occ, n_sents, n_occ / n_sents if n_sents > 0 else 0)
        print()
    return results


# TODO traverse each file only once, i.e. one corpus reader per file


# queries = [('PRESP', Condition.SUFFIX),  # -ing
#            ('in', Condition.MATCH),
#            ('on', Condition.MATCH)]


from corpusreader import CHILDESMorphFileReader
# CHILDESMorphFileReader(DATA_PATH, 'Brown/Adam/020304.xml').tagged_morph_sents()

# results:
# {(query_word, query condition) -> {age -> [n_occ, n_sent]}}
results = {}
i = 0  # TODO del
for f in glob.glob('data/Brown/Adam/*.xml'):
    f = f.replace('\\', '/')[5:]
    results = count_occurrences(CHILDESMorphFileReader(DATA_PATH, f),
                                'PRESP',
                                Condition.SUFFIX,
                                results)
    results = count_occurrences(CHILDESMorphFileReader(DATA_PATH, f),
                                'on',
                                Condition.MATCH,
                                results)
    results = count_occurrences(CHILDESMorphFileReader(DATA_PATH, f),
                                'in',
                                Condition.MATCH,
                                results)
    i += 1  # TODO del
    if i > 3:
        break

for r in results:
    print(r, results[r])
