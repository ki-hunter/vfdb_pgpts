import urllib.request
import os
import time
import bacdive
import pathlib


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



def bacdive_client(genus_name:str):

    bacdive_credentials = pathlib.Path("C:/Users/Kilian/Documents/bacdive.txt")

    credentials = credential_finder(bacdive_credentials)

    em = credentials["em"]
    pw = credentials["pw"]

    client = bacdive.BacdiveClient(em, pw)

    genus_count =client.search(taxonomy=genus_name)

    for strain in client.retrieve():
        #print(strain)
        pass

    filter = ["keywords", "culture collection no."]

    result = client.retrieve(filter)
    print({k:v for x in result for k,v in x.items()})
    
    return True



def main():
    # ncbi_datasets_installer()
    #species_name_finder()
    bacdive_client("Pseudomonas")

    pass


if __name__ == '__main__':
    main()

