import os
import subprocess

import parser.branchConfigurationParser
import data.configuration as configuration
import output.external_checker
import execution.shutil_execution
import execution.subprocess_execution
import execution.git_execution
import output.branch_name_conversion


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

    branch_name_conversion = create_branch_name_conversion(repository)
    branches = create_branches(branch_name_conversion)
    tags = create_tags(branch_name_conversion)

    external_checker = create_external_checker(repository, branches, tags)
    remote_repository_name = get_remote_repository_name(repository, external_checker)
    has_subfolder = external_checker.has_subfolder()

    folder_name = repository.folder_name
    local_folder_path = repository.local_folder_path

    if not has_dependencies:
        command = f"git submodule add --force git@bitbucket.org:curtisinst/{remote_repository_name}.git ./{folder_name}"
    else:
        command = f"git clone git@bitbucket.org:curtisinst/{remote_repository_name}.git ./{folder_name}"
        print(command)

    if folder_name.endswith(".cs"):
        print(f"path is file (no submodule): {folder_name}")
        return

    os.makedirs(local_folder_path, exist_ok=True)

    execution.subprocess_execution.check_output_execute(command, local_folder_path)

    repository_folder = os.path.join(local_folder_path, folder_name)

    print_mode = True

    if not execution.git_execution.check_remote_upload_exists(repository_folder):
        execution.git_execution.add_remote_upload(
            remote_repository_name, repository_folder
        )
    if execution.git_execution.check_remote_upload_exists(repository_folder):
        if not has_subfolder:
            pull_command = "git pull upload HEAD"
            execution.subprocess_execution.check_output_execute(
                pull_command, repository_folder
            )
            try:
                push_repository_as_live = "git push upload --tags"
                execution.subprocess_execution.check_output_execute(
                    push_repository_as_live, repository_folder
                )
            except ValueError:
                pass  # already exist
            push_repository_as_live = "git push upload --all"
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

    branch_name, is_tag = get_branch_name(external_checker, branches, tags)

    checkout_commit_hash(
        repository.commit_revision,
        branch_name,
        repository_folder,
        is_tag,
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
    #     git_branch_name,
    #     repository_path,
    #     is_tag,
    # )
    #     checkout_commit_hash(
    #     repository.commit_revision,
    #     branch_name,
    #     repository_path,
    #     is_tag,
    # )
    # git checkout commit hash needs to be done here, so add submodule embedded db and push commit is done on correct commit
    # clone repository needs to do repository no externals in any case and upload it to remote
    # the else self.dependencies can stay empty since in recursive it is checked out by add_submodule


def checkout_single_file_from_svn(repository):
    base_server_url = configuration.get_base_server_url()
    remote_path = repository.remote_path.replace(" (obsolete)", "")

    if repository.commit_revision:
        commit_revision = repository.commit_revision.replace("r", "")
        commit_revision_string = f"@{commit_revision}"
    else:
        commit_revision_string = ""

    command = [
        "svn",
        "export",
        f"{base_server_url}/{remote_path}/{repository.branch_name}{commit_revision_string}",
        ".",
    ]

    print(f"{command} at: {repository.local_folder_path}")

    execution.subprocess_execution.check_output_execute(
        command, repository.local_folder_path
    )


def add_submodule(repository):
    local_folder_path = repository.local_folder_path
    folder_name = repository.folder_name

    repository_path = os.path.join(local_folder_path, folder_name)

    if folder_name.endswith(".cs"):
        print(f"path is file (no submodule): {folder_name}")
        checkout_single_file_from_svn(repository)
        return

    root_git_path = get_root_git_path(local_folder_path)
    subpath = local_folder_path[len(root_git_path) + 1 :]
    print(subpath)

    execution.shutil_execution.delete(os.path.join(local_folder_path, folder_name))
    os.makedirs(local_folder_path, exist_ok=True)

    branch_name_conversion = create_branch_name_conversion(repository)
    branches = create_branches(branch_name_conversion)
    tags = create_tags(branch_name_conversion)

    external_checker = create_external_checker(repository, branches, tags)
    remote_repository_name = get_remote_repository_name(repository, external_checker)

    command = f"git submodule add --force git@bitbucket.org:curtisinst/{remote_repository_name}.git ./{folder_name}"
    print(command)

    execution.subprocess_execution.check_output_execute(command, local_folder_path)

    branch_name, is_tag = get_branch_name(external_checker, branches, tags)

    checkout_commit_hash(
        repository.commit_revision,
        branch_name,
        repository_path,
        is_tag,
    )

    print("submodule was added:")
    print(f"path: {repository_path}")
    print(f"commit_revision: {repository.commit_revision}")
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


def get_branch_name(external_checker, branches, tags):
    svn_extracted_branch_name = external_checker.get_extracted_branch_name()
    git_extracted_branch_name = branches.get(svn_extracted_branch_name)
    is_tag = False
    if git_extracted_branch_name is None:
        is_tag = True
        try:
            git_extracted_branch_name = tags[svn_extracted_branch_name]
        except:
            breakpoint()
            git_extracted_branch_name = "main"
            is_tag = False
    return git_extracted_branch_name, is_tag


def checkout_commit_hash(
    commit_revision_or_hash,
    git_branch_name,
    repository_path,
    is_tag,
):
    if is_tag:
        checkout_command = f"git checkout {git_branch_name}"
    else:
        commit_hash = find_commit_hash_by(
            commit_revision_or_hash,
            repository_path,
            git_branch_name,
        )
        checkout_command = f"git checkout {commit_hash}"

    print(f"{checkout_command} at: {repository_path}")
    execution.subprocess_execution.check_output_execute(
        checkout_command, repository_path
    )


def find_commit_hash_by(commit_revision_or_hash, repository_path, git_branch_name):
    if "r" not in commit_revision_or_hash:
        return commit_revision_or_hash

    commit_hash = get_matching_commit_hash_from_live_git_repository_by(
        commit_revision_or_hash, git_branch_name, repository_path
    )
    if commit_hash is None:
        raise ValueError(
            f"error: could not find commit hash for revision: {commit_revision_or_hash}"
        )
    return commit_hash


def get_matching_commit_hash_from_live_git_repository_by(
    commit_revision, git_branch_name, working_directory
):
    if git_branch_name == "gitDistrDummy":
        commit_revision = "r578257"
        # git log --all --grep="578257"
    if not commit_revision:
        return ""
    commit_revision = commit_revision.replace("r", "")
    pattern = f"git-svn-id:.*@{commit_revision}"
    print(f"pattern: {pattern}")
    commit = subprocess.check_output(
        ["git", "log", "--all", f"--grep={pattern}", "-n1", "--format=%H"],
        cwd=working_directory,
    )
    commit = commit.decode("utf-8")
    commit = commit.strip()
    if commit == "":
        breakpoint()
    else:
        print(f"successfully found commit hash: {commit}")

    return commit


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

    if execution.git_execution.check_remote_upload_exists(working_directory):
        push_command = "git push --force upload HEAD"
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
