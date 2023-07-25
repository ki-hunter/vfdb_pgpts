import numpy as np
import pandas as pd
import seaborn as sns
import sklearn 
import os
from pathlib import Path
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA


def data_import():
    
    cwd = os.getcwd()

    cwd_content = os.listdir(cwd)

    comparison_count_filenames = []

    for item in cwd_content:

        if "keggname_to_count" in item:

            comparison_count_filenames.append(item)

    comparison_count = {}

    for count_file in comparison_count_filenames:

        comparison_count.update({count_file : pd.read_csv(Path(f"{cwd}/{count_file}"), sep="\t", header=0, index_col=0)})

    return comparison_count



def pca(data:dict):
    df1 = data["Kosakonia_nr_default_comparison_hpath_keggname_to_count.txt"]

    principal = PCA(n_components=3)

    principal.fit(df1)

    x = principal.transform(df1)

    print(x.shape)

    print(principal.components_)

    plt.figure(figsize=(10,10))
    plt.scatter(x[:,0], x[:,1])
    plt.xlabel("pc1")
    plt.ylabel("pc2")

    pass



def kmeans():
    pass



def dataviz():
    pass



def main():
    
    pca(data_import())

    pass


if __name__ == '__main__':
    main()

