import os

import output.branch_name_conversion
import output.external_checker
import parser.branchConfigurationParser
import data.configuration as configuration
import execution.subprocess_execution
import execution.shutil_execution
import output.transformation
import execution.git_execution
import output.logger


def migrate(repositories):
    for repository in repositories:
        migrate_each(repository)


def migrate_each(repository):
    repository_name = parser.branchConfigurationParser.parse_repo_name(
        repository.remote_path
    )
    migration_output_path = configuration.get_migration_output_path()
    repository_path = os.path.join(migration_output_path, repository_name)
    print(repository)

    branch_name_conversion = output.branch_name_conversion.BranchNameConversion(
        repository_path
    )
    branches = branch_name_conversion.create_branches_dictionary()
    tags = branch_name_conversion.create_tags_dictionary()

    external_checker = output.external_checker.ExternalChecker(
        repository.branch_name, branches.keys(), tags.keys(), repository.remote_path
    )
    if external_checker.has_subfolder():
        upload_subfolder(
            external_checker,
            branches,
            tags,
            repository_name,
            repository.branch_name,
        )


def upload_subfolder(
    external_checker,
    branches,
    tags,
    repository_name,
    repository_branch_name,
):
    svn_extracted_branch_name = external_checker.get_extracted_branch_name()
    git_extracted_branch_name = branches.get(svn_extracted_branch_name)
    is_tag = False
    if git_extracted_branch_name is None:
        is_tag = True
        git_extracted_branch_name = tags[svn_extracted_branch_name]

    print_mode = False

    subfolder = external_checker.get_subfolder()
    if subfolder.endswith(".cs"):
        return

    repository_name_no_externals = f"{repository_name}-no-externals"
    transformation_path = configuration.get_transformation_output_path()

    destination_name = parser.branchConfigurationParser.parse_subfolder_repo_name(
        repository_name, subfolder
    )
    destination_path = os.path.join(transformation_path, destination_name)

    os.makedirs("logs/uploadSubfolders", exist_ok=True)
    logger = output.logger.LoggerFactory.create(
        "upload_subfolders", f"logs/uploadSubfolders/uploadSubfolders.log"
    )
    logger.debug(f"repository_name: {repository_name}")
    logger.debug(f"subfolder repository name: {destination_name}")
    logger.debug(f"branch as is: {repository_branch_name}")
    logger.debug(f"svn_extracted_branch_name: {svn_extracted_branch_name}")
    logger.debug(f"git_extracted_branch_name: {git_extracted_branch_name}")
    logger.debug(f"subfolder: {subfolder}")
    logger.debug(100 * "-")
    logger.debug("\n")

    execution.shutil_execution.delete(destination_path)
    checkout_git_repository(
        repository_name_no_externals,
        destination_name,
        git_extracted_branch_name,
        transformation_path,
    )

    if subfolder_exists(subfolder, destination_path) is False:
        commit_hash = find_commit_with_subfolder_deletion(subfolder, destination_path)
        reset_to_one_commit_before(commit_hash, destination_path)

    create_repository_from_external_subfolder(subfolder, destination_path)

    execution.git_execution.add_remote_upload(destination_name, destination_path)
    remote_exists = execution.git_execution.check_remote_upload_exists(destination_path)
    if remote_exists is False:
        if print_mode:
            execution.git_execution.add_missing_remote_to_file(destination_name)
            print(f"added missing remote: {destination_name}")
        else:
            raise ValueError(
                f'error: remote origin for repository: "{destination_name}" does not exist'
            )
    else:
        print(f"destination_path: {destination_path}")
        print(f"destination_name: {destination_name}")

        if is_tag:
            upload_tag_command = f"git push upload -f tag {git_extracted_branch_name}"
            execution.subprocess_execution.check_output_execute(
                upload_tag_command, destination_path
            )
        else:
            upload_branch_command = f"git push upload -f {git_extracted_branch_name}"
            execution.subprocess_execution.check_output_execute(
                upload_branch_command, destination_path
            )

        dummy_main_commands = [
            ["git", "checkout", "-b", "dummy_main"],
            ["git", "commit", "-m", "dummy main", "--allow-empty"],
            ["git", "push", "upload", "-f", "HEAD"],
        ]
        for each_command in dummy_main_commands:
            execution.subprocess_execution.check_output_execute(
                each_command, destination_path
            )


def subfolder_exists(subfolder, repo_path):
    path = os.path.join(repo_path, subfolder)
    return os.path.exists(path)


def find_commit_with_subfolder_deletion(subfolder, repo_path):
    command = [
        "git",
        "log",
        "--diff-filter=D",
        "-1",
        "--format=format:%H",
        "--",
        subfolder,
    ]
    output = execution.subprocess_execution.check_output_execute(command, repo_path)
    return output


def add_missing_remote_to_file(name):
    file_path = "remotes.txt"

    with open(file_path, "a") as file:
        file.write(f"{name}\n")


def reset_to_one_commit_before(commit_hash, repo_path):
    reset_command = f"git reset --hard {commit_hash}^"
    print(reset_command)
    execution.subprocess_execution.check_output_execute(reset_command, repo_path)


def create_repository_from_external_subfolder(external_subfolder, repo_path):
    sub_directory = os.path.join(repo_path, external_subfolder)

    if not os.path.exists(sub_directory):
        raise ValueError(
            f'error: subdirectory does not exist: "{sub_directory}", at: "{repo_path}"'
        )

    subfolder_command = f"git filter-repo --subdirectory-filter {external_subfolder} --force --prune-empty never"
    print(subfolder_command)
    execution.subprocess_execution.check_output_execute(subfolder_command, repo_path)


def checkout_git_repository(
    repository_name_no_externals, checkout_name, branch_name, working_directory
):
    clone_command = f"git clone -b {branch_name} git@bitbucket.org:curtisinst/{repository_name_no_externals}.git ./{checkout_name}"
    print(clone_command)
    execution.subprocess_execution.check_output_execute(
        clone_command, working_directory
    )
