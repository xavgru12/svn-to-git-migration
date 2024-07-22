import data.configuration as configuration
import os
import subprocess
import multiprocessing
import shutil
import sys
import output.branchConfiguration
import datetime
import output.printRepositoryData
import output.subprocess_execution
import parser.branchConfigurationParser
import model.svnRepositoryModel


def migrate_svn_externals_to_git(remote_paths, logger):
    print("check and write svn branch paths according to configuration ... ")
    branch_dict = dict()

    for remote_path in remote_paths:
        output.branchConfiguration.set_repo_configuration_from(remote_path, branch_dict)

    print("branch_dict:")
    print(200 * "-")
    output.printRepositoryData.print_info(branch_dict, logger)
    print(200 * "-")
    print()
    print("... done")

    migrate(branch_dict.values())


def migrate_econ_folder():
    repository_paths = get_econ_repository_paths()
    print("econ folder repository paths:")
    print(repository_paths)
    trees = create_econ_repository_trees(repository_paths)
    for tree in trees:
        tree.parse_recursively()
        # print(f"tree: {tree.recursive_list.current.folder_name}")

    for tree in trees:
        print(f"tree: {tree.recursive_list.current.folder_name}")
        tree.print_tree()

    print("migrate repositories recursively")
    for tree in trees:
        tree.migrate_repositories_recursively()

    # this will be a new function: checkout_econ_folder
    # print("checkout git repositories recursively...")
    # for tree in trees:
    #     tree.checkout_git_repositories_recursively()


def create_econ_repository_trees(repository_paths):
    repository_trees = []

    for path in repository_paths:
        tree = create_tree(path)
        repository_trees.append(tree)

    return repository_trees


def create_tree(path):
    remote_path = path

    name = parser.branchConfigurationParser.parse_repo_name(remote_path)

    local_path = configuration.get_local_path()
    local_path = os.path.join(local_path, name)
    print(f"local_path: {local_path}")

    branch_name = get_trunk_branch_name(remote_path)

    top = model.svnRepositoryModel.SvnRepositoryModel(
        name, "", local_path, remote_path, branch_name, ""
    )
    # branch_name retrieved from branch_dict

    tree = output.repositoryTree.RepositoryTree(top)
    return tree


def get_trunk_branch_name(remote_path):
    branch_configuration = parser.branchConfigurationParser.parse()

    trunk_names = branch_configuration["generic"]["trunk"]["folders"]

    found_trunk = []
    for name in trunk_names:
        inside_path = False
        if remote_path.endswith(name):
            branch = remote_path
            inside_path = True
        else:
            branch = f"/{remote_path}/{name}"

        branch_url = f"{configuration.get_base_server_url()}/{branch}"
        if output.branchConfiguration.check_for_existence(branch_url) is True:
            if inside_path:
                found_trunk.append("")
            else:
                found_trunk.append(name)

    if len(found_trunk) > 1:
        raise Exception(
            f"found several possible branch names for trunk in top repository of repository tree: {found_trunk}"
        )

    if not found_trunk:
        raise Exception(
            f"no trunk found for top repository of repository tree: {remote_path}"
        )

    return found_trunk[0]


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
    file = f"logs/migration/{repo_name}.txt"
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
        for log in output.subprocess_execution.continuous_execute(command, local_repo_path, "stderr"):
            print(f"{repo_name}: {append_log}: {log}")
            f.write(f"{append_log}: {log}")
            f.flush()
