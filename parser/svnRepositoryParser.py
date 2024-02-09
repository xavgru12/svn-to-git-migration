import subprocess
import sys
from parser.lineParser import *
from model.svnRepositoryModel import *
import data.configuration as configuration


def parse(remote_url):
    external_information = get_external_info_from_server(remote_url + "/trunk")

    data_dict = parse_external_info(external_information)
    return data_dict


def get_external_info_from_server(branch_url):
    return subprocess.check_output(["svn", "propget", "svn:externals", branch_url, "-R"]).decode(sys.stdout.encoding)


def parse_external_info(data):
    external_repo_dictionary = dict()
    base_folder = ""
    for line in data.splitlines():
        if line.strip():
            line_parser = LineParser(line)
            base_folder = line_parser.parse_base_folder_name(configuration.remote_url, base_folder)
            local_folder_path = configuration.local_path + base_folder
            remote_path = line_parser.parse_remote_path()
            commit_revision = line_parser.parse_commit_revision()
            name = line_parser.parse_name()
            branch_name = line_parser.parse_branch()
            data_object = SvnRepositoryModel(name, base_folder, local_folder_path, remote_path, branch_name,
                                             commit_revision)
            external_repo_dictionary[name.lower()] = data_object

    return external_repo_dictionary
