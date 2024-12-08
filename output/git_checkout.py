import os
import re
import shutil
import subprocess

import parser.branchConfigurationParser
import data.configuration as configuration
import output.external_checker
import execution.shutil_execution
import execution.subprocess_execution
import execution.git_execution
import output.branch_name_conversion


def checkout(repository):
    """
    git checkout <commit_revision or origin/branch>
    """

    destination_directory = set_destination_directory(repository)
    if not output.external_checker.is_type_external_subfolders(repository.branch_name):
        repo_name = parser.branchConfigurationParser.parse_repo_name(
            repository.remote_path
        )
    else:
        name = parser.branchConfigurationParser.parse_repo_name(repository.remote_path)
        branch_name = repository.branch_name.replace("/", "-")
        repo_name = f"{name}_{branch_name}_subfolder-external"

    # output.external_subfolder_migration.migrate(repositories)
    # only works in pure git repositories, does not work in git svn
    # check here for remote_path and if longer than trunk/ etc then parse repo name from branchName, not remote path. git clone from online repository

    print(f"repo_name: {repo_name}")

    zip_file = f"{repo_name}.zip"
    zip_file_source_path = create_zip_file_path(zip_file)
    print(f"zip_file_path: {zip_file_source_path}")
    print(f"destination_directory: {destination_directory}")

    shutil.copy(zip_file_source_path, destination_directory)

    zip_file_destination_path = os.path.join(destination_directory, zip_file)
    if not os.path.isfile(zip_file_destination_path):
        raise FileNotFoundError(zip_file_destination_path)

    execution.shutil_execution.extract(zip_file_destination_path, destination_directory)

    # prefer commit, if commit is not available take branch
    if repository.commit_revision:
        checkout = repository.commit_revision
    else:
        checkout = repository.branch_name
    # do git checkout here


def create_zip_file_path(zip_file):
    repository_directory = configuration.get_publish_output_path()
    zip_file_path = os.path.join(repository_directory, "latest", zip_file)
    if not os.path.isfile(zip_file_path):
        raise FileNotFoundError(
            f"{zip_file_path}: migrate the repository and check paths"
        )
    return zip_file_path


def set_destination_directory(repository):
    if repository.folder_name.startswith("ag-"):
        destination_directory = repository.local_folder_path
    else:
        destination_directory = os.path.join(
            repository.local_folder_path, repository.folder_name
        )

    os.makedirs(destination_directory, exist_ok=True)
    return destination_directory


###################################################################################################################
## newly added functions
def checkout_top_repository(repository):
    repository_name = parser.branchConfigurationParser.parse_repo_name(
        repository.remote_path
    )
    repository_name_no_externals = f"{repository_name}-no-externals"

    local_folder_path = repository.local_folder_path
    folder_name = os.path.basename(local_folder_path)
    base_directory = os.path.dirname(local_folder_path)

    execution.shutil_execution.delete(local_folder_path)

    command = f"git clone git@bitbucket.org:curtisinst/{repository_name_no_externals}.git ./{folder_name}"
    print(command)

    execution.subprocess_execution.check_output_execute(command, base_directory)
    execution.git_execution.add_remote_upload(repository_name, local_folder_path)


