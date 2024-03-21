import data.configuration as configuration
import os
import subprocess
import multiprocessing
import shutil
import output.branchConfiguration
import datetime
import output.printRepositoryData


def migrate_svn_externals_to_git(data_dict):
    repositories = filter_double(data_dict.values())
    add_git_remote_branches_configuration(data_dict, repositories)
    output.printRepositoryData.print_info(data_dict)
    if confirm(
        "This process takes one day to finish. Preferably copy and paste the already migrated repositories."
        " Do you still want to continue?"
    ):
        migrate(repositories)


def filter_double(repositories):
    repository_dict = dict()
    for repository in repositories:
        if repository.repo_name not in repository_dict:
            repository_dict[repository.repo_name] = repository

    return repository_dict.values()


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


def add_git_remote_branches_configuration(data_dict, repositories):
    print(f"check and write svn branch paths according to configuration ... ")
    for data in repositories:
        print(data.repo_name)
        data.branches = []
        data.ignore_refs = []
        output.branchConfiguration.add(data)
    for data_dict in data_dict.values():
        for repository in repositories:
            if repository.repo_name == data_dict.repo_name:
                data_dict.branches = repository.branches
                data_dict.ignore_refs = repository.ignore_refs

    print()
    print("... done")


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
    if "NORImageCreator" != repository.name:
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
        for log in execute(command, local_repo_path):
            print(f"{repo_name}: {append_log}: {log}")
            f.write(f"{append_log}: {log}")
            f.flush()


def execute(command, external_source_path):
    popen = subprocess.Popen(
        command.split(),
        stderr=subprocess.PIPE,
        cwd=external_source_path,
        creationflags=subprocess.REALTIME_PRIORITY_CLASS,
        universal_newlines=True,
    )
    for stderr_line in iter(popen.stderr.readline, ""):
        if stderr_line.strip() and stderr_line is not None:
            yield stderr_line
    popen.stderr.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(
            return_code,
            f"{command} at {external_source_path} failed. Stop migration for this repository",
        )
