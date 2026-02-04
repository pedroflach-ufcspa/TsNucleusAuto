import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import json
# ==========================
# MACHINE-SPECIFIC PATH
# ==========================

RUN_FILE = "/home/pedro/Documentos/ic/TOPAS-nBio/examples/scorers/SBSDamageToDNANucleus/ExampleNucleusDNADamage.txt"


def get_header(path: str) -> list:
    columns = []

    with open(path) as file:
        index = 0
        lines = file.readlines()

        for line in range(len(lines)):
            if lines[line].__contains__("as follow"):
                index = line + 1
                break
        for column in range(index, len(lines) - 1):
            content = lines[column].split(":")[-1].strip()
            if content != "":
                columns.append(content)
        return columns

def get_phsp(path: str, header: list) -> pd.DataFrame:
    return pd.read_csv(path, names=header, sep=r"\s+")

def get_dataframe(filename: str, dirpath: str) -> pd.DataFrame:
    """
        :param filename: name of the file (without extension)
        :param dirpath: path to the directory where the file is located
        :return: The dataframe for the analysis
    """

    header = get_header(f"{dirpath}/{filename}.header")
    return get_phsp(f"{dirpath}/{filename}.phsp", header)

def create_seed_dir(folder_name: str, tgt_dir: str = "outputs") -> int:

    """
    Method used to create the directory for the new simulation
    :param tgt_dir: Partial path to the folder (final path will be tgt_dir/folder_name)
    :param folder_name: Name of the folder
    :return: The seed number
    """

    os.makedirs(tgt_dir+"/"+folder_name, exist_ok=True)
    files = os.listdir(f"{tgt_dir}/{folder_name}")

    index = len(files) + 1
    if index == 0:
        new_dir = f"{tgt_dir}/{folder_name}/seed1"
    else:
        new_dir = f"{tgt_dir}/{folder_name}/seed{index}"

    os.makedirs(new_dir, exist_ok=True)
    return index

def move_files(folder_name, src_dir: str, include_list: list[str], tgt_dir: str = "outputs"):

    """
    Method used to move the files generated at the end of the simulation
    :param folder_name: Name of the folder created
    :param src_dir: path to the directory where the files are located.
    :param include_list: Files that are going to be moved during the process.
    :param tgt_dir: Partial path name where the files are going to be moved (final path will be tgt_dir/folder_name)
    """

    index = create_seed_dir(folder_name,tgt_dir)

    check_list = os.listdir(src_dir)

    for file in check_list:
        if file in include_list:
            os.rename(
                os.path.join(src_dir, file),
                f"{tgt_dir}/{folder_name}/seed{index}/{file}"
            )

def read_param_file(filename: str) -> dict[str, dict]:

    """
    Method used to read the parameters file
    :param filename: Name of the parameter file (without extension)
    :return: A dictionary containing the parameters
    """

    with open(f"{filename}.json") as file:
        return json.load(file)

def check_simulation(run_dir: str) -> bool:
    """
    Check if the simulation finished successfully.
    A successful simulation must generate a non-empty DNADamage.phsp file.
    """

    phsp_path = os.path.join(run_dir, "DNADamage.phsp")

    if os.path.exists(phsp_path):
        if os.path.getsize(phsp_path) > 0:
            return True

    return False

def check_seeds(folder_name, tgt_dir: str = "topas/outputs") -> int:
    """
    Method used to check if the seeds are complete.
    :return: Current number of seeds (this will be checked based in the directory seed number in the folder name)
    """

    seeds = os.listdir(f"{tgt_dir}/{folder_name}")
    seed_numbers = [int(seeds.split("d")[-1]) for seeds in seeds]
    return np.max(seed_numbers)

def update_parameters(params: dict):

    with open(RUN_FILE, "r") as file:
        lines = file.readlines()

    with open(RUN_FILE, "w") as file:
        for line in lines:
            if "=" not in line:
                file.write(line)
                continue

            key = line.split("=")[0]

            if "Seed" in key:
                new_value = params["seeds"]
            elif "BeamParticle" in key:
                new_value = f'"{params["particle"]}"'
            elif "BeamEnergy" in key:
                new_value = f"{params['energy']} MeV"
            elif "NumberOfHistoriesInRun" in key:
                new_value = params["histories"]
            else:
                new_value = None

            if new_value is not None:
                line = f"{key} = {new_value}\n"

            file.write(line)


def save_problematic_seed(seed: int, particle: str):
    if os.path.exists("p_seeds.txt"):
        with open("p_seeds.txt", 'r') as file:
            lines = file.readlines()
    else:
        lines = []

    with open("p_seeds.txt", "w") as file:
        lines.append(f"{particle}: {seed}\n")
        file.writelines(lines)