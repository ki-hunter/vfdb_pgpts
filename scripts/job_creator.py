import urllib.request
import os
from pathlib import Path
import re
import sys


class StrainInfo:
    def __init__(self, data_header: str, strain_metadata: str) -> None:
        self.img_data = strain_metadata

        strain_metadata = strain_metadata.split("\t")

        self.data_header = data_header.split("\t")

        status_index = self.data_header.index("Sequencing Status")

        self.status = strain_metadata[status_index].strip()

        org_name_index = self.data_header.index("Genome Name / Sample Name")

        self.organism_name = strain_metadata[org_name_index].strip()

        genus_index = self.data_header.index("Genus")

        self.genus_name = strain_metadata[genus_index].strip()

        species_index = self.data_header.index("Species")

        self.species_name = strain_metadata[species_index].strip()

        strain_index = self.data_header.index("Strain")

        self.strain_name = strain_metadata[strain_index].strip()

        ncbi_taxid_index = self.data_header.index("NCBI Taxon ID")

        self.ncbi_taxid = strain_metadata[ncbi_taxid_index].strip()

        ncbi_assembly_index = self.data_header.index("NCBI Assembly Accession")

        self.ncbi_assembly = strain_metadata[ncbi_assembly_index].strip()

        ncbi_biopr_index = self.data_header.index("NCBI Bioproject Accession")

        self.ncbi_bioproject = strain_metadata[ncbi_biopr_index].strip()

        ncbi_biosmpl_index = self.data_header.index("NCBI Biosample Accession")

        self.ncbi_biosample = strain_metadata[ncbi_biosmpl_index].strip()

        img_relevance_index = self.data_header.index("Relevance")

        self.img_relevance = strain_metadata[img_relevance_index].strip()

        img_diseases_index = self.data_header.index("Diseases")

        self.img_diseases = strain_metadata[img_diseases_index].strip()

        img_phenotype_index = self.data_header.index("Phenotype")

        self.img_phenotype = strain_metadata[img_phenotype_index].strip()

        self.ncbi_data = ""

        self.ncbi_match = False

        self.ftp_link = ""

        self.filename = ""

        self.human_pathogen = False

        self.animal_pathogen = False

        self.plant_pathogen = False

        self.pathogen = False

        self.is_disease = False

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


def filter_ncbi_for_genus(genus_name: str) -> list:

    fetch_assembly()

    assembly_file = open("assembly_summary.txt", "r", encoding="utf-8")
    lines = assembly_file.readlines()

    genus_assembly = []

    genus_assembly.append(lines[1])

    for line in lines:

        full_check = "Full" in line
        complete_check = "Complete Genome" in line

        if genus_name.capitalize() in line and (full_check or complete_check):

            genus_assembly.append(line)

    return genus_assembly


def filter_img_for_genus(genus_name: str, IMG_file: str) -> list:
    """\
    Filters the available IMG metadata for a given genus and for sequencing
    status ("Permanent draft" and "Finished")

    Parameters
    ----------
    genus_name : str
        Name of the genus of interest

    Returns
    -------
    genus_img_data : list[str]
        list containing img data for the strains of the given genus

    """
    genus_name = genus_name.capitalize()

    img_metadata = open(IMG_file, "r")
    lines = img_metadata.readlines()

    genus_img_data = [lines[0]]

    img_header = lines[0].split("\t")

    assembly_index = img_header.index("Sequencing Status")

    genus_index = img_header.index("Genus")

    for strain in lines:
        strain_content = strain.split("\t")

        assembly_status = strain_content[assembly_index].strip()

        assmbly_finished = "Finished" in assembly_status

        assmbly_permanent = "Permanent Draft" in assembly_status

        finished_assembly = assmbly_finished or assmbly_permanent

        line_genus = strain_content[genus_index].strip()

        correct_genus = genus_name == line_genus

        if correct_genus and finished_assembly:

            genus_img_data.append(strain)

    return genus_img_data


