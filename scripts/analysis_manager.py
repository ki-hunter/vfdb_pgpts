import job_creator as jc
import job_submitter as js
import os
from pathlib import Path


def check_relevant_files(file_list: list):

    cwd = os.getcwd()

    data_dir = Path(cwd + "/data")

    if Path.exists(data_dir):
        dir_content = os.listdir(data_dir)

    else:
        os.system(f"mkdir {data_dir}")

    with open(f"{data_dir}/filenames.txt") as f:
        file_list = f.readlines()

    file_present = []

    for file in file_list:
        if file in dir_content:
            file_present.append(True)
        else:
            file_present.append(False)

    for file, presence in zip(file_list, file_present):
        print(f"{file}: {presence}")

    pass


def get_relevant_filenames() -> list:

    cwd = os.getcwd()

    data_dir = Path(f"{cwd}/data")

    if not Path.exists(data_dir):
        print("creating dir")
        os.system(f"mkdir {data_dir}")

    filenames_path = Path(f"{data_dir}/filenames.txt")

    if Path.exists(filenames_path):
        with open(filenames_path, "r") as file:
            filenames = file.readlines()

    else:
        file = input("Please enter some filename:")

        with open(f"{data_dir}/filenames.txt", "w") as f:
            f.writelines(file)

    return filenames


def main():

    filenames = get_relevant_filenames()

    check_relevant_files(filenames)

    pass


if __name__ == '__main__':
    main()
