import os
import sys
import data.configuration as configuration
import subprocess


def checkout_svn_externals(recursive_list):
    if not os.path.isdir(f"{recursive_list.current.local_folder_path}/.git"):
        raise Exception(
            f"--local-path is not a git repository: {recursive_list.current.local_folder_path}"
        )
    for dependency in recursive_list.dependencies:
        checkout_each_external(dependency.current)


def checkout_each_external(repository):
    """
    svn checkout -r 285541 \
    http://ag-reposerver/repo/Projects/enAbleX1/SW/SharedComponents/emWin/tags/v5.22_F427_E emWin
    """
    os.makedirs(repository.local_folder_path, exist_ok=True)
    print(f"Started svn external checkout: {repository.folder_name}")

    if repository.commit_revision is not None:
        commit_revision = repository.commit_revision.replace("r", "")
        commit_revision_string = f"-r {commit_revision}"
    else:
        commit_revision_string = ""

    checkout_command = f"svn checkout {commit_revision_string} {configuration.get_base_server_url()}/{repository.remote_path}/{repository.branch_name} {repository.folder_name}"
    switch_command = f"svn switch {configuration.get_base_server_url()}/{repository.remote_path}/{repository.branch_name} {repository.folder_name}"
    update_command = f"svn update {commit_revision_string} {repository.folder_name}"
    print(f"{repository.local_folder_path}: {checkout_command}")

    try:
        output = subprocess.check_output(
            checkout_command.split(), cwd=f"{repository.local_folder_path}"
        ).decode(sys.stdout.encoding)
    except subprocess.CalledProcessError:
        print(switch_command)
        output = subprocess.check_output(
            switch_command.split(), cwd=f"{repository.local_folder_path}"
        ).decode(sys.stdout.encoding)

        print(update_command)
        output = subprocess.check_output(
            update_command.split(), cwd=f"{repository.local_folder_path}"
        ).decode(sys.stdout.encoding)

    print(output)
