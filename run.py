import subprocess
import time
import os
from datetime import datetime
import Utils as utils

# ============================================================
# MACHINE-SPECIFIC CONFIGURATION (EDIT ONLY THIS SECTION)
# ============================================================

# Caminho para o executável do TOPAS (resultado do `which topas`)
TOPAS_BIN = "/home/pedro/Documentos/ic/TOPAS/OpenTOPAS-install/bin/topas"

# Diretório onde está o script do TOPAS-nBio
# IMPORTANTE: esse diretório deve conter:
# - ExampleNucleusDNADamage.txt
# - supportFiles/
RUN_DIR = "/home/pedro/Documentos/ic/TOPAS-nBio/examples/scorers/SBSDamageToDNANucleus"

# Nome do script do TOPAS (somente o nome, sem caminho)
RUN_FILE = "ExampleNucleusDNADamage.txt"

# Caminho para as bibliotecas do Geant4
# Necessário para evitar erro: libG4Tree.so not found
GEANT4_LIB = "/home/pedro/Documentos/ic/GEANT4/geant4-install/lib"
GEANT4_SETUP = "/home/pedro/Documentos/ic/GEANT4/geant4-install/bin/geant4.sh"

# Arquivo de log
LOG_FILE = "simulation_log.txt"


def log_event(message: str, log_file: str = LOG_FILE) -> None:
    """Append log messages with timestamp to a text file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] {message}\n")


# ============================================================
# LOAD GEANT4 ENVIRONMENT (ESSENTIAL)
# ============================================================

env = os.environ.copy()

geant4_env_cmd = f"source {GEANT4_SETUP} && env"

result = subprocess.run(
    geant4_env_cmd,
    shell=True,
    executable="/bin/bash",
    capture_output=True,
    text=True
)

for line in result.stdout.splitlines():
    key, _, value = line.partition("=")
    env[key] = value

    # ============================================================
    # FORCE GEANT4 DATA VARIABLES (CRITICAL)
    # ============================================================

    GEANT4_DATA_DIR = "/home/pedro/Documentos/ic/GEANT4/G4DATA"

    env["G4ENSDFSTATEDATA"] = f"{GEANT4_DATA_DIR}/G4ENSDFSTATE2.3"
    env["G4NEUTRONHPDATA"] = f"{GEANT4_DATA_DIR}/G4NDL4.7"
    env["G4LEDATA"] = f"{GEANT4_DATA_DIR}/G4EMLOW8.2"
    env["G4LEVELGAMMADATA"] = f"{GEANT4_DATA_DIR}/PhotonEvaporation5.7"
    env["G4RADIOACTIVEDATA"] = f"{GEANT4_DATA_DIR}/RadioactiveDecay5.6"

# ============================================================
# LOAD SIMULATION PARAMETERS
# ============================================================

simulations = utils.read_param_file("params")

cur_seed = 0
successful_simulations = 0
tries = 0
last_setup = None

# ============================================================
# MAIN LOOP
# ============================================================

for name, params in simulations.items():

    seeds = params["seeds"]
    energy = params["energy"]
    particle = params["particle"]
    histories = params["histories"]
    current_setup = (energy, particle, histories)

    print(f"\nStarting simulation for scenario: {name}")
    if current_setup != last_setup:
        log_event("=" * 70)
        log_event("SETUP CHANGED")
        log_event(f"SCENARIO={name}")
        log_event(f"ENERGY={energy} MeV | PARTICLE={particle} | HISTORIES={histories}")
        log_event("=" * 70)
        last_setup = current_setup
    else:
        log_event(f"SCENARIO={name} | setup unchanged")

    log_event(f"START SCENARIO | target_successful_seeds={seeds}")
    time.sleep(1)

    while successful_simulations < seeds:

        # Atualiza parâmetros no run.txt (seed, energia, partícula, histories)
        simulation_params = {
            "seeds": cur_seed,
            "energy": energy,
            "particle": particle,
            "histories": histories
        }

        utils.update_parameters(simulation_params)

        folder_name = f"{name}_{energy}_{particle}"
        tgt_dir = "outputs"

        tries += 1
        print(f"Starting simulation for seed {cur_seed} (try {tries})...")
        log_event(f"RUN | scenario={name} | seed={cur_seed} | try={tries}")
        time.sleep(2)

        # Comando TOPAS
        cmd = f"{TOPAS_BIN} {RUN_FILE}"

        # EXECUTA O TOPAS NO DIRETÓRIO CORRETO
        process = subprocess.Popen(
            cmd,
            shell=True,
            cwd=RUN_DIR,   # <<< ESSENCIAL (resolve supportFiles)
            env=env        # <<< ESSENCIAL (resolve libG4Tree.so)
        )

        process.wait()
        time.sleep(1)

        print("Simulation finished. Checking for crashes...")

        # Verifica se o arquivo de saída foi criado corretamente
        outcome = utils.check_simulation(RUN_DIR)

        if outcome:
            print("Simulation successful. Moving output files...")
            log_event(f"SUCCESS | scenario={name} | seed={cur_seed} | try={tries}")

            include_list = [
                "DNADamage.phsp",
                "DNADamage.header",
                "DNADamage_full.csv",
                "DNADamage_sdd.txt"
            ]

            utils.move_files(
                folder_name,
                src_dir=RUN_DIR,
                include_list=include_list,
                tgt_dir=tgt_dir
            )

            successful_simulations += 1

        else:
            print("Simulation crashed. Saving problematic seed...")
            log_event(f"CRASH | scenario={name} | seed={cur_seed} | try={tries}")
            utils.save_problematic_seed(cur_seed, particle)

        cur_seed += 1
        time.sleep(1)

    print(f"\nFinished scenario: {name}")
    print(f"Total tries: {tries}")
    print(f"Successful simulations: {successful_simulations}")
    log_event(
        f"END SCENARIO | name={name} | total_tries={tries} | successful_simulations={successful_simulations}"
    )

    # Reset counters for next scenario
    cur_seed = 0
    successful_simulations = 0
    tries = 0

print("\nAll simulations finished.")
log_event("ALL SIMULATIONS FINISHED")