def match_img_ncbi(genus_name: str, IMG_file: str) -> list:
    """\
    After filtering the NCBI assembly file and the available IMG metadata for
    the genus the method tries to match each IMG entry to an NCBI entry.
    A match is successful if the IMG entry's species name _and_ NCBI assembly
    or accession id match to those of an NCBI entry. The resulting matched
    strains are returned as a list of StrainInfo objects.

    Parameters
    ----------
    genus_name : str
        Name of the genus of interest

    Returns
    -------
    genus_strains : list[StrainInfo]
        list containing a StrainInfo Object for each IMG strain matched to
        an NCBI entry

    """
    genus_strains = []

    ncbi_genus_data = filter_ncbi_for_genus(genus_name)

    assembly_header = ncbi_genus_data[0].split("\t")

    accession_index = assembly_header.index("#assembly_accession")
    assembly_index = assembly_header.index("gbrs_paired_asm")
    ncbi_name_index = assembly_header.index("organism_name")

    img_genus_data = filter_img_for_genus(genus_name, IMG_file)

    print(f"Found {len(img_genus_data)} strains of {genus_name} in IMG")
    print("attempting match...")
    match_count = 0

    for strain in img_genus_data[1:]:

        strain = StrainInfo(img_genus_data[0], strain)

        ncbi_assembly = strain.ncbi_assembly.replace(" ", "_")

        # delete e.g. .1 to ignore versioning,
        # IMG version may be outdated but data should still be correct
        if "." in ncbi_assembly:
            ncbi_assembly = ncbi_assembly[:-2]

        species = strain.species_name

        for candidate in ncbi_genus_data[:-1]:

            content = candidate.split("\t")

            if "GCA" in ncbi_assembly:
                correct_assembly = ncbi_assembly in content[assembly_index]
            elif "GCF" in ncbi_assembly:
                correct_assembly = ncbi_assembly in content[accession_index]

            correct_species = species in content[ncbi_name_index]

            if correct_assembly and correct_species:

                strain.ncbi_match = True

                strain.ncbi_data = candidate

                match_count += 1

                genus_strains.append(strain)

    print(f"Matched {match_count} IMG strains to NCBI data")
    return genus_strains


def fetch_assembly(file_dir: str):
    """\
    Downloads the NCBI Assembly file (as assembly_summary.txt)
    if it is not already present
    """
    dir_content = os.listdir(file_dir)

    assembly_not_downloaded = not ("assembly_summary.txt" in dir_content)

    if assembly_not_downloaded:

        print("Downloading the NCBI assembly summary")
        assembly_url = "https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/assembly_summary.txt"  # noqa
        response = urllib.request.urlopen(assembly_url)
        web_content = response.read().decode("UTF-8")

        with open(f"{file_dir}/assembly_summary.txt", "w", encoding="utf-8") as file:  # noqa
            file.write(web_content)
            file.close()

    else:
        return "NCBI assembly summary present"


def format_to_usability(string: str) -> str:
    """\
    Removes several characters (" ", ".", "/", ",") from a given string,
    if present, to enable use as link

    Parameters
    ----------
    string : str
        String to be formatted

    Returns
    -------
    formatted_string : str
        Formatted String


    """
    formatted_string = string.replace(" ", "_")
    formatted_string = formatted_string.replace(".", "_")
    formatted_string = formatted_string.replace("/", "_")
    formatted_string = formatted_string.replace(",", "_")
    formatted_string = formatted_string.replace("(", "_")
    formatted_string = formatted_string.replace(")", "_")
    formatted_string = formatted_string.replace(":", "_")
    formatted_string = formatted_string.replace("-", "_")

    return formatted_string


