import urllib.parse, urllib.request, urllib.error
import os


def fetch_assembly():
    """\
    Downloads the NCBI Assembly file (as assembly_summary.txt) if it is not already present
    """
    dir_content = os.listdir()

    assembly_not_downloaded = not ("assembly_summary.txt" in dir_content)

    if assembly_not_downloaded:

        assembly_url = "https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/assembly_summary.txt"
        response = urllib.request.urlopen(assembly_url)
        web_content = response.read().decode("UTF-8")
        with open("assembly_summary.txt", "w") as file:
            file.write(web_content)
            file.close()
    
    else:
        return "assembly summary present"


def format_to_usability(string:str):
    """\
    Removes several characters (" ", ".", "/", ",") from a given string, if present, to enable use as link

    Parameters
    ----------
    string : String
        String to be formatted

    Returns
    -------
    formatted_string : String
        Formatted String


    """
    formatted_string = string.replace(" ", "_").replace(".", "_").replace("/", "_").replace(",", "_")

    return formatted_string


def fetch_genus():
    """\
    Parses the assembly file for a user-entered genus name, then creates and bashes a shell to download
    that genus' protein.faa.gz files from NCBI. The downloads are placed withina new directory {genus}/{genus}_protein
    """
    genus_name = input("Enter genus name: ").capitalize()
    species_count = 0

    assembly_file = open("assembly_summary.txt", "r")
    lines = assembly_file.readlines()

    assembly_header = lines[1].split("\t")

    # asm_lvl_index = assembly_header.index("assembly_level")
    ftp_index = assembly_header.index("ftp_path")
    accession_index = assembly_header.index("# assembly_accession")
    asm_name_index = assembly_header.index("asm_name")
    organism_name_index = assembly_header.index("organism_name")
    isolate_index = assembly_header.index("isolate")

    species_in_gattung = []

    with open("genus_DL.sh", "w") as shell:
        shell.write(f"mkdir {genus_name}\n")
        shell.write(f"cd {genus_name}\n")

        shell.write(f"mkdir {genus_name}_protein\n")
        shell.write(f"cd {genus_name}_protein/\n")

        shell.write(f"touch {genus_name}_records.txt\n")
        
        for line in lines:

            full_check = "Full" in line
            complete_check = "Complete Genome" in line

            if genus_name in line and (full_check or complete_check):

                contents = line.split("\t")

                species_count += 1

                species_in_gattung.append(line)

                strain_url = contents[ftp_index]

                asm_name = contents[asm_name_index].replace("/", "_")

                accession = contents[accession_index]

                organism_name = contents[organism_name_index]

                infra_name = contents[organism_name_index + 1]

                isolate = contents[isolate_index]

                if " " in asm_name:
                    asm_name = asm_name.replace(" ", "_")

                if " " in accession:
                    accession = accession.replace(" ", "_")
                
                # if " " in organism_name:
                #     organism_name = organism_name.replace(" ", "_")
                
                # if "." in organism_name:
                #     organism_name = organism_name.replace(".", "_")

                # if  "/" in organism_name:
                #     organism_name = organism_name.replace("/", "_")

                # if " " in infra_name:
                #     infra_name = infra_name.replace(" ", "_")

                # if "." in infra_name:
                #     infra_name = infra_name.replace(".", "_")

                if infra_name == "":
                    infra_name = f"isolate={isolate}"

                protein_url = f"{strain_url}/{accession}_{asm_name}_protein.faa.gz\n"

                strain_name = format_to_usability(f"{organism_name}_{infra_name}")
                
                shell.write(f"wget -O {strain_name}_protein.faa.gz {protein_url}\n")
                shell.write(f'echo "{accession}_{asm_name} downloaded as {strain_name}_protein.faa.gz" >> {genus_name}_records.txt\n')
                shell.write(f"gzip -d {strain_name}_protein.faa.gz\n")
                shell.write(f'echo "{strain_name}_protein.faa.gz unzipped" >> {genus_name}_records.txt\n')
                
        shell.close()

        if species_count == 0:
            print(f"No records for {genus_name} found in the NCBI assembly file, try something else")
            os.system("rm genus_DL.sh")
            exit()
        else:
            os.system(f"echo {species_count} species of genus {genus_name} found, downloading...")

    os.system("bash genus_DL.sh")
    os.system("rm genus_DL.sh")

    species_downloaded = len(os.listdir(f"{genus_name}/{genus_name}_protein/")) - 1
    print(f"{species_downloaded} species downloaded")

    return genus_name



