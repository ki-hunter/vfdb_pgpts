import os
import pathlib

def zscore_filter():
    dir_content = os.listdir()
    # print(pathlib.Path.resolve(__file__))

    zscore_file_missing = not("kosakonia_nr_default_zscore_chart.txt" in dir_content)

    if zscore_file_missing:
        print("missing zscore file")
        exit()

    zscore_file = open("kosakonia_nr_default_zscore_chart.txt")

    zscore_lines = zscore_file.readlines()

    header = zscore_lines[0]

    zscore_lines = zscore_lines[1:]
    
    zscore_lines = [line.split("\t") for line in zscore_lines]

    zscore_high_path = [line for line in zscore_lines if float(line[2]) >= float(line[1])]

    zscore_no_pgp = [line for line in zscore_lines if (float(line[2]) >= float(line[1])) and (float(line[1]) == 0.0)]

    with open("kosakonia_nr_default_zscore_high_path.txt", "w") as high_path_file:
        high_path_file.write(header)
        for line in zscore_high_path:
            high_path_file.write("\t".join(line))
        high_path_file.close()

    with open("kosakonia_nr_default_zscore_no_pgp.txt", "w") as no_pgp_file:
        no_pgp_file.write(header)
        for line in zscore_no_pgp:
            no_pgp_file.write("\t".join(line))
        no_pgp_file.close()

    with open("kosakonia_nr_default_zscore_high_path_keggids.txt", "w") as no_pgp_file:
        no_pgp_file.write(header)
        for line in zscore_high_path:
            no_pgp_file.write(line[0].split(" ")[0] + "\n")
        no_pgp_file.close()

    with open("kosakonia_nr_default_zscore_no_pgp_keggids.txt", "w") as no_pgp_file:
        no_pgp_file.write(header)
        for line in zscore_no_pgp:
            no_pgp_file.write(line[0].split(" ")[0] + "\n")
        no_pgp_file.close()


    print("Done!")


def main():
    zscore_filter()



if __name__ == '__main__':
    main()

