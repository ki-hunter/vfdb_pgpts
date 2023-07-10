import urllib.request
import os
import time
import bacdive
import pathlib
from job_creator import fetch_assembly


# def ncbi_datasets_installer():
#     dir_content = os.listdir()
    
#     if not "datasets" in dir_content:
#         print("NCBI command line tools 'datasets' not found, installing...")
#         os.system("curl -o datasets 'https://ftp.ncbi.nlm.nih.gov/pub/datasets/command-line/v2/linux-amd64/datasets'")
#         os.system("chmod +x datasets")
#     else:
#         os.system("chmod +x datasets")
    
#     return True

def credential_finder(credential_dir:pathlib.Path):

    with open(credential_dir, "r") as file:
        credentials = file.readlines()
    credentials[0] = credentials[0][:-1]

    credentials = {"em" : credentials[0], "pw" : credentials[1]}

    return credentials



def find_ncbi_ids(genus_name:str):

    fetch_assembly()

    assembly_file = open("assembly_summary.txt", "r", encoding="utf-8")
    lines = assembly_file.readlines()

    assembly_header = lines[1].split("\t")

    



    pass



def bacdive_client(genus_name:str):

    bacdive_credentials = pathlib.Path("C:/Users/Kilian/Documents/bacdive.txt")

    credentials = credential_finder(bacdive_credentials)

    em = credentials["em"]
    pw = credentials["pw"]

    client = bacdive.BacdiveClient(em, pw)

    genus_count =client.search(taxonomy=genus_name)

    # for strain in client.retrieve():
    #     print(strain)
    #     print("-----------------------------------------------------------------------------------------")
    #     pass

    filter = ["species","keywords", "NCBI tax id", "Pubmed-ID", "strain designation"]

    result = client.retrieve(filter)
    result_dict = ({k:v for x in result for k,v in x.items()})

    # for k, v in result_dict.items():
    #     print(k)
    #     print(v)
    #     print("---")

    # test = client.search(id="169529")

    # for strain in client.retrieve():
    #     print(strain)
    
    return result_dict



def get_species(search_result:dict):

    result = dict()

    for id, content in search_result.items():
        
        for item in content:
            if "species" in dict(item).keys():
                result.update({id:item["species"]})

    return result



def get_strain(search_result:dict):

    result = dict()

    for id, content in search_result.items():
        
        for item in content:
            if "strain designation" in dict(item).keys():
                result.update({id:item["strain designation"]})

    return result



def get_ncbi_id(search_result:dict):

    result = dict()

    limit = 12
    count = 0

    for id, content in search_result.items():
        if count < limit:
            print(content)
            for item in content:
                print(dict(item).keys())
                if "NCBI tax id" in dict(item).keys():
                
                    result.update({id : item})
        count += 1


    return result



def main():
    # ncbi_datasets_installer()
    #species_name_finder()
    genus_search_result = bacdive_client("Kosakonia")
    print(get_ncbi_id(genus_search_result))
    #find_ncbi_ids("Kosakonia")

    pass


if __name__ == '__main__':
    main()

