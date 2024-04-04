import subprocess
import sys
from parser.lineParser import LineParser
from model.svnRepositoryModel import SvnRepositoryModel
import data.configuration as configuration


def parse(remote_url):
    external_information = get_external_info_from_server(
        remote_url + "/" + configuration.get_branch_path()
    )

    data_dict = parse_external_info(external_information)
    return data_dict


def get_external_info_from_server(branch_url):
    first_part_command = "svn propget svn:externals"
    print(f"{first_part_command} {branch_url} -R")
    command_list = []
    command_list.extend(first_part_command.split())
    command_list.append(branch_url)
    command_list.append("-R")
    return subprocess.check_output(command_list).decode(sys.stdout.encoding)


def parse_external_info(data):
    external_repo_dictionary = dict()
    base_folder = ""
    for line in data.splitlines():
        if line.strip():
            line_parser = LineParser(line)
            base_folder = line_parser.parse_base_folder_name(
                configuration.get_remote_url() + "/" + configuration.get_branch_path(),
                base_folder,
            )
            local_folder_path = configuration.get_local_git_path() + base_folder if configuration.get_local_git_path() else ""
            remote_path = line_parser.parse_remote_path()
            commit_revision = line_parser.parse_commit_revision()
            name = line_parser.parse_name()
            branch_name = line_parser.parse_branch()
            data_object = SvnRepositoryModel(
                name,
                base_folder,
                local_folder_path,
                remote_path,
                branch_name,
                commit_revision,
            )
            external_repo_dictionary[f"{base_folder}/{name}"] = data_object

    return external_repo_dictionary
