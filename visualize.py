import copy
import matplotlib.pyplot as plt
import numpy as np
import sys
# from enum import Enum


EMPTY_MONTH_MSG = 'No {}entries for month {}, query={}.'


# class Person(Enum):
#     CHI = 0
#     PARENT = 1
#     BOTH = 2


def valid(r, query, compare_adult, month, comp_idx):
    if r[month][comp_idx] is None or r[month][comp_idx] <= 0:
        msg = EMPTY_MONTH_MSG.format('adult ' if compare_adult
                                     else '', month, query)
        print(msg)
        sys.stderr.write(msg + '\n')
        return False
    return True


def visualize(results, compare_adult,
              display=True, filename=None, verbose=True):
    if verbose:
        print()
        print('--- Visualizing', filename)

    # Set up the plot.
    fig, ax = plt.subplots()
    plots = []
    cmap = plt.get_cmap('jet')
    colours = cmap(np.linspace(0, 1.0, len(results)))

    min_month, max_month = -1, -1  # earliest/latest month

    for (query, r), col in zip(results.items(), colours):
        months = sorted(r.keys())
        if verbose:
            print(query, [(key, r[key]) for key in months])

        # Get the dimensions of the graph.
        if min_month == -1 or min_month > months[0]:
            min_month = months[0]
        if max_month < months[-1]:
            max_month = months[-1]

        # Check if there is at least one child(/parent) utterance per month.
        months_ok = []
        entries_ok = []
        for month in months:
            if not valid(r, query, compare_adult, month, comp_idx=0):  # >=1 utterance?
                continue
            months_ok.append(month)
            if verbose:
                print('month:', month, 'entries:', r[month])
            chi = r[month][0] / r[month][1]
            if compare_adult:
                if not valid(r, query, compare_adult, month, comp_idx=2):  # >=1 adult utterance?
                    months_ok = months_ok[:-1]
                    continue
                chi = chi / (r[month][2] / r[month][3])
            entries_ok.append(chi)

        if verbose:
            print('months_ok', months_ok)
            print('entries_ok', entries_ok)

        plot, = plt.plot(months_ok, entries_ok, color=col, label=query)
        plots.append(plot)

    # Prepare the grid and mark full years.
    plt.grid()
    xticks = np.arange(min_month, max_month + 1, step=3).tolist()
    xtick_labels = copy.deepcopy(xticks)
    for y in range(2, 6):
        plt.axvline(x=y * 12, color='k')
        try:
            xtick_labels[xticks.index(y * 12)] = '{} yrs'.format(y)
        except ValueError:
            xticks.append(y * 12)
            xtick_labels.append('{} yrs'.format(y))

    ax.set_xticks(xticks)
    ax.set_xticklabels(xtick_labels)
    if compare_adult:
        ylabel = 'Occurrences per adult utterance'
    else:
        ylabel = 'Occurrences per utterance'
    ax.set(xlabel='Age in months',
           ylabel=ylabel,
           title='')
    plt.legend(handles=plots, loc=2)
    if filename is not None:
        fig = plt.gcf()
        fig.set_size_inches(18, 9)
        fig.savefig(filename + '.png', bbox_inches='tight', dpi=400)
    if display:
        plt.show()
