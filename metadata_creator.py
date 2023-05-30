import urllib.request
import os
import time



def ncbi_datasets_installer():
    dir_content = os.listdir()
    
    if not "datasets" in dir_content:
        print("NCBI command line tools 'datasets' not found, installing...")
        os.system("curl -o datasets 'https://ftp.ncbi.nlm.nih.gov/pub/datasets/command-line/v2/linux-amd64/datasets'")
        os.system("chmod +x datasets")
    else:
        os.system("chmod +x datasets")
    
    return True



def species_name_finder():
    genus_name = input("Please enter genus name:")
    
    
    
    return True



def main():
    ncbi_datasets_installer()
    #species_name_finder()



if __name__ == '__main__':
    main()

