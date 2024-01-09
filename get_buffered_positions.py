def get_buffered_position(
    position : int,
    held_position : int,
    buffer_fraction : float) -> int:

    lower_bound = held_position * (1 - buffer_fraction)
    upper_bound = held_position * (1 + buffer_fraction)

    if (position < lower_bound) or (position > upper_bound):
        return round(position)
    
    return held_position

def get_buffered_positions(
    positions : dict,
    held_positions : dict,
    buffer_fraction : float) -> dict:

    buffered_positions = {}

    for instrument in list(positions.keys()):
        buffered_positions[instrument] = get_buffered_position(
            position=positions[instrument],
            held_position=held_positions[instrument],
            buffer_fraction=buffer_fraction)
        
    return buffered_positions