def genus_job_creator(genus_name):
    """\
    Creates jobs for every species in the genus in batches of user-entered size, containing:
    - diamond run against nr database
    - meganization with mdb for resulting daa file
    - diamond run against vfdb database
    - sadly no automatic meganization with vfdb
    for each species

    Parameters
    ----------
    genus_name : String
        Name of the genus for which jobs are created, used to navigate to the correct directory

    """
    batch_size = input("Enter size of batches (influences max runtime (4h per species) and amount of jobs):")
    print("Creating jobs...")

    running_dir = os.getcwd()

    working_dir = f"{running_dir}/{genus_name}"
    os.chdir(working_dir)

    target_dir = f"{genus_name}_protein"

    target_dir_path = f"{working_dir}/{target_dir}"

    species_names = os.listdir(target_dir_path)

    species_count = len(species_names)
    
    batch_counter = 0

    nr_result_dir = f"{working_dir}/{genus_name}_nr_default_meganization"
    nr_vfdb_dir = f"{working_dir}/{genus_name}_nr_vfdb_meganization"
    vfdb_result_dir = f"{working_dir}/{genus_name}_vfdb_default_meganization"
    vfdb_vfdb_dir = f"{working_dir}/{genus_name}_vfdb_vfdb_meganization"
    batches_dir  = f"{working_dir}/batches"

    os.system(f"mkdir {nr_result_dir}")
    os.system(f"mkdir {nr_vfdb_dir}")
    os.system(f"mkdir {vfdb_result_dir}")
    os.system(f"mkdir {vfdb_vfdb_dir}")
    os.system(f"mkdir {batches_dir}")

    max_runtime = batch_size * 4

    for i in range(0, species_count):

        if i % batch_size == 0:
            batch_counter += 1

            job_name = genus_name + f"_batch_{batch_counter}.sh"
            job_dir = f"{batches_dir}/{job_name}"

            jobtext = ["#PBS -l nodes=1:ppn=8", f"\n#PBS -l walltime={max_runtime}:00:00", "\n#PBS -l mem=32gb",
                "\n#PBS -S /bin/bash", "\n#PBS -N " + job_name, "\n#PBS -j oe", "\n#PBS -o " + job_name + "_LOG",
                f"\ncd PBS_O_WORKDIR", '\necho "running on node:"', "\nuname -a"]

            with open(job_dir, "w") as shell:
                shell.writelines(jobtext)
                shell.close()
        
        nr_dia_part1 = f"\n/home/tu/tu_tu/tu_zxozy01/tools/diamond_15/diamond blastp -d {running_dir}/nr -q"
        nr_dia_part2 = "_result.daa -f 100 -b 5 -c 1 --threads 8"

        mdb_meg_part1 = "\n/home/tu/tu_tu/tu_zxozy01/tools/megan/tools/daa-meganizer -i"
        mdb_meg_part2 = "-mdb /home/tu/tu_tu/tu_zxozy01/tools/megan-map-Feb2022-ue.db"

        vfdb_dia_part1 = f"\n/home/tu/tu_tu/tu_zxozy01/tools/diamond_15/diamond blastp -d {running_dir}/vfdb -q"
        vfdb_dia_part2 = f"_result.daa -f 100 -b 5 -c 1 --threads 8"

        #vfdb_meg_part1 = "\n/home/tu/tu_tu/tu_zxozy01/tools/megan/tools/daa-meganizer -i "
        #vfdb_meg_part2 = " -P /home/tu/tu_tu/tu_zxozy01/tools/megan/class/resources/files/vfdb.map"

        target_filepath = target_dir_path + "/" + species_names[i]

        output_name = species_names[i][0:-4]

        f = open(job_dir, "a")
        # runs diamond against nr and vfdb, copies the files, meganizes one set automatically and leaves the other set to be manually meganized with vfdb (for now)
        f.write(f"{nr_dia_part1} {target_filepath} -o {nr_result_dir}/{output_name}{nr_dia_part2}")

        f.write(f"\ncp {nr_result_dir}/{output_name}_result.daa {nr_vfdb_dir}")

        f.write(f"{mdb_meg_part1} {nr_result_dir}/{output_name}_result.daa {mdb_meg_part2}")

        f.write(f"{vfdb_dia_part1} {target_filepath} -o {vfdb_result_dir}/{output_name}{vfdb_dia_part2}")

        f.write(f"\ncp {vfdb_result_dir}/{output_name}_result.daa {vfdb_vfdb_dir}")

        #f.write(f"{vfdb_meg_part1} {vfdb_result_dir}/{output_name}_result.daa {vfdb_meg_part2}")

        f.close()
    print(f"done, {batch_counter} jobs created")



def comparison_creator(genus_name):
    """\
    Creates a job to run comparisons for the meganized sets

    Parameters
    ----------
    genus_name : String
        Name of the genus for which jobs are created, used to navigate to the correct directory
        
    """
    # creates comparisons for the meganized sets (the manually meganized ones must be manually compared for now)

    working_dir = os.getcwd()

    nr_result_dir = f"{working_dir}/{genus_name}_nr_default_meganization"
    nr_vfdb_dir = f"{working_dir}/{genus_name}_nr_vfdb_meganization"
    vfdb_result_dir = f"{working_dir}/{genus_name}_vfdb_default_meganization"
    vfdb_vfdb_dir = f"{working_dir}/{genus_name}_vfdb_vfdb_meganization"

    jobtext = ["#PBS -l nodes=1:ppn=8", "\n#PBS -l walltime=02:00:00", "\n#PBS -l mem=32gb",
            "\n#PBS -S /bin/bash", "\n#PBS -N " + f"{genus_name}_comparison" , "\n#PBS -j oe", f"\n#PBS -o {genus_name}_comparison_LOG",
            f"\ncd PBS_O_WORKDIR", '\necho "running on node:"', "\nuname -a"]

    with open(f"{genus_name}_comparison.sh", "w") as shell:
        shell.writelines(jobtext)
        shell.close()

    comparison_cmd_part1 = "\nhome/tu/tu_tu/tu_zxozy01/tools/megan/tools/compute-comparison -i "

    shell = open(f"{genus_name}_comparison.sh", "a")

    shell.write(f"{comparison_cmd_part1}{nr_result_dir} -o {working_dir}/nr_default_comparison.megan")
    #shell.write(f"{comparison_cmd_part1}{nr_vfdb_dir} -o {working_dir}/nr_vfdb_comparison.megan")
    shell.write(f"{comparison_cmd_part1}{vfdb_result_dir} -o {working_dir}/vfdb_default_comparison.megan")
    #shell.write(f"{comparison_cmd_part1}{vfdb_vfdb_dir} -o {working_dir}/vfdb_vfdb_comparison.megan")

    shell.close()
    




def main():
    fetch_assembly()

    genus_name = fetch_genus()

    genus_job_creator(genus_name)

    comparison_creator(genus_name)



if __name__ == '__main__':
    main()
