import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Methods for reading the output files
# First, read the dataframe using the getDataframe method

def filterPlotData(data: list, step: int, startIndex: int, endIndex: int) -> list:

    elements = []

    if endIndex == 0: endIndex = len(data)
    filter_data = data[startIndex:endIndex]
    elements_to_keep = len(filter_data) / step
    for index in range(0, int(elements_to_keep)):
        elements.append(filter_data[index * step])
    return elements


def getResultsByMolecule(df: pd.DataFrame, name: str) -> pd.DataFrame:
    """
    Filter the dataframe to only display information about a specific molecule
    :param df: dataframe
    :param name: molecule name
    :return:
    """
    filtered = df[df["Molecule"] == name]
    return filtered


def getMolecules(df: pd.DataFrame) -> list:
    """
    Get the list of unique molecules on the simulation
    :param df: dataframe
    :return:
    """
    return df["Molecule"].unique()

def getDataframe(fileName: str, dirPath: str) -> pd.DataFrame:
    """
    Return the dataframe for the analysis
    :param fileName: name of the file (without extension)
    :param dirPath: path to the directory where the file is located
    :return:
    """
    header = getHeader(f"{dirPath}/{fileName}.header")
    phsp = getPHSP(f"{dirPath}/{fileName}.phsp", header)
    return phsp

def getPHSP( path: str, header: list) -> pd.DataFrame:
    return pd.read_csv(path, names=header, sep=r"\s+").fillna("none")

def getHeader( path: str) -> list:
    """
    Get the column elements for the dataframe
    :param path: path to the directory where the file is located
    :return:
    """
    with open(path) as file:
        columns = []
        data = file.readlines()
        for index in range(4, len(data)):
            content = data[index].split(":")[-1].strip()
            if content != "":
                columns.append(content)
    return columns

def organizeByMolecules( df: pd.DataFrame) -> dict:
    """
    Create a dictionary, separating the entire dataframe by molecule name
    :param df: dataframe
    :return:
    """
    by_molecule = {}
    for molecule in getMolecules(df):
        new_dataframe = getResultsByMolecule(df, molecule)
        by_molecule[molecule] = new_dataframe
    return by_molecule


def yieldByTimeSingleMolecule(df: pd.DataFrame, molecule: str, step: int = 10, startIndex: int = 0,
                              endIndex: int = 0, log: bool = True) -> None:

    """
    Used to plot the yield of a specific scenario per molecule

    :param df: Dataframe being analyzed
    :param molecule: molecule name
    :param step: Number of steps to filter plot data
    :param startIndex: starting index of the data list (useful if you need to analyze better some smaller areas)
    :param endIndex: end index of the data list (useful if you need to analyze better some smaller areas)
    :param log: use log system?
    :return:
    """

    df = getResultsByMolecule( df, molecule)

    if step != 0:
        x = filterPlotData(list(df["Time [ps]"]), step, startIndex, endIndex)
        y = filterPlotData(list(df["Yield"]), step, startIndex, endIndex)
    else:
        x = df["Time [ps]"]
        y = df["Yield"]

    if log:
        x = np.log(x)

    plt.figure(figsize=(8, 6))
    plt.xlabel("Time [ps] in log scale")
    plt.ylabel("Yield")
    plt.title(f"{molecule} yield")
    plt.scatter(x, y)
    plt.show()


def yieldByTimeMultipleScenarios(dfs: dict[str, pd.DataFrame], molecule: str, step: int = 10, startIndex: int = 0,
                                 endIndex: int = 0, log: bool = True) -> None:

    """
    Used to plot multiple dataframes at the same graph

    :param dfs: Dictionary of Dataframes being analyzed, the key string is the legend description
    :param molecule: molecule name
    :param step: Number of steps to filter plot data
    :param startIndex: starting index of the data list (useful if you need to analyze better some smaller areas)
    :param endIndex: end index of the data list (useful if you need to analyze better some smaller areas)
    :param log: use log system?
    :return:
    """

    plt.figure(figsize=(8, 6))
    legend_elements = []

    for index in range(len(dfs)):
        result = getResultsByMolecule(list(dfs.values())[index], name=molecule)
        legend = list(dfs.keys())[index]
        legend_elements.append(legend)

        if step != 0:
            x = filterPlotData(list(result["Time [ps]"]), step, startIndex, endIndex)
            y = filterPlotData(list(result["Yield"]), step, startIndex, endIndex)
        else:
            x = result["Time [ps]"]
            y = result["Yield"]

        if log:
            x = np.log(x)

        plt.scatter(x, y)

    plt.legend(legend_elements)
    plt.xlabel("Time [ps] in log scale")
    plt.ylabel("Yield")
    plt.title(f"{molecule} yield for multiple scenarios")
    plt.show()