def choose_strain_name(assembly_header: list, strain_data: list) -> str:
    """\
    Given a strain's NCBI data (it's line in the assembly file) and the header
    of the NCBI assembly file this method returns a hopefully unique name for
    that strain based on the organism and infraspecific name in the assembly
    file - if no infraspecific name is present, the isolate is used.

    Parameters
    ----------
    assembly_header : list
        header of the NCBI assembly file necessary to navigate its content
    strain_data : list
        a line of the NCBI assembly file containing the available data of a
        single strain

    Returns
    -------
    strain_name : str
        hopefully unique name for the strain
    """
    organism_name_index = assembly_header.index("organism_name")
    infra_index = assembly_header.index("infraspecific_name")
    isolate_index = assembly_header.index("isolate")
    asm_name_index = assembly_header.index("asm_name")

    organism_name = strain_data[organism_name_index]

    infra_name = strain_data[infra_index]

    isolate = strain_data[isolate_index]

    assembly = strain_data[asm_name_index]

    if infra_name == "" or infra_name == "na":
        infra_name = f"isolate={isolate}"

    strain_name = format_to_usability(f"{organism_name}_{infra_name}_{assembly}")  # noqa

    return strain_name


def fetch_genus(genus_name: str) -> str:
    """\
    Parses the assembly file for a user-entered genus name, then creates and
    bashes a shell to download that genus' member species protein.faa.gz files
    from NCBI, provided the species' NCBI id is found in IMG.
    The downloads are placed within a new directory {genus}/{genus}_protein

    Returns
    -------
    genus_name : str
        name of the genus for which protein files where downloaded
    """

    species_count = 0

    strains_of_interest = match_img_ncbi(genus_name, "IMG_metadata.txt")

    assembly_file = open("assembly_summary.txt", "r", encoding="utf-8")
    lines = assembly_file.readlines()

    assembly_header = lines[1].split("\t")

    ftp_index = assembly_header.index("ftp_path")
    accession_index = assembly_header.index("#assembly_accession")
    asm_name_index = assembly_header.index("asm_name")
    # organism_name_index = assembly_header.index("organism_name")

    species_in_gattung = []

    working_dir = Path(os.getcwd())

    with open("genus_DL.sh", "w") as shell:

        genus_dir = Path(f"{working_dir}/{genus_name}")

        shell.write(f"mkdir {genus_dir}\n")
        shell.write(f"cd {genus_dir}\n")

        # shell.write(f"touch  {genus_dir}/{genus_name}_ncbi_data.txt\n")

        genus_protein_dir = Path(f"{genus_dir}/{genus_name}_protein")

        shell.write(f"mkdir {genus_protein_dir}\n")
        shell.write(f"cd {genus_protein_dir}\n")

        shell.write(f"touch {genus_protein_dir}/{genus_name}_records.txt\n")

        for strain in strains_of_interest:

            strain_has_ncbi_data = strain.ncbi_match

            strain_ncbi_data = strain.ncbi_data

            if strain_has_ncbi_data:

                strain_ncbi_data = strain_ncbi_data.replace("\n", "")

                # shell.write(f"echo '{strain_ncbi_data}' >> {genus_dir}/{genus_name}_ncbi_data.txt\n")

                contents = strain_ncbi_data.split("\t")

                species_count += 1

                species_in_gattung.append(strain_ncbi_data)

                strain_url = contents[ftp_index]

                asm_name = contents[asm_name_index].replace("/", "_")

                accession = contents[accession_index]

                if " " in asm_name:
                    asm_name = asm_name.replace(" ", "_")

                if " " in accession:
                    accession = accession.replace(" ", "_")

                protein_url = Path(f"{strain_url}/{accession}_{asm_name}_protein.faa.gz")

                strain_name = choose_strain_name(assembly_header, contents)

                strain.filename = strain_name + "_protein"

                strain.ftp_link = protein_url

                shell.write(f"wget -nc -O {strain_name}_protein.faa.gz {protein_url}\n")
                shell.write(f'echo "{accession}_{asm_name} downloaded as {strain_name}_protein.faa.gz" >> {genus_name}_records.txt\n')
                shell.write(f"gzip -d {strain_name}_protein.faa.gz\n")
                shell.write(f'echo "{strain_name}_protein.faa.gz unzipped" >> {genus_name}_records.txt\n\n')

        shell.close()

        if species_count == 0:
            print(f"No records for {genus_name} found in the NCBI assembly file, try something else")
            os.system("rm genus_DL.sh")
            sys.exit()
        else:
            os.system(f"echo {species_count} species of genus {genus_name} found, downloading...")

    os.system("bash genus_DL.sh")
    # os.system("rm genus_DL.sh")

    species_downloaded = len(os.listdir(f"{genus_name}/{genus_name}_protein/")) - 1
    print(f"{species_downloaded} species downloaded")

    return genus_name


