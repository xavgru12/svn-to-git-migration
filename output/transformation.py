import shutil
import os
import re
import subprocess
import multiprocessing
import output.shutil_execute
import data.configuration as configuration
import output.external_checker
import output.subprocess_execution
import parser.branchConfigurationParser


def upload(repository_names):
    path = configuration.get_migration_output_path()
    repository_names = list(set(repository_names))

    # debug
    # for repository_name in repository_names:
    #     repository_path = os.path.join(path, repository_name)
    #     upload_each(repository_path)

    repository_paths = []
    for repository_name in repository_names:
        repository_path = os.path.join(path, repository_name)
        repository_paths.append(repository_path)

    with multiprocessing.Pool() as pool:
        for result in pool.imap(upload_each, repository_paths):
            if isinstance(result, Exception):
                print("Got exception: {}".format(result))
        pool.close()
        pool.join()


def upload_each(repository_path):
    working_directory = copy_repository_to_transformation_output_path(repository_path)
    print(f"working directory: {working_directory}")
    transform_git_bridge_to_native_git(working_directory)


def copy_repository_to_transformation_output_path(repo_path):
    name = os.path.basename(repo_path)
    destination = configuration.get_transformation_output_path()
    destination_repo_path = os.path.join(destination, name)
    os.makedirs(destination, exist_ok=True)

    output.shutil_execute.delete(destination_repo_path)
    print(destination_repo_path)
    shutil.copytree(repo_path, destination_repo_path)

    destination_path = os.path.join(destination, name)
    return destination_path


def transform_git_bridge_to_native_git(repo_path):
    git_bridge_folder = os.path.join(repo_path, ".git", "svn")
    if not os.path.exists(git_bridge_folder):
        raise FileNotFoundError(
            f'directory is not a git bridge repository: "{git_bridge_folder}"'
        )

    repo_name = create_repo_name(repo_path)
    add_remote_origin(repo_name, repo_path)
    check_remote_origin_exists(repo_path)
    branches_with_subfolders = parser.branchConfigurationParser.get_all_folders_with_subfolders_variations_as_list()
    branch_top_folders = (
        parser.branchConfigurationParser.get_all_branch_top_folders_as_list()
    )
    tag_top_folders = parser.branchConfigurationParser.get_all_tag_top_folders_as_list()
    tag_sub_folders = parser.branchConfigurationParser.get_all_tag_sub_folders_as_list()
    all_trunk_variations = (
        parser.branchConfigurationParser.get_all_trunk_variations_as_list()
    )
    transform_branches(
        repo_path, branches_with_subfolders, all_trunk_variations, branch_top_folders
    )
    transform_tags(repo_path, tag_top_folders, tag_sub_folders)


def create_repo_name(repo_path):
    base_name = os.path.basename(repo_path)
    repo_name = f"{base_name}-no-externals"
    return repo_name


def add_remote_origin(repo_name, repo_path):
    url = f"git@bitbucket.org:curtisinst/{repo_name}.git"
    command = f"git remote add origin {url}"

    output.subprocess_execution.check_output_execute(command, repo_path)


def check_remote_origin_exists(repo_path):
    checker_command = "git ls-remote origin"
    try:
        output.subprocess_execution.check_output_execute(checker_command, repo_path)
    except:
        raise ValueError(
            f'error: remote origin for repository: "{repo_path}" does not exist'
        )


def remove_remote_origin(repo_path):
    command = "git remote remove origin"

    output.subprocess_execution.check_output_execute(command, repo_path)


def transform_branches(
    repo_path, branches_with_subfolders, all_trunk_variations, branch_top_folders
):
    command_list = ["git", "for-each-ref", "--format=%(refname:short)"]
    branches = []
    for line in output.subprocess_execution.continuous_execute(
        command_list, repo_path, "stdout"
    ):
        if "@" not in line:
            line = line.replace("\n", "")

            for branch_name in branch_top_folders:
                branch_pattern = f"origin.*{branch_name}/"

                branch_command = get_line_as_branch_command(
                    line, branch_pattern, branches_with_subfolders
                )
                branches.append(branch_command) if branch_command is not None else None

            for trunk_name in all_trunk_variations:
                trunk_pattern = f"origin/{trunk_name}"
                branch_command = get_line_as_trunk_command(
                    line, trunk_pattern, branches_with_subfolders
                )
                branches.append(branch_command) if branch_command is not None else None

            if "ag-curmit" in repo_path:
                tag_pattern = "origin.*distr/"
                branch_command = get_line_as_branch_command(
                    line, tag_pattern, branches_with_subfolders
                )
                branches.append(branch_command) if branch_command is not None else None

    name = os.path.basename(repo_path)
    log_name = f"logs/uploadBranches/{name}"
    os.makedirs(os.path.dirname(log_name), exist_ok=True)
    logger = output.logger.LoggerFactory.create(
        f"{name}-uploadBranches", f"{log_name}.log"
    )

    for branch in branches:
        logger.debug(branch)

    print("Uploading branches...")
    max_length = 32000  # max length of string seems to be 32767 characters
    base_command = "git push origin --force"
    branch_commands = generate_branch_commands(branches, max_length, base_command)
    for branch_command in branch_commands:
        output.subprocess_execution.check_output_execute(branch_command, repo_path)


