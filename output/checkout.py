import os
import sys
import data.configuration as configuration
import subprocess


def checkout_svn_externals(data_dictionary):
    for _, data in data_dictionary.items():
        checkout_each_external(data)


def checkout_each_external(repository):
    """
    svn checkout -r 285541 \
    http://ag-reposerver/repo/Projects/enAbleX1/SW/SharedComponents/emWin/tags/v5.22_F427_E emWin
    """
    os.makedirs(repository.local_folder_path, exist_ok=True)
    print(f"Started svn external checkout: {repository.name}")
    if repository.commit_revision is not None:
        revision = f"-r {repository.commit_revision}"
    else:
        revision = ""

    command = f"svn checkout {revision} {configuration.get_base_server_url()}/{repository.remote_path}{repository.branch_name} {repository.name}"
    print(f"{repository.local_folder_path}: {command}")
    output = subprocess.check_output(
        command.split(), cwd=f"{repository.local_folder_path}"
    ).decode(sys.stdout.encoding)
    print(output)
