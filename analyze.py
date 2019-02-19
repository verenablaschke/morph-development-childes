import nltk
from nltk.corpus.reader import CHILDESCorpusReader

DATA_PATH = 'data'


def count_occurrences(corpus, query_word, verbose=True):
    if verbose:
        print(corpus.fileids(), corpus.age(month=True))
    n_sents = 0
    n_occ = 0
    for sent in corpus.tagged_sents(speaker='CHI',
                                    strip_space=True,
                                    stem=True   # Inflection details.
                                    ):
        n_sents += 1
        for (word, _) in sent:
            if word == query_word:
                n_occ += 1
    if verbose:
        print(n_occ, n_sents, n_occ / n_sents if n_sents > 0 else 0)
        print()
    return n_occ, n_sents


instances = []
for year in range(6):
    for month in range(1, 13):
        age = year * 12 + month
        n_occ, n_sents = count_occurrences(
            corpus=CHILDESCorpusReader(DATA_PATH,
                                       '.*/.*/{:02d}{:02d}.*.xml'
                                       .format(year, month)),
            query_word='on')
        if n_sents > 0:
            instances.append((age, n_occ, n_sents))

for i in instances:
    print(i)
