import re

import parser.branchConfigurationParser


def is_type_external_subfolders(branch_name):
    possible_branch_names = (
        parser.branchConfigurationParser.get_all_variations_as_list()
    )
    for possible_branch_name in possible_branch_names:
        if possible_branch_name == branch_name:
            return None

    suitable_branch = find_most_suitable_branch_name(branch_name)
    if suitable_branch is not None:
        possible_subfolder_branch = branch_name.replace(f"{suitable_branch}/", "")
        if "/" in possible_subfolder_branch:
            cut_off_branch_from_subfolder = re.sub(
                r"^.*?/", "", possible_subfolder_branch
            )
            return cut_off_branch_from_subfolder

    return None


def find_most_suitable_branch_name(branch_name):
    possible_branch_names = (
        parser.branchConfigurationParser.get_all_variations_as_list()
    )
    for possible_branch_name in possible_branch_names:
        if possible_branch_name in branch_name:
            return possible_branch_name
