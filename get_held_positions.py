import pandas as pd

def get_held_positions(instruments_path : str, positions_path : str) -> dict:
    #!! NOTE: This function needs to source its data properly, from SQL or whatever
    instruments_file = pd.read_csv(instruments_path)

    data_symbols = instruments_file['Data Symbol'].tolist()

    held_positions = {}
    for data_symbol in data_symbols:
        held_positions[data_symbol] = 0.0

    return held_positions

if __name__ == '__main__':
    print(get_held_positions('CSVs/instruments.csv', 'CSVs/positions.csv'))