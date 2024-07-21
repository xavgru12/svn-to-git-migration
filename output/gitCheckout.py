import os
import parser.branchConfigurationParser
import data.configuration as configuration
import shutil


def checkout(repository):
    """
    git checkout <commit_revision or origin/branch>
    """

    destination_directory = set_destination_directory(repository)

    repo_name = parser.branchConfigurationParser.parse_repo_name(repository.remote_path)
    print(f"repo_name: {repo_name}")

    zip_file = f"{repo_name}.zip"
    zip_file_path = create_zip_file_path(zip_file)
    print(f"zip_file_path: {zip_file_path}")
    print(f"destination_directory: {destination_directory}")

    shutil.copy(zip_file_path, destination_directory)

    local_zip = os.path.join(destination_directory, zip_file)
    if not os.path.isfile(local_zip):
        raise FileNotFoundError(local_zip)

    extract(local_zip, destination_directory)

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


def extract(zip_file, destination):
    shutil.unpack_archive(zip_file, destination)
    os.remove(zip_file)
