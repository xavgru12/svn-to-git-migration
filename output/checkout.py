import os
import sys
import data.configuration as configuration

import subprocess


def checkout_svn_externals(data_dictionary):
    for _, data in data_dictionary.items():
        checkout_each_external(data)


def checkout_each_external(dataclass_object):
    # svn checkout -r 285541 \
    # http://ag-reposerver/repo/Projects/enAbleX1/SW/SharedComponents/emWin/tags/v5.22_F427_E emWin
    os.makedirs(dataclass_object.local_folder_path, exist_ok=True)
    print(f"Started svn external checkout: {dataclass_object.name}")
    if dataclass_object.commit_revision is not None:
        revision = f"-r {dataclass_object.commit_revision}"
    else:
        revision = ""

    process_string = f"svn checkout {revision} {configuration.base_server_url}/{dataclass_object.remote_path}{dataclass_object.branch_name} {dataclass_object.name}".split()

    output = subprocess.check_output(
        process_string, cwd=f"{dataclass_object.local_folder_path}"
    ).decode(sys.stdout.encoding)
    print(output)
