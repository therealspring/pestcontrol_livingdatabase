"""Scrub table fields."""
import os

from matplotlib import colors
from sklearn.cluster import Birch
import collections
import editdistance
import matplotlib.pyplot as plt
import numpy
import pandas

TABLE_PATH = 'plotdata.cotton.select.csv'
CLUSTER_RESOLUTION = 0.01


def main():
    """Entry point."""
    table = pandas.read_csv(
        TABLE_PATH, encoding='unicode_escape', engine='python')
    X = table[['long', 'lat']]
    print(X['long'].min(), X['long'].max())
    fig, ax = plt.subplots()
    brc = Birch(threshold=0.01, n_clusters=None)
    brc.fit(X.values)
    clusters = brc.predict(X.values)
    table['clusters'] = clusters

    #table.plot.scatter(y='lat', x='long', s=0.5)
    print('generating scatter plot')
    colorlist = list(colors.ColorConverter.colors.keys())
    for i, cluster in enumerate(numpy.unique(clusters)):
        df = table[table['clusters'] == cluster]
        df.plot.scatter(
            x='long', y='lat', ax=ax, s=0.01, marker='x',
            color=colorlist[i % len(colorlist)])
        ax.set_title(f'{os.path.basename(TABLE_PATH)} {len(clusters)} clusters\nwithin ${CLUSTER_RESOLUTION}^\\circ$ of each other')
    plt.savefig(
        f'{os.path.basename(os.path.splitext(TABLE_PATH)[0])}.png', dpi=600)


    name_to_edit_distance = collections.defaultdict(set)
    for cluster in numpy.unique(clusters):
        unique_names = table[
            table['clusters'] == cluster]['technician'].dropna().unique()

        # process this subset of names
        # first filter by names we've already identified
        [name_to_edit_distance[a].update([(editdistance.eval(a, b), b)
         for b in unique_names])
         for a in unique_names]

    print('generating edit distance')
    print(name_to_edit_distance[next(iter(name_to_edit_distance))])
    for max_edit_distance in range(1, 5):
        processed_set = set()
        with open(
                f'candidate_table_{max_edit_distance}.csv', 'w',
                encoding="ISO-8859-1") as candidate_table:
            for base_name, edit_distance_set in name_to_edit_distance.items():
                if base_name in processed_set:
                    continue
                processed_set.add(base_name)
                row = f'"{base_name}"'
                for edit_distance, name in sorted(edit_distance_set):
                    if name == base_name:
                        continue
                    if edit_distance > max_edit_distance:
                        break
                    processed_set.add(name)
                    row += f',"{name}"'
                candidate_table.write(f'{row}\n')

    return


    return

    for max_edit_distance in range(1, 10):
        print(f'max edit edit_distance {max_edit_distance}')
        table = pandas.read_csv(
            TABLE_PATH, encoding='unicode_escape', engine='python')
        all_names_df = table['region'].dropna().apply(lambda x: x.lower())
        names_by_count = all_names_df.value_counts()

        name_set = set(names_by_count.index)
        cross_product = {
            a: sorted(
                [(editdistance.eval(a, b), b) for b in name_set if a != b])
            for a in name_set}

        with open(f'candidate_table_{max_edit_distance}.csv', 'w', encoding="utf-8") as candidate_table:
            for name, count in zip(names_by_count.index, names_by_count):
                print(name, count)
                if name not in name_set:
                    continue
                name_set.remove(name)
                row = f'"{name}"'
                for edit_distance, candidate in cross_product[name]:
                    if candidate not in name_set:
                        continue
                    if edit_distance > max_edit_distance:
                        break
                    row += f',"{candidate}"'
                    name_set.remove(candidate)
                candidate_table.write(f'{row}\n')


if __name__ == '__main__':
    main()