# put clone repository and add submodule into one function
def clone_repository(repository, has_dependencies):
    repository_name = parser.branchConfigurationParser.parse_repo_name(
        repository.remote_path
    )
    repository_name_no_externals = f"{repository_name}-no-externals"
    folder_name = repository.folder_name
    local_folder_path = repository.local_folder_path

    if not has_dependencies:
        command = f"git submodule add --force git@bitbucket.org:curtisinst/{repository_name_no_externals}.git ./{folder_name}"
    else:
        command = f"git clone git@bitbucket.org:curtisinst/{repository_name_no_externals}.git ./{folder_name}"

    if folder_name.endswith(".cs"):
        print(f"path is file (no submodule): {folder_name}")
        return

    os.makedirs(local_folder_path, exist_ok=True)

    execution.subprocess_execution.check_output_execute(command, local_folder_path)

    repository_folder = os.path.join(local_folder_path, folder_name)

    print_mode = True
    if not execution.git_execution.check_remote_upload_exists(repository_folder):
        execution.git_execution.add_remote_upload(repository_name, repository_folder)
    if execution.git_execution.check_remote_upload_exists(repository_folder):
        push_repository_as_live = "git push upload --mirror"
        execution.subprocess_execution.check_output_execute(
            push_repository_as_live, repository_folder
        )
    else:
        if print_mode:
            add_missing_remote_to_file(
                f"clone_repository: {repository_name}: {repository_folder}"
            )
            print(f"added missing remote: {repository_name}")
        else:
            raise ValueError(
                f'error: remote origin for repository: "{repository_name}" does not exist'
            )

    branch_name_conversion = create_branch_name_conversion(repository)
    branches = create_branches(branch_name_conversion)
    tags = create_tags(branch_name_conversion)

    external_checker = create_external_checker(repository, branches, tags)
    remote_repository_name = get_remote_repository_name(repository, external_checker)
    has_subfolder = external_checker.has_subfolder()

    branch_name = get_branch_name(
        external_checker, repository.branch_name, branches, tags
    )

    checkout_commit_hash(
        repository.commit_revision,
        remote_repository_name,
        has_subfolder,
        branch_name,
        repository_folder,
    )

    checkout_new_branch_command = (
        f"git checkout -b {branch_name}_{repository.commit_revision}"
    )
    execution.subprocess_execution.check_output_execute(
        checkout_new_branch_command, repository_folder
    )

    # extract upload functionality from git clone functionality, upload needs to be done in every case

    # the safe variant would be to checkout a commit and create a new branch main_r33333
    # if this branch is used with another revision, there wont be any conflicts/rewrite
    # do a git commit --amend so it is clear to which revision it belongs by the text: git-svn-id

    # checkout_commit_hash(
    #     repository.commit_revision,
    #     repository_name,
    #     has_subfolder,
    #     git_branch_name,
    #     repository_path,
    # )
    #     checkout_commit_hash(
    #     repository.commit_revision,
    #     remote_repository_name,
    #     has_subfolder,
    #     branch_name,
    #     repository_path,
    # )
    # git checkout commit hash needs to be done here, so add submodule embedded db and push commit is done on correct commit
    # clone repository needs to do repository no externals in any case and upload it to remote
    # the else self.dependencies can stay empty since in recursive it is checked out by add_submodule


def add_submodule(repository):
    local_folder_path = repository.local_folder_path
    folder_name = repository.folder_name
    # if "EmbeddedDB" in folder_name:
    #     breakpoint()
    repository_path = os.path.join(local_folder_path, folder_name)

    if folder_name.endswith(".cs"):
        print(f"path is file (no submodule): {folder_name}")
        return

    root_git_path = get_root_git_path(local_folder_path)
    subpath = local_folder_path[len(root_git_path) + 1 :]
    print(subpath)

    # breakpoint()
    # git_delete_folder(folder_name, local_folder_path, subpath, root_git_path)
    execution.shutil_execution.delete(os.path.join(local_folder_path, folder_name))
    os.makedirs(local_folder_path, exist_ok=True)

    branch_name_conversion = create_branch_name_conversion(repository)
    branches = create_branches(branch_name_conversion)
    tags = create_tags(branch_name_conversion)

    external_checker = create_external_checker(repository, branches, tags)
    remote_repository_name = get_remote_repository_name(repository, external_checker)
    has_subfolder = external_checker.has_subfolder()

    command = f"git submodule add --force git@bitbucket.org:curtisinst/{remote_repository_name}.git ./{folder_name}"
    print(command)

    execution.subprocess_execution.check_output_execute(command, local_folder_path)

    update_submodules_commands = [
        "git submodule sync --recursive",
        "git submodule update --init --recursive --remote",
    ]
    for each_command in update_submodules_commands:
        execution.subprocess_execution.check_output_execute(
            each_command, local_folder_path
        )

    if remote_repository_name == "ag-pb-generator":
        breakpoint()

    if not execution.git_execution.check_remote_upload_exists(repository_path):
        execution.git_execution.add_remote_upload(
            remote_repository_name, repository_path
        )
    else:
        execution.git_execution.remove_remote_upload(repository_path)
        execution.git_execution.add_remote_upload(
            remote_repository_name, repository_path
        )

    branch_name = get_branch_name(
        external_checker, repository.branch_name, branches, tags
    )

    checkout_commit_hash(
        repository.commit_revision,
        remote_repository_name,
        has_subfolder,
        branch_name,
        repository_path,
    )

    print("submodule was added:")
    print(f"path: {repository_path}")
    print(f"commit_revision: {repository.commit_revision}")
    # print(f"repository_name: {repository_name}")
    print(f"remote_repository_name: {remote_repository_name}")


