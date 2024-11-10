import os
import parser.branchConfigurationParser
import data.configuration as configuration
import shutil
import output.external_checker
import execution.shutil_execution
import execution.subprocess_execution
import execution.git_execution


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
    repository_name = parser.branchConfigurationParser.parse_repo_name(repository.remote_path)
    repository_name_no_externals = f"{repository_name}-no-externals"

    local_folder_path = repository.local_folder_path
    folder_name = os.path.basename(local_folder_path)
    base_directory = os.path.dirname(local_folder_path)

    execution.shutil_execution.delete(local_folder_path)

    command = f"git clone git@bitbucket.org:curtisinst/{repository_name_no_externals}.git ./{folder_name}"
    print(command)

    execution.subprocess_execution.check_output_execute(
            command, base_directory
        )
    execution.git_execution.add_remote_upload(repository_name, local_folder_path)


def clone_repository(repository):
    repository_name = parser.branchConfigurationParser.parse_repo_name(repository.remote_path)
    repository_name_no_externals = f"{repository_name}-no-externals"
    folder_name = repository.folder_name
    local_folder_path = repository.local_folder_path

    clone_command = f"git submodule add --force git@bitbucket.org:curtisinst/{repository_name_no_externals}.git ./{folder_name}"

    if folder_name.endswith(".cs"):
        print(f"path is file (no submodule): {folder_name}")
        return

    os.makedirs(local_folder_path, exist_ok=True)

    execution.subprocess_execution.check_output_execute(
            clone_command, local_folder_path
        )
    
    repository_folder = os.path.join(local_folder_path, folder_name)

    print_mode = True

    execution.git_execution.add_remote_upload(repository_name, repository_folder)
    if execution.git_execution.check_remote_upload_exists(repository_folder):
        push_repository_as_live = "git push upload --mirror"
        execution.subprocess_execution.check_output_execute(
                push_repository_as_live, repository_folder
            )
    else:
        if print_mode:
            add_missing_remote_to_file(repository_name)
            print(f"added missing remote: {repository_name}")
        else:
            raise ValueError(
                f'error: remote origin for repository: "{repository_name}" does not exist'
            )
        

def add_submodule(repository):
    repository_name = parser.branchConfigurationParser.parse_repo_name(repository.remote_path)

    local_folder_path = repository.local_folder_path
    folder_name = repository.folder_name

    if folder_name.endswith(".cs"):
        print(f"path is file (no submodule): {folder_name}")
        return

    root_git_path = get_root_git_path(local_folder_path)
    subpath = local_folder_path[len(root_git_path) + 1:]
    print(subpath)

    git_delete_folder(folder_name, local_folder_path, subpath, root_git_path)
    execution.shutil_execution.delete(os.path.join(local_folder_path, folder_name))
    os.makedirs(local_folder_path, exist_ok=True)

    command = f"git submodule add --force git@bitbucket.org:curtisinst/{repository_name}.git ./{folder_name}"
    print(command)

    execution.subprocess_execution.check_output_execute(
            command, local_folder_path
        )


def create_and_push_commit(repository, working_directory):
    print("push repository:")
    print(repository)
    repository_name = parser.branchConfigurationParser.parse_repo_name(repository.remote_path)

    add_command = "git add -A"
    execution.subprocess_execution.check_output_execute(
            add_command, working_directory
        )

    commit_command = ["git", "commit", "-m", "activate git submodules"]
    execution.subprocess_execution.check_output_execute(
            commit_command, working_directory
        )
    
    print_mode = True

    if execution.git_execution.check_remote_upload_exists(working_directory):
        push_command = "git push upload main --force"
        execution.subprocess_execution.check_output_execute(
                push_command, working_directory
            )
    else:
        if print_mode:
            add_missing_remote_to_file(repository_name)
            print(f"added missing remote: {repository_name}")
        else:
            raise ValueError(
                f'error: remote origin for repository: "{repository_name}" does not exist'
            )


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
        execution.subprocess_execution.check_output_execute(
                command, path
            )
        execution.shutil_execution.delete(os.path.join(root_git_path, f".git/modules/{relative_path}/{folder}"))