def genus_job_creator(genus_name):
    """\
    Creates jobs for every species in the genus in batches of user-entered
    size, containing:
    - diamond run against nr database
    - meganization with mdb for resulting daa file
    - diamond run against vfdb database
    - sadly no automatic meganization with vfdb
    for each species

    Parameters
    ----------
    genus_name : str
        Name of the genus for which jobs are created, used to navigate to the
        correct directory

    """
    comment = "(influences max runtime (4h per species) amount of jobs)"

    batch_size = int(input(f"Enter size of batches {comment}:"))

    if not isinstance(batch_size, int):
        print("Please enter an integer")
        sys.exit()

    if batch_size > 12:
        long_warning = "This size will result in jobs being submitted to the long queue"  # noqa
        print(long_warning)

    print("Creating jobs...")

    running_dir = Path(os.getcwd())

    working_dir = Path(f"{running_dir}/{genus_name}")
    os.chdir(working_dir)

    target_dir = f"{genus_name}_protein"

    target_dir_path = Path(f"{working_dir}/{target_dir}")

    species_names = os.listdir(target_dir_path)

    species_count = len(species_names)

    batch_counter = 0

    nr_result_dir = Path(f"{working_dir}/{genus_name}_nr_default_meganization")
    # nr_vfdb_dir = Path(f"{working_dir}/{genus_name}_nr_vfdb_meganization")
    vfdb_result_dir = Path(f"{working_dir}/{genus_name}_vfdb_default_meganization")
    # vfdb_vfdb_dir = Path(f"{working_dir}/{genus_name}_vfdb_vfdb_meganization")
    batches_dir = Path(f"{working_dir}/batches")

    os.system(f"mkdir {nr_result_dir}")
    # os.system(f"mkdir {nr_vfdb_dir}")
    os.system(f"mkdir {vfdb_result_dir}")
    # os.system(f"mkdir {vfdb_vfdb_dir}")
    os.system(f"mkdir {batches_dir}")

    max_runtime = abs(batch_size) * 4

    assigned_cores = 4

    assigned_memory = assigned_cores * 4

    for i in range(0, species_count):

        if i % batch_size == 0:
            batch_counter += 1

            job_name = f"{genus_name}_batch_{batch_counter}.sh"
            job_dir = Path(f"{batches_dir}/{job_name}")

            jobtext = [f"#PBS -l nodes=1:ppn={assigned_cores}",
                       f"\n#PBS -l walltime={max_runtime}:00:00",
                       f"\n#PBS -l mem={assigned_memory}gb",
                       "\n#PBS -S /bin/bash",
                       f"\n#PBS -N {job_name}",
                       "\n#PBS -j oe",
                       f"\n#PBS -o {job_name.replace('.sh', '')}_LOG",
                       "\ncd $PBS_O_WORKDIR",
                       '\necho "running on node:"',
                       "\nuname -a"]

            with open(job_dir, "w") as shell:
                shell.writelines(jobtext)
                shell.close()

        nr_dia_part1 = f"\n/home/tu/tu_tu/tu_zxozy01/tools/diamond_15/diamond blastp -d {running_dir}/nr -q"
        nr_dia_part2 = "_result.daa -f 100 -b 5 -c 1 --threads 8"

        mdb_meg_part1 = "\n/home/tu/tu_tu/tu_zxozy01/tools/megan/tools/daa-meganizer -i"
        mdb_meg_part2 = "-mdb /home/tu/tu_tu/tu_zxozy01/tools/megan-map-Feb2022-ue.db"

        vfdb_dia_part1 = f"\n/home/tu/tu_tu/tu_zxozy01/tools/diamond_15/diamond blastp -d {running_dir}/vfdb -q"
        vfdb_dia_part2 = f"_result.daa -f 100 -b 5 -c 1 --threads 8"

        # vfdb_meg_part1 = "\n/home/tu/tu_tu/tu_zxozy01/tools/megan/tools/daa-meganizer -i "
        # vfdb_meg_part2 = " -P /home/tu/tu_tu/tu_zxozy01/tools/megan/class/resources/files/vfdb.map"

        target_filepath = Path(f"{target_dir_path}/{species_names[i]}")

        output_name = species_names[i][0:-4]

        f = open(job_dir, "a")
        # runs diamond against nr and vfdb
        # after, the file is meganized
        f.write(f"{nr_dia_part1} {target_filepath} -o {nr_result_dir}/{output_name}{nr_dia_part2}")

        # f.write(f"\ncp {nr_result_dir}/{output_name}_result.daa {nr_vfdb_dir}")

        f.write(f"{mdb_meg_part1} {nr_result_dir}/{output_name}_result.daa {mdb_meg_part2}")

        f.write(f"{vfdb_dia_part1} {target_filepath} -o {vfdb_result_dir}/{output_name}{vfdb_dia_part2}")

        # f.write(f"\ncp {vfdb_result_dir}/{output_name}_result.daa {vfdb_vfdb_dir}")

        # f.write(f"{vfdb_meg_part1} {vfdb_result_dir}/{output_name}_result.daa {vfdb_meg_part2}")

        f.close()
    print(f"done, {batch_counter} jobs created")