def generate_branch_commands(branches, max_length, base_command):
    commands = []
    current_command = base_command
    for branch in branches:
        potential_command = f"{current_command} {branch}"
        if len(potential_command) > max_length:
            # If the current command would exceed max length, finalize it and start a new one
            commands.append(current_command.split())
            current_command = f"{base_command} {branch}"
        else:
            current_command = potential_command

    # Append the last command if it has content
    if current_command != base_command:
        commands.append(current_command.split())

    return commands


def get_line_as_branch_command(line, pattern, branches_with_subfolders):
    found_pattern = find(pattern, line)
    if found_pattern is None:
        return None

    for branch_with_subfolder in branches_with_subfolders:
        if line.endswith(branch_with_subfolder):
            return None

    remote_part = line.replace(found_pattern, "")
    if "trunk" in found_pattern:
        remote_part = "main"
    command = f"refs/remotes/{line}:refs/heads/{remote_part}"
    return command


def get_line_as_trunk_command(line, pattern, branches_with_subfolders):
    found_pattern = find(pattern, line)
    if found_pattern is None:
        return None

    for branch_with_subfolder in branches_with_subfolders:
        if line.endswith(branch_with_subfolder):
            return None

    remote_part = "main"
    command = f"refs/remotes/{line}:refs/heads/{remote_part}"
    return command


def find(pattern, line):
    match = re.match(pattern, line)
    if match:
        return match.group()


def transform_tags(repo_path, tag_top_folders, tag_sub_folders):
    # distr in ag-curmit must be treated as branch, do not make git tags for it
    if "ag-curmit" in repo_path:
        return

    command_list = ["git", "for-each-ref", "--format=%(refname:short) %(objectname)"]
    for line in output.subprocess_execution.continuous_execute(
        command_list, repo_path, "stdout"
    ):
        if "@" not in line:
            splitted_line = line.split()
            original_tag_name = splitted_line[0]
            commit_hash = splitted_line[1]

            for tag_top_folder in tag_top_folders:
                tag_pattern = f"origin.*{tag_top_folder}/"
                found_pattern = find(tag_pattern, original_tag_name)
                if found_pattern is not None:
                    if not is_broken_tag(original_tag_name, tag_sub_folders):
                        tag_name = original_tag_name.replace(found_pattern, "")
                        create_git_tag(commit_hash, tag_name, repo_path)

    print("Uploading tags...")
    push_local_git_tags(repo_path)


def is_broken_tag(original_tag_name, tag_sub_folders):
    for tag_sub_folder in tag_sub_folders:
        if original_tag_name.endswith(tag_sub_folder):
            print(original_tag_name)
            return True
    return False


def create_git_tag(commit_hash, tag_name, repo_path):
    description_command = ["git", "log", "-1", "--format=format:%B", commit_hash]
    description = output.subprocess_execution.check_output_execute(
        description_command, repo_path
    )
    tag_command = ["git", "tag", "-a", "-m", f'"{description}"', tag_name, commit_hash]

    name = os.path.basename(repo_path)
    log_name = f"logs/uploadTags/{name}"
    os.makedirs(os.path.dirname(log_name), exist_ok=True)
    logger = output.logger.LoggerFactory.create(f"{name}-uploadTags", f"{log_name}.log")

    logger.debug(f"working directory tag command: {repo_path}")
    logger.debug(f"{" ".join(tag_command)}")
    logger.debug("\n")
    logger.debug(20 * "-")
    try:
        output.subprocess_execution.check_output_execute(tag_command, repo_path)
    except subprocess.CalledProcessError as process:
        if not process.returncode == 128:
            raise ValueError(f'error: git tag: "{tag_name}" could not be created')


def delete_local_and_remote_git_tags(repo_path):
    fetch_command = "git fetch"
    output.subprocess_execution.check_output_execute(fetch_command, repo_path)
    get_local_tags_command = "git tag -l"
    for line in output.subprocess_execution.continuous_execute(
        get_local_tags_command, repo_path, "stdout"
    ):
        delete_local_tag_command = f"git tag -d {line}"
        output.subprocess_execution.check_output_execute(
            delete_local_tag_command, repo_path
        )

        delete_remote_tag_command = f"git push origin --delete {line}"
        output.subprocess_execution.check_output_execute(
            delete_remote_tag_command, repo_path
        )


def push_local_git_tags(repo_path):
    command = "git push origin --tags --force"

    output.subprocess_execution.check_output_execute(command, repo_path)
