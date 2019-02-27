import copy
import matplotlib.pyplot as plt
import numpy as np
import sys


EMPTY_MONTH_MSG = 'No {}entries for month {}, query={}.'


def valid(r, month, comp_idx):
    if r[month][comp_idx] is None or r[month][comp_idx] <= 0:
        msg = EMPTY_MONTH_MSG.format('' if compare_total else 'adult ',
                                     month, query)
        print(msg)
        sys.stderr.write(msg + '\n')
        return False
    return True



def visualize(results, compare_total, display=True, filename=None):
    fig, ax = plt.subplots()
    plots = []
    cmap = plt.get_cmap('jet')
    n_plots = len(results)
    colours = cmap(np.linspace(0, 1.0, n_plots))
    i = 1

    if compare_total:
        comp_idx = 2
    else:
        comp_idx = 1

    min_month, max_month = -1, -1

    for (query, r), col in zip(results.items(), colours):
        print(query, r)
        months = sorted(r.keys())

        # Get the dimensions of the graph.
        if min_month == -1 or min_month > months[0]:
            min_month = months[0]
        if max_month < months[-1]:
            max_month = months[-1]

        months_ok = []
        entries_ok = []
        for month in months:
            if not valid(r, month, comp_idx=2):  # >1 utterance?
                continue
            months_ok.append(month)
            chi = r[month][0] / r[month][2]
            if not compare_total:
                if not valid(r, month, comp_idx=1):  # >1 adult utterance?
                    continue
                chi = chi / (r[month][1] / r[month][2])
            entries_ok.append(chi)

        plot, = plt.plot(months_ok, entries_ok, color=col, label=query)
        plots.append(plot)
        i += 1

    plt.grid()
    xticks = np.arange(min_month, max_month + 1, step=3).tolist()
    xtick_labels = copy.deepcopy(xticks)
    for y in range(2, 6):
        plt.axvline(x=y * 12, color='r')
        xticks.append(y * 12)
        xtick_labels[-1] = '{} yrs'.format(y)

    ax.set_xticks(xticks)
    ax.set_xticklabels(xtick_labels)
    if compare_total:
        ylabel = 'Occurrences per utterance'
    else:
        ylabel = 'Occurrences per adult utterance'
    ax.set(xlabel='Age in months',
           ylabel=ylabel,
           title='')
    plt.legend(handles=plots, loc=2)
    if display:
        plt.show()
    if filename is not None:
        plt.savefig(filename, bbox_inches='tight')