def create_branch_name_conversion(repository):
    repository_name = parser.branchConfigurationParser.parse_repo_name(
        repository.remote_path
    )
    migration_output_path = configuration.get_migration_output_path()
    migration_repository_path = os.path.join(migration_output_path, repository_name)
    branch_name_conversion = output.branch_name_conversion.BranchNameConversion(
        migration_repository_path
    )
    return branch_name_conversion


def create_branches(branch_name_conversion):
    return branch_name_conversion.create_branches_dictionary()


def create_tags(branch_name_conversion):
    return branch_name_conversion.create_tags_dictionary()


def create_external_checker(repository, branches, tags):
    external_checker = output.external_checker.ExternalChecker(
        repository.branch_name, branches.keys(), tags.keys(), repository.remote_path
    )

    return external_checker


def get_remote_repository_name(repository, external_checker):
    repository_name = parser.branchConfigurationParser.parse_repo_name(
        repository.remote_path
    )

    has_subfolder = external_checker.has_subfolder()
    if has_subfolder:
        subfolder = external_checker.get_subfolder()
        remote_repository_name = (
            parser.branchConfigurationParser.parse_subfolder_repo_name(
                repository_name, subfolder
            )
        )
    else:
        remote_repository_name = repository_name

    return remote_repository_name


def get_branch_name(external_checker, branch_name, branches, tags):
    if not external_checker.has_subfolder():
        return branch_name

    svn_extracted_branch_name = external_checker.get_extracted_branch_name()
    git_extracted_branch_name = branches.get(svn_extracted_branch_name)
    is_tag = False
    if git_extracted_branch_name is None:
        is_tag = True
        try:
            git_extracted_branch_name = tags[svn_extracted_branch_name]
        except:
            breakpoint()
    return git_extracted_branch_name


def checkout_commit_hash(
    commit_revision_or_hash,
    repository_name,
    has_subfolder,
    git_branch_name,
    repository_path,
):
    commit_hash = find_commit_hash_by(
        commit_revision_or_hash,
        repository_name,
        has_subfolder,
        git_branch_name,
    )

    if (
        commit_hash == "79e32336ba35101437795faabb9d7a6cd6b20a9c"
    ):  # embeddeddb wrong commit hash
        breakpoint()

    if commit_hash == "6da77de7136ba0fb5688a81c43afef64a0e0e852":
        breakpoint()

    checkout_command = f"git checkout {commit_hash}"
    print(f"{checkout_command} at: {repository_path}")
    execution.subprocess_execution.check_output_execute(
        checkout_command, repository_path
    )


