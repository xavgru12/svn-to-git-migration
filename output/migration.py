import data.configuration as configuration
import os
import subprocess
import multiprocessing
import shutil
import sys
import output.branchConfiguration
import datetime
import output.printRepositoryData
import output.branchConfiguration
import output.subprocess_execution
import subprocess_execution


def migrate_svn_externals_to_git(data_dict):
    print("check and write svn branch paths according to configuration ... ")
    branch_dict = dict()
    for repository in data_dict.values():
        output.branchConfiguration.set_repo_configuration_from(
            repository.remote_path, branch_dict
        )
    print("branch_dict:")
    print(200 * "-")
    output.printRepositoryData.print_info(branch_dict)
    print("data_dict:")
    print(200 * "-")
    output.printRepositoryData.print_info(data_dict)
    print()
    print("... done")

    if confirm(
        "This process takes one day to finish. Preferably copy and paste the already migrated repositories. "
        "Do you still want to continue?"
    ):
        migrate(branch_dict.values())


def migrate_econ_folder():
    repository_paths = get_econ_repository_paths()
    print("econ folder repository paths:")
    print(repository_paths)
    branch_dict = dict()
    for path in repository_paths:
        output.branchConfiguration.set_repo_configuration_from(path, branch_dict)
    print("branch dict")
    for repo in branch_dict.values():
        print(repo)

    if confirm(
        "This process takes one day to finish. Preferably copy and paste the already migrated repositories. "
        "Do you still want to continue?"
    ):
        migrate(branch_dict.values())


def get_econ_repository_paths():
    repositories = []
    paths = [
        "http://ag-reposerver/repo/Projects/ECON/SW",
        "http://ag-reposerver/repo/Projects/ECON/SW/Tools",
        "http://ag-reposerver/repo/Projects/ECON/SW/Common",
        "http://ag-reposerver/repo/Projects/ECON/SW/Remote_Diagnostics",
    ]

    for path in paths:
        repos = get_repositories_from(path)
        repositories.extend(repos)

    return repositories


def get_repositories_from(path):
    repositories = []

    command = f"svn list {path}"

    data = subprocess.check_output(command.split()).decode(sys.stdout.encoding)

    repositories = get_list_from(data)

    add_path(repositories, path)

    return repositories


def get_list_from(data):
    exclude_list = [
        "obsolete/",
        "Webupdate/",
        "Tools/",
        "Common/",
        "Remote_Diagnostics/",
    ]
    repositories = []
    for line in data.splitlines():
        if line not in exclude_list and "/" in line:
            name = line.removesuffix("/")
            repositories.append(f"{name}")

    return repositories


def add_path(repositories, path):
    for index, repository in enumerate(repositories):
        repositories[index] = f"{path}/{repository}".replace(
            f"{configuration.get_base_server_url()}/", ""
        )


def confirm(prompt):
    """Prompts for yes or no response from the user. Returns True for yes and
    False for no.

    """
    while True:
        ans = input(prompt + " [y/n]: ")
        if ans.lower() == "y":
            return True
        elif ans.lower() == "n":
            return False
        else:
            print("Please enter y or n.")


def migrate(repositories):
    for repository in repositories:
        init_each(repository)

    with multiprocessing.Pool() as pool:
        for result in pool.imap(migrate_each, repositories):
            if isinstance(result, Exception):
                print("Got exception: {}".format(result))
        pool.close()
        pool.join()


def init_each(repository):
    external_source_path = (
        f"{configuration.get_migration_output_path()}/{repository.repo_name}"
    )

    if not os.path.exists(external_source_path):
        os.makedirs(external_source_path)
        init_command = f"git svn init {configuration.get_base_server_url()}"
        execute_with_log(init_command, repository.repo_name, external_source_path)
        set_repository_configuration(repository, external_source_path)


def migrate_each(repository):
    print(f"Started git migration for: {repository.repo_name}")

    external_source_path = (
        f"{configuration.get_migration_output_path()}/{repository.repo_name}"
    )

    # remove NORImageCreator since it triggers http://ag-reposerver/repo/Projects/enAbleX1/SW/HC-Q,
    # who needs NORImageCreator anyways?
    # modify remotepath to Projects/enAbleX1/SW/HC-Q/trunk/Tools/NORImageCreator in order to prevent to migrate hc-q
    if "NORImageCreator" != repository.repo_name:
        fetch_command = "git svn fetch --quiet --quiet"
        execute_with_log(fetch_command, repository.repo_name, external_source_path)

    print(f"Ended git migration for: {repository.repo_name}")


def set_repository_configuration(data, external_source_path):
    git_config_file = f"{external_source_path}/.git/config"
    shutil.copy("./data/gitRepositoryConfiguration/config.template", git_config_file)

    with open(git_config_file, "a") as f:
        for branch in data.branches:
            f.write(f"	{branch}\n")

        if data.ignore_refs:
            ignore_string = "	ignore-refs = "
            separator = "|"
            for i, ignore in enumerate(data.ignore_refs):
                if i == (len(data.ignore_refs) - 1):
                    separator = ""

                ignore_string = ignore_string + ignore + separator

            f.write(ignore_string + "\n")

        path = os.getcwd()
        new_path = path.replace(os.sep, "/")
        f.write(f"[svn]\n	authorsfile = {new_path}/data/svn-authors.txt")


def execute_with_log(command, repo_name, local_repo_path):
    file = f"logs/{repo_name}.txt"
    time = "{date:%d-%m-%Y_%H-%M-%S}".format(date=datetime.datetime.now())
    append_log = ""
    if "fetch" in command:
        append_log = "fetch"
    if "init" in command:
        append_log = "init"
        history_path = os.path.join(os.path.dirname(file), "history")
        history_file = os.path.join(history_path, f"{repo_name}-{time}.txt")
        os.makedirs(history_path, exist_ok=True)
        if os.path.isfile(file):
            shutil.move(file, history_file)

    os.makedirs(os.path.dirname(file), exist_ok=True)
    with open(file, "a+") as f:
        f.write(
            f'new run of "{append_log}" in "{local_repo_path}": {time} '
            + "-" * 70
            + "\n"
        )
        for log in output.subprocess_execution.continuous_execute(command, local_repo_path):
            print(f"{repo_name}: {append_log}: {log}")
            f.write(f"{append_log}: {log}")
            f.flush()
