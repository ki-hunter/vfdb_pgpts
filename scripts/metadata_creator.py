import re
from job_creator import choose_strain_name, match_img_ncbi
import pandas as pd

# IMG_SAMPLE_ID	SEQUENCING_STATUS	STUDY_NAME	GENOME_NAME	IGZ_CULTURECOLLECTION
# SEQUENCING_CENTER	PHYLUM	CLASS	ORDER
# FAMILY	GENUS	SPECIES	GENOME_NAME	GENOME_SIZE	GENE_COUNT	JGI_PROTEIN_COUNT
# GENE_DENSITY	JGI_KEGG_PROTEIN_COUNT	IS_PUBLIC
# NCBI_PROJECT_ID	REFSEQ_PROJECT_ID	BIOTIC_RELATIONSHIP	ECOSYSTEM
# ECOSYSTEM_CATEGORY	HOST:PLANT	HOST:HUMAN	HOST:ANIMAL
# HOST:SOIL	HOST:COMPOST	HOST:ROCK	HOST:FUNGI	HOST:AQUATIC
# HOST: ALGAE-PLANKTON	HOST:FOOD	HOST:AIR
# HOST:BIOTECH/INDUST	HOST:ND		ORGAN:PHYLLOSPHERE	ORGAN:RHIZOSPHERE
# ORGAN:FRUIT	ORGAN:FLOWER	ORGAN:SEED	ORGAN:BARK
# ORGAN:ND	PHEN:PGPT	PHEN:PATHO	PHEN:ND	PGPT	ECOSYSTEM_SUBTYPE
# ECOSYSTEM_TYPE	not_announced	HABITAT	ISOLATION
# HOST_NAME	PHENOTYPE	PUBMED_ID	RELEVANCE	SAMPLE_BODY_SITE
# TYPE_STRAIN	GENOME_SIZE	GENE_COUNT	CULTURED	DISEASE
# ENERGY_SOURCE	GEOGRAPHIC_LOCATION	GRAM_STAINING	ISOLATION_COUNTRY
# METABOLISM	MOTILITY	OXYGEN_REQUIREMENT	PH
# PRESSURE	SALINITY	SPORULATION	TEMPERATURE_RANGE	ANI_CLUSTER_ID
# ANI_CLUSTER_TYPE	JGI_PROJECT_ID	GOLD_ANALYSIS_ID
# GOLD_SEQPROJECT_ID	GOLD_STUDY_ID	NCBI_TAX_ID	REFSEQ_PROJECT_ID
# NCBI_PROJECT_ID	NCBI_BIOPROJECT_ID-GBK	NCBI_BIOSAMPLE_ID
# GENOME_NAME	PMO_PROJECT_ID	REFSEQ_BIOPROJECT_ID	REFSEQ_SAMPLE_ID
# REFSEQ_GBK_ACCESSION	REFSEQ_GBK_ID
# REFSEQ_ASSEMBLY_ACCESSION	REFSEQ_ASSEMBLY_LEVEL	REFSEQ_WGS_MASTER
# REFSEQ_TAXID	REFSEQ_SPECIES_ID	REFSEQ_ORGANISM
# REFSEQ_LINK	GBK_BIOPROJECT_ID	GBK_SAMPLE_ID	GBK_GBK_ACCESSION
# GBK_GBK_ID	GBK_ASSEMBLY_ACCESSION	GBK_ASSEMBLY_LEVEL
# GBK_WGS_MASTER	GBK_TAXID	GBK_SPECIES_ID	GBK_ORGANISM	GBK_LINK
# ORGINF_GCF_ID	ORGINF_GCA	ORGINF_KEGG_ORG_ID
# ORGINF_KEGG_ORG_SYM	ORGINF_SEQUENCE_LEVEL	ORGINF_GENOME_CONTENT
# ORGINF_LIFESTYLE	ORGINF_ISOLATION	ORGINF_PUBMED_ID
# ORGINF_ALL

