import json

# Load file A
with open('../HankGreen.json', 'r') as f:
    data_A = json.load(f)

# Load file B
with open('FixedAdditions.json', 'r') as f:
    data_B = json.load(f)

# Iterate over each dictionary in the list from file B
for dict_B in data_B:
    # For each category in dict_B
    for category, value in dict_B.items():
        # If the category also exists in data_A
        if category in data_A:
            # Check if the value is a list
            if isinstance(value, list):
                for v in value:  # for each dict in the list
                    if isinstance(v, dict):  # make sure it's a dictionary
                        data_A[category].update(v)  # update with each dict
            else:
                # Update the category in data_A with the data from dict_B
                data_A[category].update(value)

# Save combined data to a new file
with open('../combined_Hank_Green.json', 'w') as f:
    json.dump(data_A, f)
