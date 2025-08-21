import shutil
import os
import pdb

import subprocess
import multiprocessing
import execution.shutil_execution
import data.configuration as configuration
import output.external_checker
import execution.subprocess_execution
import output.branch_name_conversion
import execution.git_execution


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

    execution.shutil_execution.delete(destination_repo_path)
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
    execution.git_execution.add_remote_origin(repo_name, repo_path)
    remote_exists = execution.git_execution.check_remote_origin_exists(repo_path)

    print_mode = True

    if remote_exists is False:
        if print_mode:
            execution.git_execution.add_missing_remote_to_file(repo_name)
            print(f"added missing remote: {repo_name}")
        else:
            raise ValueError(
                f'error: remote origin for repository: "{repo_name}" does not exist'
            )
    else:
        branch_name_conversion = output.branch_name_conversion.BranchNameConversion(
            repo_path
        )
        svn_git_branch_pairs = branch_name_conversion.create_branches_dictionary()
        svn_git_tag_pairs = branch_name_conversion.create_tags_dictionary()

        transform_branches(repo_path, svn_git_branch_pairs)
        transform_tags(repo_path, svn_git_tag_pairs)


def create_repo_name(repo_path):
    base_name = os.path.basename(repo_path)
    repo_name = f"{base_name}-no-externals"
    return repo_name


def transform_branches(repo_path, svn_git_branch_pairs):
    branch_commands = []
    for svn_branch, git_branch in svn_git_branch_pairs.items():
        command = f"refs/remotes/{svn_branch}:refs/heads/{git_branch}"
        branch_commands.append(command)

    name = os.path.basename(repo_path)
    log_name = f"logs/uploadBranches/{name}"
    os.makedirs(os.path.dirname(log_name), exist_ok=True)
    logger = output.logger.LoggerFactory.create(
        f"{name}-uploadBranches", f"{log_name}.log"
    )

    for branch in branch_commands:
        logger.debug(branch)

    print("Uploading branches...")
    max_length = 32000  # max length of string seems to be 32767 characters
    base_command = "git push origin --force"
    branch_command_list = generate_branch_commands(
        branch_commands, max_length, base_command
    )
    for branch_command in branch_command_list:
        try:
            execution.subprocess_execution.check_output_execute(
                branch_command, repo_path
            )
        except Exception:
            print(repo_path)
            breakpoint()


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


def transform_tags(repo_path, svn_git_tag_pairs):
    for svn_tag, git_tag in svn_git_tag_pairs.items():
        create_git_tag(svn_tag, git_tag, repo_path)

    print("Uploading tags...")
    execution.git_execution.push_local_git_tags(repo_path)


def create_git_tag(branch, tag_name, repo_path):
    description_command = ["git", "log", "-1", "--format=format:%B", branch]
    description = execution.subprocess_execution.check_output_execute(
        description_command, repo_path
    )
    tag_command = ["git", "tag", "-a", "-m", f'"{description}"', tag_name, branch]

    name = os.path.basename(repo_path)
    log_name = f"logs/uploadTags/{name}"
    os.makedirs(os.path.dirname(log_name), exist_ok=True)
    logger = output.logger.LoggerFactory.create(f"{name}-uploadTags", f"{log_name}.log")

    logger.debug(f"working directory tag command: {repo_path}")
    logger.debug(f"{' '.join(tag_command)}")
    logger.debug("\n")
    logger.debug(20 * "-")
    try:
        execution.subprocess_execution.check_output_execute(tag_command, repo_path)
    except subprocess.CalledProcessError as process:
        if not process.returncode == 128:
            raise ValueError(f'error: git tag: "{tag_name}" could not be created')


def delete_local_and_remote_git_tags(repo_path):
    execution.git_execution.fetch(repo_path)
    get_local_tags_command = "git tag -l"
    for line in execution.subprocess_execution.continuous_execute(
        get_local_tags_command, repo_path, "stdout"
    ):
        delete_local_tag_command = f"git tag -d {line}"
        execution.subprocess_execution.check_output_execute(
            delete_local_tag_command, repo_path
        )

        delete_remote_tag_command = f"git push origin --delete {line}"
        execution.subprocess_execution.check_output_execute(
            delete_remote_tag_command, repo_path
        )
