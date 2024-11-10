import os
import parser.branchConfigurationParser
import data.configuration as configuration
import shutil
import output.external_checker
import execution.shutil_execution


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
