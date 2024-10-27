input_dict = {"1": "a", "distr": "b", "3": "b", "4": "c", "5": "d", "5": "e", "6": "h"}
print("input_dict:", input_dict)

# find duplicate values
# find keys of duplicate values
# add distr to value if distr in key

# Step 1: Find duplicate values
# Reverse the dictionary so that values map to a list of keys
from collections import defaultdict
import pdb


def find_duplicates(input_dict):
    value_to_keys = defaultdict(list)
    for key, value in input_dict.items():
        value_to_keys[value].append(key)

    # Find duplicates: values with more than one key
    duplicates = {value: keys for value, keys in value_to_keys.items() if len(keys) > 1}

    print("Duplicate Values:", duplicates)
    return duplicates


def modify_duplicate_values(input_dict, duplicates):
    modified_dictionary = input_dict
    for key, values in duplicates.items():
        breakpoint()
        if len(values) > 2:
            raise ValueError(
                f"more than two duplicate values in dictionary: {input_dict}"
            )
        has_distr = False
        for each_value in values:
            if "distr" in each_value:
                modified_dictionary[each_value] = f"distr/{key}"
                has_distr = True
        if has_distr is False:
            raise ValueError(f"distr was not found as key in duplicates: {values}")

    return modified_dictionary


def has_duplicates(dictionary):
    values = list(dictionary.values())
    return len(values) != len(set(values))


if has_duplicates(input_dict):
    duplicates = find_duplicates(input_dict)
    modified_input_dictionary = modify_duplicate_values(input_dict, duplicates)
    print("modified_input_dictionary:", modified_input_dictionary)
else:
    print("no duplicates")
# # Step 2: Find keys of duplicate values
# keys_of_duplicates = {value: keys for value, keys in value_to_keys.items() if len(keys) > 1}

# # Step 3: Add 'distr' to value if 'distr' is in the key
# modified_dict = {}
# for key, value in input_dict.items():
#     if 'distr' in key:
#         modified_dict[key] = value + 'distr'
#     else:
#         modified_dict[key] = value

# # Output the results
# print("Duplicate Values:", duplicates)
# print("Keys of Duplicate Values:", keys_of_duplicates)
# print("Modified Dictionary:", modified_dict)
