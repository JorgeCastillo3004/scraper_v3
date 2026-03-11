"""
paralel_execution.py

Lanza N drivers en paralelo, distribuyendo las ligas habilitadas en
leagues_info.json entre ellos y ejecutando extraction_by_dict por worker.

Uso:
    python paralel_execution.py <n_sessions> <name_section>

Ejemplos:
    python paralel_execution.py 3 results
    python paralel_execution.py 2 fixtures
"""

import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, '/home/you/work_2026')

import milestone4
import common_functions
from common_functions import launch_navigator, load_check_point
from milestone4 import extraction_by_dict


# ─────────────────────────────────────────────
#  LOCK GLOBAL — protege escrituras en leagues_info.json
# ─────────────────────────────────────────────
_file_lock = threading.Lock()
_original_save = common_functions.save_check_point


def _locked_save(*args, **kwargs):
    with _file_lock:
        _original_save(*args, **kwargs)


# Monkey-patch en ambos módulos que llaman a save_check_point
milestone4.save_check_point      = _locked_save
common_functions.save_check_point = _locked_save


# ─────────────────────────────────────────────
#  CONSTANTES
# ─────────────────────────────────────────────
LEAGUES_INFO_FILE = 'check_points/leagues_info.json'
SUPPORTED_SPORTS  = ['FOOTBALL', 'BASKETBALL', 'BASEBALL', 'AM._FOOTBALL', 'HOCKEY']


# ─────────────────────────────────────────────
#  FUNCIONES DE DISTRIBUCIÓN
# ─────────────────────────────────────────────

def get_enabled_leagues(name_section='results'):
    """
    Lee leagues_info.json y retorna lista de (sport, league_name)
    donde el flag extract está habilitado.
    """
    extract_key   = 'extract_results' if name_section == 'results' else 'extract_fixtures'
    leagues_info  = load_check_point(LEAGUES_INFO_FILE)
    enabled       = []

    for sport, leagues in leagues_info.items():
        if sport not in SUPPORTED_SPORTS:
            continue
        for league_name, league_info in leagues.items():
            if league_info.get(extract_key, {}).get('extract', False):
                enabled.append((sport, league_name))

    print(f'[DIST] Total ligas habilitadas ({name_section}): {len(enabled)}')
    return enabled


def split_into_dicts(enabled_leagues, n_sessions):
    """
    Distribuye la lista de (sport, league) en N dicts round-robin.
    Retorna lista de N dicts: [{'FOOTBALL': [...], 'BASKETBALL': [...]}, ...]
    """
    dicts = [{} for _ in range(n_sessions)]

    for i, (sport, league) in enumerate(enabled_leagues):
        worker_idx = i % n_sessions
        dicts[worker_idx].setdefault(sport, []).append(league)

    for idx, d in enumerate(dicts):
        total = sum(len(v) for v in d.values())
        print(f'[DIST] Worker {idx}: {total} ligas → {d}')

    return dicts


# ─────────────────────────────────────────────
#  WORKER
# ─────────────────────────────────────────────

def worker(worker_id, sport_leagues_dict, name_section):
    """
    Lanza un driver propio y ejecuta extraction_by_dict con el subset asignado.
    """
    print(f'[WORKER {worker_id}] Iniciando driver...')
    driver = launch_navigator('https://www.flashscore.com', headless=True)

    try:
        print(f'[WORKER {worker_id}] Iniciando extracción — sección: {name_section}')
        extraction_by_dict(driver, sport_leagues_dict, name_section=name_section)
        print(f'[WORKER {worker_id}] Extracción completada.')
    except Exception as e:
        print(f'[WORKER {worker_id}] ERROR: {e}')
        raise
    finally:
        driver.quit()
        print(f'[WORKER {worker_id}] Driver cerrado.')


# ─────────────────────────────────────────────
#  ENTRADA PRINCIPAL
# ─────────────────────────────────────────────

def run_parallel(n_sessions, name_section='results'):
    """
    Distribuye ligas habilitadas entre N workers y los lanza en paralelo.
    """
    enabled      = get_enabled_leagues(name_section)
    league_dicts = split_into_dicts(enabled, n_sessions)

    print(f'\n[MAIN] Lanzando {n_sessions} workers para sección: {name_section}\n')

    with ThreadPoolExecutor(max_workers=n_sessions) as executor:
        futures = {
            executor.submit(worker, idx, d, name_section): idx
            for idx, d in enumerate(league_dicts)
        }
        for future in as_completed(futures):
            idx = futures[future]
            try:
                future.result()
                print(f'[MAIN] Worker {idx} terminó OK.')
            except Exception as e:
                print(f'[MAIN] Worker {idx} terminó con ERROR: {e}')

    print('\n[MAIN] Todos los workers finalizados.')


if __name__ == '__main__':
    n_sessions   = int(sys.argv[1])   if len(sys.argv) > 1 else 2
    name_section = sys.argv[2]        if len(sys.argv) > 2 else 'results'
    run_parallel(n_sessions, name_section)
