import pandas as pd
import os
import math


def create_absence_presence():

    dir_content = os.listdir()

    count_files = []

    for file in dir_content:
        print(file)
        if "all_vfdb_keggname_to_count" in file:
            count_files.append(file)

    for file in count_files:
        print(file)
        keggname_to_count = pd.read_csv(file, sep="\t")

        keggname_to_count.set_index("#Datasets", inplace=True)

        keggname_to_count.rename_axis("Gene", axis=0, inplace=True)

        for i in keggname_to_count.columns:

            old_name = str(i)
            new_name = old_name.replace("_result", "").strip()

            keggname_to_count.rename(columns={old_name : new_name}, inplace=True)

            keggname_to_count[new_name] = keggname_to_count[new_name].apply(lambda x : 1 if int(x) >= 1 else 0)

        additional_columns = ["Non-unique Gene name","Annotation","No. isolates","No. sequences","Avg sequences per isolate","Genome fragment","Order within fragment","Accessory Fragment","Accessory Order with Fragment","QC","Min group size nuc","Max group size nuc","Avg group size nuc"]

        col_index = 0

        for column_name in additional_columns:

            keggname_to_count.insert(col_index, column_name, None)
            col_index += 1

        keggname_to_count.to_csv(str(file).replace("keggname_to_count.txt", "absence_presence.csv"), sep=",")

    return True


def create_trait_tables(trait_name: str):

    metadata = pd.read_csv("Kosakonia_metadata_58_species.txt", sep="\t")

    trait_variants = []

    for i in range(len(metadata)):
        variant_name = metadata.loc[i, trait_name]

        if variant_name not in trait_variants:

            variant_isnan = isinstance(variant_name, float) and math.isnan(variant_name)

            if not variant_isnan:

                trait_variants.append(variant_name)

    stripped_strains = [str(strain).replace("_result", "").strip() for strain in metadata.iloc[:, 0]]

    trait_table = pd.DataFrame(stripped_strains)

    for variant in trait_variants:

        trait_table.insert(1, variant, [0]*len(metadata))

    for i in range(len(metadata)):

        variant = metadata.loc[i, trait_name]

        variant_isnan = isinstance(variant, float) and math.isnan(variant)

        if variant_isnan:

            for column in trait_table.columns[1:]:
                trait_table.loc[i, column] = "NA"

        else:
            trait_table.loc[i, variant] = 1

    trait_table.rename(columns={0: ""}, inplace=True)
    print(trait_table)

    trait_table.to_csv(f"{trait_name}_trait_table.csv", sep=",", index=False)

    return True


def main():
    create_absence_presence()

    # create_trait_tables("PLANT_PHENOTYPE")

    pass


if __name__ == '__main__':
    main()
