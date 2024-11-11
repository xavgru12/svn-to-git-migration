import subprocess
import sys
from parser.lineParser import LineParser
from model.svnRepositoryModel import SvnRepositoryModel
import data.configuration as configuration
import output.logger


def parse(remote_url, local_path, commit_revision):
    commit_revision = commit_revision.replace("r", "")
    external_information, remote_url = get_external_info_from_server(
        remote_url, local_path, commit_revision
    )

    data_dict = parse_external_info(external_information, remote_url, local_path)
    return data_dict


def get_external_info_from_server(branch_url, local_path, commit_revision):
    if commit_revision:
        common_command_part = f"svn propget svn:externals -r {commit_revision} -R"
    else:
        common_command_part = "svn propget svn:externals -R"

    command = f"{common_command_part} {branch_url}"
    common_command_split = common_command_part.split()
    command_split = common_command_split
    command_split.append(f"{branch_url}")
    print(command)
    logger = output.logger.LoggerFactory.create("logger")
    try:
        data = subprocess.check_output(command_split).decode(sys.stdout.encoding)
        logger.debug(data)
    except subprocess.CalledProcessError as propget:
        if branch_url.endswith(".cs"):
            return "", branch_url

        removed_last_part = "/".join(branch_url.split("/")[:-1])
        last_part = branch_url.split("/")[-1]
        logger.debug(f"removed_last_part: {removed_last_part}")
        common_command_split = common_command_part.split()
        command_split = common_command_split
        command_split.append(f"{removed_last_part}")
        print(" ".join(command_split))

        data = subprocess.check_output(command_split).decode(sys.stdout.encoding)
        data_dict = parse_external_info(data, removed_last_part, local_path)

        found_items = 0
        for repository in data_dict.values():
            if last_part in repository.remote_path:
                found_items += 1
                solved_url = (
                    f"{configuration.get_base_server_url()}/{repository.remote_path}"
                )
                common_command_split = common_command_part.split()
                command_split = common_command_split
                command_split.append(f"{solved_url}")
                print(" ".join(command_split))

                data = subprocess.check_output(command_split).decode(
                    sys.stdout.encoding
                )
                logger.debug(f"externals in fallback found: \n{data}")

        if found_items > 1:
            raise ValueError(f"several entries found for: {last_part}")
        if found_items == 0:
            return "", branch_url

    return data, branch_url


def parse_external_info(data, remote_url, local_path):
    external_repo_dictionary = dict()
    base_folder = ""
    for line in data.splitlines():
        if line.strip():
            line_parser = LineParser(line)
            base_folder = line_parser.parse_base_folder_name(
                remote_url,
                base_folder,
            )
            local_folder_path = local_path + base_folder if local_path else ""
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
