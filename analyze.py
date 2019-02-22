import glob
import numpy as np
import matplotlib.pyplot as plt
# Imports from other files in this directory:
from corpusreader import CHILDESMorphFileReader
from match import Matcher


DATA_PATH = 'data'


def count_occurrences(corpus, matcher, results, verbose=True):
    age = corpus.age(month=True)[0]
    if verbose:
        print(matcher)
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
                if verbose:
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
matchers = [Matcher('infl', infl='PRESP'),                       # 1. -ing
            Matcher('form', form='in'),                          # 2./3. in
            Matcher('form', form='on'),                          # 2./3. on
            Matcher('infl_suffix_expl', infl='PL', suffix='s'),  # 4. PL -s
            Matcher('infl_fusion', infl='PAST'),                 # 5. irregular PAST
            # TODO fix POSS query
            Matcher('infl_suffix_expl', infl='POSS', suffix='\'s'),  # 6. POSS 's
            # # 7. is, are when uncontractable
            Matcher('form', form='the'),                         # 8. the, a
            Matcher('form', form='a'),                           # 8. the, a
            Matcher('infl_suffix_expl', infl='PAST', suffix='ed'),  # 9. regular PAST
            Matcher('infl_suffix_expl', infl='3S', suffix='s')  # 10. 3.SG -s
            ]

# results:
# {query -> {age -> [n_occ, n_sent]}}
results = {}
i = 0  # TODO del
for f in glob.glob('data/Brown/Adam/*.xml'):
    f = f.replace('\\', '/')[5:]
    for matcher in matchers:
        results = count_occurrences(CHILDESMorphFileReader(DATA_PATH, f),
                                    matcher,
                                    results)

    # i += 1  # TODO del
    # if i > 2:
        # break

# Visualization of the results
fig, ax = plt.subplots()
plots = []
cmap = plt.get_cmap('jet')
n_plots = len(results)
colours = cmap(np.linspace(0, 1.0, n_plots))
i = 1

for (query, r), col in zip(results.items(), colours):
    print(query, r)
    months = r.keys()
    plot, = plt.plot(months, [r[month][0] / r[month][1] for month in months],
                     color=col, label=query)
    plots.append(plot)
    i += 1

ax.set(xlabel='Age in months',
       ylabel='Occurrences per utterance',
       title='')
plt.legend(handles=plots, loc=2)
plt.show()
# plt.savefig('filename.png', bbox_inches='tight')