def comparison_creator(genus_name):
    """\
    Creates a job to run comparisons for the meganized sets

    Parameters
    ----------
    genus_name : str
        Name of the genus for which jobs are created,
        used to navigate to the correct directory

    """
    # creates jobs for comparisons of the default meganized sets

    working_dir = os.getcwd()

    nr_result_dir = f"{working_dir}/{genus_name}_nr_default_meganization"
    # nr_vfdb_dir = f"{working_dir}/{genus_name}_nr_vfdb_meganization"
    vfdb_result_dir = f"{working_dir}/{genus_name}_vfdb_default_meganization"
    # vfdb_vfdb_dir = f"{working_dir}/{genus_name}_vfdb_vfdb_meganization"

    jobtext = ["#PBS -l nodes=1:ppn=8",
               "\n#PBS -l walltime=02:00:00",
               "\n#PBS -l mem=32gb",
               "\n#PBS -S /bin/bash",
               "\n#PBS -N " + f"{genus_name}_comparison",
               "\n#PBS -j oe", f"\n#PBS -o {genus_name}_comparison_LOG",
               "\ncd PBS_O_WORKDIR",
               '\necho "running on node:"',
               "\nuname -a"]

    with open(f"{genus_name}_comparison.sh", "w") as shell:
        shell.writelines(jobtext)
        shell.close()

    comparison_cmd_part1 = "\n/home/tu/tu_tu/tu_zxozy01/tools/megan/tools/compute-comparison -i "

    shell = open(f"{genus_name}_comparison.sh", "a")

    shell.write(f"{comparison_cmd_part1}{nr_result_dir} -o {working_dir}/nr_default_comparison.megan")
    # shell.write(f"{comparison_cmd_part1}{nr_vfdb_dir} -o {working_dir}/nr_vfdb_comparison.megan")
    shell.write(f"{comparison_cmd_part1}{vfdb_result_dir} -o {working_dir}/vfdb_default_comparison.megan")
    # shell.write(f"{comparison_cmd_part1}{vfdb_vfdb_dir} -o {working_dir}/vfdb_vfdb_comparison.megan")

    shell.close()


def main():

    genus_name = input("Enter genus name: ")

    fetch_genus(genus_name)

    genus_job_creator(genus_name)

    comparison_creator(genus_name)

    pass


if __name__ == '__main__':
    main()