# class AltStrainInfo:
    def __init__(self, img_header: str, img_strain_data: str) -> None:
        self.img_data = img_strain_data

        img_strain_content = img_strain_data.split("\t")

        self.img_header = img_header.split("\t")

        self.assembly_status = img_strain_content[self.img_header.index("SEQUENCING_STATUS")].strip()

        self.organism_name = img_strain_content[self.img_header.index("GENOME_NAME")].strip()

        self.genus_name = img_strain_content[self.img_header.index("GENUS")].strip()

        self.species_name = img_strain_content[self.img_header.index("SPECIES")].strip()

        self.strain_name = img_strain_content[self.img_header.index("GENOME_NAME")].strip()

        self.ncbi_taxid = img_strain_content[self.img_header.index("NCBI_TAX_ID")].strip()

        self.ncbi_assembly = img_strain_content[self.img_header.index("REFSEQ_GBK_ID")].strip()

        self.ncbi_bioproject = img_strain_content[self.img_header.index("REFSEQ_BIOPROJECT_ID")].strip()

        self.ncbi_biosample = img_strain_content[self.img_header.index("REFSEQ_SAMPLE_ID")].strip()

        self.img_relevance = img_strain_content[self.img_header.index("RELEVANCE")].strip()

        self.img_diseases = img_strain_content[self.img_header.index("DISEASE")].strip()

        self.img_phenotype = img_strain_content[self.img_header.index("PHENOTYPE")].strip()

        self.ncbi_data = ""

        self.ncbi_match = False

        self.ftp_link = ""

        self.filename = ""

        self.human_pathogen = False

        self.animal_pathogen = False

        self.plant_pathogen = False

        self.pathogen = False

        self.is_disease = False

        self.is_pgpb = False

        if re.search("[Hh]uman [Pp]athogen", self.img_data):
            self.human_pathogen = True

        if re.search("[Aa]nimal [Pp]athogen", self.img_data):
            self.human_pathogen = True

        if re.search("[Pp]lant [Pp]athogen", self.img_data):
            self.human_pathogen = True

        if re.search("[Pp]athogen", self.img_data):
            self.pathogen = True

        if len(self.img_diseases) > 3 or self.pathogen:
            self.is_disease = True

# def filter_sascha_for_genus(genus_name: str, IMG_file: str) -> list:
#     """\
#     Filters the available IMG metadata for a given genus and for sequencing
#     status ("Permanent draft" and "Finished")

#     Parameters
#     ----------
#     genus_name : str
#         Name of the genus of interest

#     Returns
#     -------
#     genus_img_data : list[str]
#         list containing img data for the strains of the given genus

#     """
#     genus_name = genus_name.capitalize()

#     img_metadata = open(IMG_file, "r") # accessed 23/08/2023
#     lines = img_metadata.readlines()

#     genus_img_data = [lines[0]]

#     img_header = lines[0].split("\t")

#     assembly_index = img_header.index("Sequencing Status")

#     genus_index = img_header.index("Genus")

#     for strain in lines:
#         strain_content = strain.split("\t")

#         assembly_status = strain_content[assembly_index].strip()

#         finished_assembly = "Finished" in assembly_status or "Permanent Draft" in assembly_status

#         line_genus = strain_content[genus_index].strip()

#         correct_genus = genus_name == line_genus

#         if correct_genus and finished_assembly:

#             genus_img_data.append(strain)


#     return genus_img_data

# def match_img_ncbi(genus_name:str, IMG_file:str) -> list:
#     """\
#     After filtering the NCBI assembly file and the availble IMG metadata for the genus the method tries to match 
#     each IMG entry to an NCBI entry. A match is successful if the IMG entry's species name _and_ NCBI assembly
#     or accession id match to those of an NCBI entry. The resulting matched strains are returned as 
#     a list of StrainInfo objects.

#     Parameters
#     ----------
#     genus_name : str
#         Name of the genus of interest

#     Returns
#     -------
#     genus_strains : list[StrainInfo]
#         list containing a StrainInfo Object for each IMG strain matched to an NCBI entry

#     """
#     genus_strains = []

#     ncbi_genus_data = filter_ncbi_for_genus(genus_name)

#     assembly_header = ncbi_genus_data[0].split("\t")

#     accession_index = assembly_header.index("#assembly_accession")
#     assembly_index = assembly_header.index("gbrs_paired_asm")
#     ncbi_name_index = assembly_header.index("organism_name")

#     img_genus_data = filter_sascha_for_genus(genus_name, IMG_file)

