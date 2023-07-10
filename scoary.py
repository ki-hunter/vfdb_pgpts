import pandas as pd
import os

def create_absence_presence():

    dir_content = os.listdir()

    count_files = []

    for file in dir_content:
        if "keggname_to_count" in file:
            count_files.append(file)

    for file in count_files:
        keggname_to_count = pd.read_csv(file, sep="\t")

        keggname_to_count = keggname_to_count.set_index("#Datasets")

        keggname_to_count = keggname_to_count.rename_axis("Gene", axis=0)

        for i in keggname_to_count.columns:

            keggname_to_count[i] = keggname_to_count[i].apply(lambda x : 1 if int(x) >= 1 else 0)

        additional_columns = ["Non-unique Gene name","Annotation","No. isolates","No. sequences","Avg sequences per isolate","Genome fragment","Order within fragment","Accessory Fragment","Accessory Order with Fragment","QC","Min group size nuc","Max group size nuc","Avg group size nuc"]
        
        col_index = 0

        for column_name in additional_columns:

            keggname_to_count.insert(col_index, column_name, None)
            col_index += 1

        keggname_to_count.to_csv(str(file).replace("keggname_to_count", "absence_presence"), sep=",")

    





def main():
    create_absence_presence()
    

    pass


if __name__ == '__main__':
    main()
