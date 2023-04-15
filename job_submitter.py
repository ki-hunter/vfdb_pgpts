import os
def submitting_shell():
    dir_content = os.listdir()
    gattung_name = input("Enter genus for which you want to submit jobs:").capitalize()
    cwd = os.getcwd()

    if gattung_name in dir_content:
        os.chdir(f"{gattung_name}/batches")
        batches = os.listdir()
        print(f"Found {len(batches)} batches, submitting...")
        
        for batch in batches:

            os.system(f"qsub -q short {batch}")
            print(f"{batch} submitted")
        
        print("Batches, submitted. Overview")
        os.system("qstat -u tu_zxozy01")

    else:
        return "No such genus present."

    
def main():
    submitting_shell()


if __name__ == '__main__':
    main()
