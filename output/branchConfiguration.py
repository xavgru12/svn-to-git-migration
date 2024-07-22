import subprocess
import data.configuration as configuration
import parser.branchConfigurationParser
import model.branchModel


def add(data_object):
    branch_configuration = parser.branchConfigurationParser.parse()

    generic_configuration = branch_configuration["generic"]

    for branch_type in generic_configuration.keys():
        generate_branches(
            data_object,
            branch_type,
            generic_configuration[branch_type]["folders"],
            generic_configuration[branch_type].get("subfolders"),
        )


def generate_branches(data_object, branch_type, folders, subfolders):
    existing_branches = []

    if folders is None:
        raise Exception(
            f"folders does not exist in branchConfiguration.json for branch type: {branch_type}"
        )

    existing_folders = add_folders(folders, branch_type, data_object.remote_path)
    existing_branches.extend(existing_folders)

    if subfolders is not None:
        existing_subfolders, ignore_refs_subfolders = add_subfolders(
            folders, subfolders, branch_type, data_object.remote_path
        )
        existing_branches.extend(existing_subfolders)
        data_object.ignore_refs.extend(ignore_refs_subfolders)

    data_object.branches.extend(existing_branches)


def add_folders(folders, branch_type, remote_path):
    branch_list = []

    for folder in folders:
        if folder == "Uid" and "LogicalComponents (obsolete)/Uid" in remote_path:
            continue
        if remote_path.endswith(folder):
            branch = remote_path
        else:
            branch = f"{remote_path}/{folder}"

        branch_url = f"{configuration.get_base_server_url()}/{branch}"
        if check_for_existence(branch_url) is True:
            remote_part = f"refs/remotes/origin/{folder}"

            branch_line_string = build_branch_string(branch_type, branch, remote_part)
            branch_list.append(branch_line_string)

    return branch_list


def add_subfolders(folders, subfolders, branch_type, remote_path):
    branch_list = []
    ignore_refs = []
    for folder in folders:
        for subfolder in subfolders:
            branch = f"{remote_path}/{folder}/{subfolder}"
            branch_url = f"{configuration.get_base_server_url()}/{branch}"
            # print(f"branch_url = {branch_url}")
            if check_for_existence(branch_url) is True:
                remote_part = f"refs/remotes/origin/sub{folder}/{subfolder}"
                branch_line_string = build_branch_string(
                    branch_type, branch, remote_part
                )

                ignore_ref_string = f"refs/remotes/origin/{folder}/{subfolder}"
                build_ignore_ref_string(ignore_refs, branch_type, ignore_ref_string)

                branch_list.append(branch_line_string)
    return branch_list, ignore_refs


def check_for_existence(complete_branch):
    complete_branch = complete_branch.replace(" ", "%20")
    process_string = f"svn info {complete_branch}"
    result = subprocess.run(
        process_string.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False


def build_branch_string(branch_type, branch, remote_part):
    if branch_type == "trunk":
        string_type = "fetch"
        wildcard = ""
    else:
        string_type = branch_type
        wildcard = "/*"

    line_string = f"{string_type} = {branch}{wildcard}:{remote_part}{wildcard}"
    return line_string


def build_ignore_ref_string(ignore_refs, branch_type, remote_part):
    if branch_type != "trunk":
        ignore_refs.append(remote_part)


def set_repo_configuration_from(remote_path, branch_dict):
    if remote_path not in branch_dict:
        repo_name = parser.branchConfigurationParser.parse_repo_name(remote_path)
        print(f"{remote_path}: {repo_name}")
        data = model.branchModel.BranchModel(repo_name, remote_path)
        data.branches = []
        data.ignore_refs = []
        add(data)
        branch_dict[remote_path] = data
