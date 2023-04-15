import os

def kegg_izer():
    dir_content = os.listdir()
    print(dir_content)

    vfdb_file_missing = not ("VFDB_readname_to_keggname.txt" in dir_content)

    comparison_missing = not ("kosakonia_keggid_to_count.txt" in dir_content)

    if vfdb_file_missing or comparison_missing:
        print("missing essential file(s), try again")
        exit()
    
    vfdb_keggid_set = set()

    vfdb_file = open("VFDB_readname_to_keggname.txt", "r")

    lines = vfdb_file.readlines()

    for line in lines:
        kegg_id = line.split("\t")[1].strip()

        vfdb_keggid_set.add(kegg_id)
    
    comparison_file = open("kosakonia_keggid_to_count.txt", "r")

    comparison_lines = comparison_file.readlines()

    comparison_trimmed = list(comparison_lines[0])

    comparison_absence_presence = list(comparison_lines[0])

    for i in range(1, len(comparison_lines)):
        line = comparison_lines[i].split("\t")

        kegg_id = line[0]

        if kegg_id in vfdb_keggid_set:
            comparison_trimmed.append("\t".join(line))

    with open(f"kosakonia_comparison_vfdb_filtered.txt", "w") as shell:
        for line in comparison_trimmed:
            shell.write(line)
        shell.close()
    
    return("Done!")



def main():
    kegg_izer()



if __name__ == '__main__':
    main()
