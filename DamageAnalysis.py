import matplotlib.pyplot as plt

import Utils as utils

def get_damage(path: str, file_name: str, seeds: int = 3, dose: float = 1.0) -> dict[str, dict]:

    """
    Method used to calculate the total amount of damage with its associated standard deviation
    :param dose: Dose yeield to analyze damage
    :param path: File path directory
    :param file_name: File name (without extension)
    :param seeds: Number of seeds used to calculate the standard deviation
    :return: A dictionary with the damage type as key, and another dictionary with the standard deviation and damage yield values.
    """

    results: list[dict[str, float]] = [get_total_damage(utils.get_dataframe(file_name, f"{path}/seed{seed}"), dose=dose) for seed in range(1, seeds+1)]

    result_with_error = {
        "Total SSBs": {"value": 0, "error": 0.0, "values": []},
        "Total DSBs": {"value": 0, "error": 0.0, "values": []},
        "Direct SSBs": {"value": 0, "error": 0.0, "values": []},
        "Indirect SSBs": {"value": 0, "error": 0.0, "values": []},
        "Direct DSBs": {"value": 0, "error": 0.0, "values": []},
        "Indirect DSBs": {"value": 0, "error": 0.0, "values": []},
        "Ratio": {"value": 0, "error": 0.0, "values": []},
    }

    for result in results:
        for damagetype, value in result.items():
            result_with_error[damagetype]["value"] += value
            result_with_error[damagetype]["values"].append(value)
    for info in result_with_error.values():
        info["value"] = info["value"] / len(results)
        values: list[float] = info["values"]
        info["error"] = float(utils.np.std(values))

    return result_with_error

def get_total_damage(df: utils.pd.DataFrame, dose: float = 1.0) -> dict[str, float]:

    """
    Return the damage yield per Gy
    :param df: dataframe being analyzed
    :param dose: amount of dose (make sure that the simulation runs until this amount is reached)
    :return: A dictionary with the following keys (Total SSBs, Total DSBs, Direct SSBs, Indirect SSBs, Direct DSBs, Indirect DSBs )
    """

    reset_points = df['Dose_per_event_Gy'].diff() < 0
    print(reset_points)
    first_reset_index = reset_points.idxmin() if reset_points.any() else len(df)
    filter_df = df.loc[:first_reset_index-1]

    return {
        "Total SSBs": df["SSBs"].sum(),
        "Total DSBs": df["DSBs"].sum(),
        "Direct SSBs": df ["SSBs_Direct"].sum(),
        "Indirect SSBs": df["SSBs_Indirect"].sum(),
        "Direct DSBs": df["DSBs_Direct"].sum(),
        "Indirect DSBs": df["DSBs_Indirect"].sum(),
        "Ratio": df["SSBs"].sum() / df["DSBs"].sum()
    }

def get_damage_info(data: dict) -> None:

    """
    Method used to display a full description about the damage.
    :param data: The dictionary containing the damage info.
    :return:
    """

    info = ""
    for key, value in data.items():
        if type(value) == dict:
            info += f"{key}: {value["value"]:.2f}\n"
        else:
            info += f"{key}: {value:.2f}\n"
    print(info)

def plot_full_damage(damage: dict[str, float], log: bool = False) -> None:

    """
    Method used to plot all the information about damage yield in a single scenario
    :param log: Plot in log scale?
    :param damage: the dictionary containing the damage info, you can get this using the get_total_damage() method.
    :return:
    """

    utils.plt.figure(figsize=(6,6))
    for damagetype, value in damage.items():
        utils.plt.bar(damagetype, value)

    utils.plt.title("Damage Yield per Gy")

    y_label = "Damage Yield per Gy"

    if log:
        utils.plt.yscale("log")
        y_label += " (log scale)"
    utils.plt.xticks(rotation=90)
    utils.plt.ylabel(y_label)
    utils.plt.show()

def plot_full_damage_with_error(damage: dict[str, dict], log: bool = False):

    """
    Method used to plot all the information about damage yield in a single scenario with its associated standard deviation
    :param log: Plot in log scale?
    :param damage: dictionary containing the damage info, you can get this using the get_damage() method.
    :return:
    """

    utils.plt.figure(figsize=(5,6))
    utils.plt.tight_layout()

    y_label = "Damage Yield per Gy"

    for damagetype, info in damage.items():
        utils.plt.errorbar(damagetype, info["value"], yerr=info["error"], fmt="o", ecolor="black", capsize=8)
        utils.plt.xticks(rotation=90)

    if log:
        utils.plt.yscale("log")
        y_label += " (log scale)"

    utils.plt.title("Damage Yield (per Gy)")
    utils.plt.ylabel(y_label)
    utils.plt.show()

def compare_damage_with_error(damagelist: list[dict[str,dict]], scenarios: dict[str, int], damagetype: str = "Total DSBs"):
    """
    Method used to plot and compare different scenarios
    :param damagelist: A list of damage dictionaries that are going to be compared. The key value is the name used to be displayed in the legend.
    :param scenarios: A dictionary describing the name of the scenario and the energy used.
    :param damagetype: Name of the parameter to be analyzed
    :return:
    """

    legends = []
    plt.figure(figsize=(6,8))
    plt.title(damagetype)
    for index in range(len(damagelist)):
        x = list(scenarios.values())[index]
        y = damagelist[index][damagetype]["value"]
        yerr = damagelist[index][damagetype]["error"]
        plt.errorbar(x,y,yerr=yerr, fmt="o", ecolor="black", capsize=8)
        legends.append(list(scenarios.keys())[index])

    plt.legend(legends)
    plt.show()