#     print(f"Found {len(img_genus_data)} strains of {genus_name} in IMG, attempting match")
#     match_count = 0

#     for strain in img_genus_data[1:]:

#         strain = AltStrainInfo(img_genus_data[0], strain)

#         ncbi_assembly = strain.ncbi_assembly.replace(" ", "_")

#         if "." in ncbi_assembly:
#             ncbi_assembly = ncbi_assembly[:-2]

#         species = strain.species_name

#         for candidate in ncbi_genus_data[:-1]:

#             content = candidate.split("\t")

#             if "GCA" in ncbi_assembly:
#                 correct_assembly = ncbi_assembly in content[assembly_index]
#             elif "GCF" in ncbi_assembly:
#                 correct_assembly = ncbi_assembly in content[accession_index]

#             correct_species = species in content[ncbi_name_index]

#             if correct_assembly and correct_species:

#                 strain.ncbi_match = True

#                 strain.ncbi_data = candidate

#                 match_count += 1

#                 genus_strains.append(strain)

#     print(f"Matched {match_count} IMG strains to NCBI data")
#     return genus_strains

def create_metadata(genus_name: str):
    assembly = open("assembly_summary.txt", "r", encoding="utf-8")
    lines = assembly.readlines()

    assembly_header = lines[1].split("\t")

    strains_of_interest = match_img_ncbi(genus_name, "Metadata_Kosakonia_Pseudomonas_PGPT-PATHO.txt")

    sample_ids = []

    species = []

    human_pathogen = []

    animal_pathogen = []

    plant_pathogen = []

    pathogen = []

    disease = []

    for strain in strains_of_interest:

        if strain.ncbi_match:

            strain.filename = choose_strain_name(assembly_header, strain.ncbi_data.split("\t"))

            sample_ids.append(strain.filename + "_protein")

            species.append(strain.species_name)

            if strain.human_pathogen:
                human_pathogen.append(1)
            else:
                human_pathogen.append(0)

            if strain.animal_pathogen:
                animal_pathogen.append(1)
            else:
                animal_pathogen.append(0)

            if strain.plant_pathogen:
                plant_pathogen.append(1)
            else:
                plant_pathogen.append(0)

            if strain.pathogen:
                pathogen.append(1)
            else:
                pathogen.append(0)

            if strain.is_disease:
                disease.append(1)
            else:
                disease.append(0)

    metadata_dict = {
        "#SampleID": sample_ids,
        "SPECIES": species,
        "HUMAN_PATHOGEN": human_pathogen,
        "ANIMAL_PATHOGEN": animal_pathogen,
        "PLANT_PATHOGEN": plant_pathogen,
        "PATHOGEN": pathogen
        }

    metadata_df = pd.DataFrame(metadata_dict)

    metadata_df.to_csv(f"{genus_name}_metadata_{len(species)}_strains.csv", sep="\t", index=False)

    return metadata_df


def create_trait_tables(genus_name: str):

    metadata_df = create_metadata(genus_name)

    for column in metadata_df.columns[2:]:
        trait_df = metadata_df.loc[:, ["#SampleID", column]]
        trait_df = trait_df.rename(columns={"#SampleID" : ""})

        trait_df.to_csv(f"{genus_name}_{column}_trait_table.csv", sep=",", index=False)

    pass


def main():
    # ncbi_datasets_installer()
    # species_name_finder()
    # genus_search_result = bacdive_client("kosakonia")
    # print(genus_search_result)
    # print(filter_for_genus("Kosakonia"))

    # create_initial_metadata("Kosakonia")

    # print(parse_bacdive_keywords(genus_search_result))

    # for strain in match_img_ncbi("kosakonia"):
    #     relevance_index = strain.img_header.index("Phenotype")

    #     print(strain.img_data.split("\t")[relevance_index])

    # count pathogenic strains:
    pathogen_count = 0
    filter_result = filter_sascha_for_genus("kosakonia")
    for strain in filter_result:
        if re.search("[Pp]athogen", strain):
            pathogen_count += 1
    print(pathogen_count)
    print(len(filter_result))

    create_trait_tables("pseudomonas")

    pass


if __name__ == '__main__':
    main()
