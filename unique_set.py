import pdb


list1 = [1, 2, 3, 2]
list2 = [4, 1, 5, 3]
list3 = [6, 2, 3, 7]

# # Initialize a set to track unique elements
# seen = set()

# # Using a list comprehension to iterate over all lists and add unique items
# unique_list = [item for lst in (list1, list2, list3) for item in lst if item not in seen and not seen.add(item)]

# print(unique_list)  # Output: [1, 2, 3, 4, 5, 6, 7]

complete_list = []

all_lists = [list1, list2, list3]

for each_list in all_lists:
    complete_list.extend(each_list)

breakpoint()

remove_duplicate_repositories = list(set(complete_list))

breakpoint()
