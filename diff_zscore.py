import os
from pathlib import Path
def zscore_filter():
    """\
    Given a Z-Score chart with 2 zscore values of PGP and Pathogen for each KEGG id is filtered for:
    - absence of pgp/presence of pathogen
    - higher pathogen score than pgp
    the filtered KEGG ids are saved in files
    """
    cwd = os.getcwd()
    next_dir = cwd + "/Pseudomonas_analysis/"
    dir_content = os.listdir(Path(next_dir))
    print(dir_content)
    # print(pathlib.Path.resolve(__file__))

    zscore_file_missing = not("912_pseudomonas_zscores.txt" in dir_content)

    if zscore_file_missing:
        print("missing zscore file")
        exit()

    zscore_file = open(Path(next_dir + "912_pseudomonas_zscores.txt"))

    zscore_lines = zscore_file.readlines()

    header = zscore_lines[0]

    zscore_lines = zscore_lines[1:]
    
    zscore_lines = [line.split("\t") for line in zscore_lines]

    zscore_high_path = [line for line in zscore_lines if float(line[1]) >= float(line[2])]

    zscore_no_pgp = [line for line in zscore_lines if (float(line[1]) >= float(line[2])) and (float(line[2]) == 0.0)]

    with open(Path(next_dir + "high_patho_zscores_Pseudomonas_nr_default.txt"), "w") as high_path_file:
        high_path_file.write(header)
        for line in zscore_high_path:
            high_path_file.write("\t".join(line))
        high_path_file.close()

    with open(Path(next_dir + "only_patho_zscores_Pseudomonas_nr_default.txt"), "w") as no_pgp_file:
        no_pgp_file.write(header)
        for line in zscore_no_pgp:
            no_pgp_file.write("\t".join(line))
        no_pgp_file.close()

    with open(Path(next_dir + "high_patho_vfdb_keggids.txt"), "w") as no_pgp_file:
        no_pgp_file.write(header)
        for line in zscore_high_path:
            no_pgp_file.write(line[0].split(" ")[0] + "\n")
        no_pgp_file.close()

    with open(Path(next_dir + "only_patho_vfdb_keggids.txt"), "w") as no_pgp_file:
        no_pgp_file.write(header)
        for line in zscore_no_pgp:
            no_pgp_file.write(line[0].split(" ")[0] + "\n")
        no_pgp_file.close()


    print("Done!")


def main():
    zscore_filter()



if __name__ == '__main__':
    main()

