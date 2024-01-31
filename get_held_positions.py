import pandas as pd

def get_held_positions(instruments : list, positions_path : str) -> dict:
    #!! NOTE: This function needs to source its data properly, from SQL or whatever

    held_positions = {}
    for instrument in instruments:
        held_positions[instrument] = 0.0

    return held_positions

if __name__ == '__main__':
    print(get_held_positions('CSVs/instruments.csv', 'CSVs/positions.csv'))