import os
import subprocess
import multiprocessing
import sys
import shutil
import data.configuration as configuration


def migrate_svn_externals_to_git(data_dict):
    # add_git_remote_branches_configuration(data_dict)
    migrate_externals(data_dict)


def add_git_remote_branches_configuration(data_dict):
    for _, data in data_dict.items():
        data.branches = []
        add_mandatory_branches(data)
        add_optional_branches(data)


def migrate_externals(data_dict):
    with multiprocessing.Pool() as pool:
        for result in pool.imap(migrate_each_external, data_dict.values()):
            if isinstance(result, Exception):
                print("Got exception: {}".format(result))
        pool.close()
        pool.join()


def add_mandatory_branches(data_object):
    all_branches = []
    trunk_branch = f"fetch = {data_object.remote_path}/trunk:refs/remotes/origin/trunk"
    all_branches.append(trunk_branch)
    release_branch = add_release_branch(data_object)
    all_branches.extend(release_branch)
    data_object.branches.extend(all_branches)


def add_release_branch(data):
    output_branches = []
    split_branch_name = data.branch_name.split("/")
    last_part = split_branch_name[-1]
    parts_except_last = split_branch_name[:-1]
    optional_name_parts = "/".join(parts_except_last)

    complete_line_string = (
        f"branches = {data.remote_path}{optional_name_parts}/{{{last_part}}}"
        f":refs/remotes/origin/releaseBranch{optional_name_parts}/*"
    )
    output_branches.append(complete_line_string)
    return output_branches


def add_optional_branches(data_object):
    branches = f"branches = {data_object.remote_path}/branches/*:refs/remotes/origin/branches/*"
    tags = f"tags = {data_object.remote_path}/tags/*:refs/remotes/origin/tags/*"
    data_object.branches.extend([branches, tags])


def migrate_each_external(data):
    print(f"Started git migration for: {data.name}")

    external_source_path = (
        f"{configuration.local_path}/SharedComponentsSources/{data.name}"
    )
    if not os.path.exists(external_source_path):
        os.makedirs(external_source_path)
    subprocess.check_output(
        ["git", "svn", "init", configuration.base_server_url], cwd=external_source_path
    ).decode(sys.stdout.encoding)
    set_repository_configuration(data, external_source_path)
    # remove NORImageCreator since it triggers http://ag-reposerver/repo/Projects/enAbleX1/SW/HC-Q,
    # who needs NORImageCreator anyways?
    if "NORImageCreator" != data.name:
        subprocess.check_output(
            ["git", "svn", "fetch", "--quiet", "--quiet"],
            cwd=external_source_path,
            creationflags=subprocess.REALTIME_PRIORITY_CLASS,
        ).decode(sys.stdout.encoding)

    print(f"Ended git migration for: {data.name}")


def set_repository_configuration(data, external_source_path):
    git_config_file = f"{external_source_path}/.git/config"
    shutil.copy("./data/gitRepositoryConfiguration/config.template", git_config_file)

    with open(git_config_file, "a") as f:
        for branch in data.branches:
            f.write(f"	{branch}\n")
        path = os.getcwd()
        new_path = path.replace(os.sep, "/")
        f.write(f"[svn]\n	authorsfile = {new_path}/data/svn-authors.txt")
