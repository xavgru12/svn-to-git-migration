import json


def parse():
    with open("data/branchConfiguration.json", "r") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise Exception("reading branch configuration failed")

    return data


def parse_repo_name(remote_path):
    name = remote_path.split("/")[-1]
    if name == "HC-Q":
        return "ag-hcq"
    elif name == "CuRMiT":
        return "ag-curmit"
    elif name == "eX1":
        return "ag-system-firmware"
    replace_underscore = name.replace("_", "-")
    replace_capitals = replace_capitals_with_lower_case_dash(replace_underscore)

    replace_stm_string = (
        replace_capitals.replace("stm32-f4", "stm32f4")
        .replace("stm32-l4xx", "stm32l4xx")
        .replace("stm32-f7", "stm32f7")
    )
    repo_name = replace_stm_string.replace("--", "-")
    ag_repo_name = "ag-" + repo_name
    ag_repo_name = ag_repo_name.replace(" ", "")
    return ag_repo_name


def parse_subfolder_repo_name(repository_name, subfolder):
    branch_name = subfolder.replace("/", "-")
    destination_name = f"{repository_name}_{branch_name}_subfolder"
    destination_name = destination_name[:62]
    return destination_name


def replace_capitals_with_lower_case_dash(name):
    final_name = ""
    sequence = False

    for index, char in enumerate(name):
        if char.isupper() and sequence is False and index != 0:
            final_name = final_name + "-" + char.lower()
        else:
            final_name = final_name + char.lower()

        if char.isupper():
            sequence = True
        else:
            sequence = False

    return final_name


def get_top_and_sub_folders_from_configuration(branch_types):
    branch_configuration = parse()

    generic_configuration = branch_configuration["generic"]

    top_folders = get_all_folder_names_by_type(
        generic_configuration, "folders", branch_types
    )
    sub_folders = get_all_folder_names_by_type(
        generic_configuration, "subfolders", branch_types
    )

    return top_folders, sub_folders


def get_all_variations_as_list():
    branch_types = ["trunk", "branches", "tags"]
    top_folders, sub_folders = get_top_and_sub_folders_from_configuration(branch_types)

    return get_all_variations(top_folders, sub_folders)


def get_all_branch_name_variations_as_list():
    branch_types = ["branches"]
    top_folders, sub_folders = get_top_and_sub_folders_from_configuration(branch_types)

    return get_all_variations(top_folders, sub_folders)


def get_all_tag_top_folders_as_list():
    branch_types = ["tags"]
    top_folders, _ = get_top_and_sub_folders_from_configuration(branch_types)

    return top_folders


def get_all_tag_sub_folders_as_list():
    branch_types = ["tags"]
    _, sub_folders = get_top_and_sub_folders_from_configuration(branch_types)

    return sub_folders


def get_all_branch_top_folders_as_list():
    branch_types = ["branches"]
    top_folders, _ = get_top_and_sub_folders_from_configuration(branch_types)

    return top_folders


def get_all_trunk_variations_as_list():
    branch_types = ["trunk"]
    top_folders, sub_folders = get_top_and_sub_folders_from_configuration(branch_types)

    return get_all_variations(top_folders, sub_folders)


def get_all_tag_name_variations_as_list():
    branch_types = ["tags"]
    top_folders, sub_folders = get_top_and_sub_folders_from_configuration(branch_types)

    return get_all_variations(top_folders, sub_folders)


def get_all_folders_with_subfolders_variations_as_list():
    branch_types = ["trunk", "branches", "tags"]
    top_folders, sub_folders = get_top_and_sub_folders_from_configuration(branch_types)

    return get_all_folders_with_subfolders(top_folders, sub_folders)


def get_all_folder_names_by_type(generic_configuration, folder_type, branch_types):
    folders = []

    for branch_type in generic_configuration.keys():
        if branch_type in branch_types:
            folder = generic_configuration[branch_type].get(folder_type)
            if folder is not None:
                folders.extend(folder)

    return folders


def get_all_branch_folder_names(generic_configuration, folder_type):
    branch_types = ["trunk", "branches"]
    folders = []

    for branch_type in generic_configuration.keys():
        if branch_type in branch_types:
            folder = generic_configuration[branch_type].get(folder_type)
            if folder is not None:
                folders.extend(folder)

    return folders


def get_all_folders_with_subfolders(top_folders, sub_folders):
    variations = []
    for top_folder in top_folders:
        for sub_folder in sub_folders:
            variation = f"{top_folder}/{sub_folder}"
            variations.append(variation)

    return variations


def get_all_variations(top_folders, sub_folders):
    variations = get_all_folders_with_subfolders(top_folders, sub_folders)

    variations.extend(top_folders)

    return variations
