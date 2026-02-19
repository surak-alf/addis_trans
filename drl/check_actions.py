def get_action_mapping():
    # Defining the lists here ensures they are the source of truth
    headway_options = [-240, -180, -120, -60, 0, 60, 120, 180, 240]
    dwell_options = [0, 30, 60]
    return headway_options, dwell_options

def print_action_table():
    headway_options, dwell_options = get_action_mapping()
    num_actions = len(headway_options) * len(dwell_options)

    print(f"{'Action ID':<10} | {'Headway Shift':<15} | {'Dwell Extension':<15}")
    print("-" * 45)

    for i in range(num_actions):
        h_idx = i // 3
        d_idx = i % 3
        
        h_val = headway_options[h_idx]
        d_val = dwell_options[d_idx]
        
        print(f"{i:<10} | {h_val:<15} | {d_val:<15}")
    
    print("-" * 45)
    print(f"Total Discrete Actions: {num_actions}")

if __name__ == "__main__":
    print_action_table()