def find_commit_hash_by(
    commit_revision_or_hash,
    repository_name,
    has_subfolder,
    git_branch_name,
):
    transformation_path = configuration.get_transformation_output_path()
    working_directory = os.path.join(transformation_path, repository_name)

    if "r" in commit_revision_or_hash and has_subfolder:
        commit_hash = get_matching_commit_hash_from_live_git_repository_by(
            commit_revision_or_hash, git_branch_name, working_directory
        )
        if commit_hash is None:
            raise ValueError(
                f"error: could not find commit hash for revision: {commit_revision_or_hash}"
            )
        return commit_hash

    if "r" in commit_revision_or_hash and not has_subfolder:
        commit_revision = commit_revision_or_hash
        find_commit_hash_command = f"git svn find-rev {commit_revision}"
        migration_output_path = configuration.get_migration_output_path()
        migration_repository_path = os.path.join(migration_output_path, repository_name)
        return execution.subprocess_execution.check_output_execute(
            find_commit_hash_command, migration_repository_path
        )

    return commit_revision_or_hash


def get_matching_commit_hash_from_live_git_repository_by(
    commit_revision, git_branch_name, working_directory
):
    commit_revision = commit_revision.replace("r", "")
    pattern = f"git-svn-id:.+@{commit_revision}"

    commits = execution.subprocess_execution.check_output_execute(
        ["git", "rev-list", git_branch_name], working_directory
    ).splitlines()
    for commit in commits:
        commit_message = subprocess.check_output(
            ["git", "log", "-1", "--format=%B", commit], cwd=working_directory
        )

        try:
            commit_message = commit_message.decode("utf-8")
        except:
            breakpoint()
            return

        if re.search(pattern, commit_message):
            print(f"Matching commit hash: {commit}")
            return commit
    breakpoint()


def create_and_push_commit(repository, working_directory):
    print("push repository:")
    print(repository)
    repository_name = parser.branchConfigurationParser.parse_repo_name(
        repository.remote_path
    )

    add_command = "git add -A"
    execution.subprocess_execution.check_output_execute(add_command, working_directory)

    commit_command = ["git", "commit", "--amend", "--no-edit"]
    execution.subprocess_execution.check_output_execute(
        commit_command, working_directory
    )

    print_mode = True

    # execution.git_execution.add_remote_upload(repository_name, working_directory)
    if execution.git_execution.check_remote_upload_exists(working_directory):
        push_command = "git push upload --mirror"
        print(f"create_and_push_commit: {push_command}")
        execution.subprocess_execution.check_output_execute(
            push_command, working_directory
        )
    else:
        if print_mode:
            add_missing_remote_to_file(
                f"create_and_push_commit: {repository_name}: {working_directory}"
            )
            print(f"added missing remote: {repository_name}")
        else:
            raise ValueError(
                f'error: remote origin for repository: "{repository_name}" does not exist'
            )

    find_created_commit_hash_command = "git rev-parse HEAD"

    created_commit_hash = execution.subprocess_execution.check_output_execute(
        find_created_commit_hash_command, working_directory
    )

    created_commit_hash = created_commit_hash.strip().replace("\n", "")
    repository.commit_revision = created_commit_hash
    print(f"push and commit: new commit hash: {created_commit_hash}")
    breakpoint()

    # find new commit is only needed, cause new commit is made, better: do git commit --amend to reserve history:
    # git upload without force push will not work anymore


def add_missing_remote_to_file(name):
    file_path = "remotes.txt"

    with open(file_path, "a") as file:
        file.write(f"{name}\n")


def get_root_git_path(local_folder_path):
    local_path = configuration.get_local_path()
    remove_folder = local_folder_path
    root_git_path = local_folder_path

    while remove_folder != local_path:
        root_git_path = remove_folder
        remove_folder = os.path.dirname(remove_folder)

    print(f"root git path: {root_git_path}")
    return root_git_path


def git_delete_folder(folder, path, relative_path, root_git_path):
    if os.path.exists(os.path.join(path, folder)):
        command = f"git rm {folder} -rf"
        execution.subprocess_execution.check_output_execute(command, path)
        execution.shutil_execution.delete(
            os.path.join(root_git_path, f".git/modules/{relative_path}/{folder}")
        )
