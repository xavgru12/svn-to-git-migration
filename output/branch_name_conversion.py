import re

import execution.subprocess_execution
import parser.branchConfigurationParser
import output.migration
from collections import defaultdict


class BranchNameConversion:
    def __init__(self, repo_path) -> None:
        self.repo_path = repo_path
        self.branches_with_subfolders = parser.branchConfigurationParser.get_all_folders_with_subfolders_variations_as_list()
        self.branch_top_folders = (
            parser.branchConfigurationParser.get_all_branch_top_folders_as_list()
        )
        self.tag_top_folders = (
            parser.branchConfigurationParser.get_all_tag_top_folders_as_list()
        )
        self.tag_sub_folders = (
            parser.branchConfigurationParser.get_all_tag_sub_folders_as_list()
        )
        self.all_trunk_variations = (
            parser.branchConfigurationParser.get_all_trunk_variations_as_list()
        )

    def create_branches_dictionary(self):
        command_list = ["git", "for-each-ref", "--format=%(refname:short)"]
        branches = {}
        if self.check_for_repositories_without_trunk_branch():
            is_repository_without_branch_name = True
        else:
            is_repository_without_branch_name = False

        for line in execution.subprocess_execution.continuous_execute(
            command_list, self.repo_path, "stdout"
        ):
            if "@" not in line:
                line = line.replace("\n", "").replace("Ã¤", "ä")
                for branch_name in self.branch_top_folders:
                    branch_pattern = f"origin.*{branch_name}/"
                    if not branch_pattern == line:
                        svn_git_branch_pair = (
                            self.retrieve_svn_git_branch_or_tag_pair_from_line(
                                line, branch_pattern, self.branches_with_subfolders
                            )
                        )
                    else:
                        svn_git_branch_pair = None

                    branches.update(
                        svn_git_branch_pair
                    ) if svn_git_branch_pair is not None else None

                for trunk_name in self.all_trunk_variations:
                    trunk_pattern = f"origin/{trunk_name}"
                    svn_git_branch_pair = (
                        self.retrieve_svn_git_branch_or_tag_pair_from_line(
                            line, trunk_pattern, self.branches_with_subfolders
                        )
                    )
                    if svn_git_branch_pair is not None:
                        for key in svn_git_branch_pair:
                            svn_git_branch_pair[key] = "main"
                    branches.update(
                        svn_git_branch_pair
                    ) if svn_git_branch_pair is not None else None

                if "ag-curmit" in self.repo_path:
                    distr_patterns = ["distr", "gitDistrDummy"]
                    for pattern in distr_patterns:
                        current_pattern = f"origin/{pattern}"
                        svn_git_branch_pair = (
                            self.retrieve_svn_git_branch_or_tag_pair_from_line(
                                line, current_pattern, self.branches_with_subfolders
                            )
                        )
                        if svn_git_branch_pair is not None:
                            for key in svn_git_branch_pair:
                                svn_git_branch_pair[key] = f"{pattern}"
                        branches.update(
                            svn_git_branch_pair
                        ) if svn_git_branch_pair is not None else None

                if is_repository_without_branch_name:
                    if self.is_not_twice_in_string("/", line) and "origin/" in line:
                        svn_git_branch_pair = {line: "main"}
                        branches.update(
                            svn_git_branch_pair
                        ) if svn_git_branch_pair is not None else None

        return branches

    def create_tags_dictionary(self):
        if "ag-curmit" in self.repo_path:
            return {}

        tags = {}
        command_list = ["git", "for-each-ref", "--format=%(refname:short)"]
        for line in execution.subprocess_execution.continuous_execute(
            command_list, self.repo_path, "stdout"
        ):
            if "@" not in line:
                line = line.replace("\n", "").replace("Ã¤", "ä")
                for tag_top_folder in self.tag_top_folders:
                    tag_pattern = f"origin.*{tag_top_folder}/"
                    if not tag_pattern == line:
                        svn_git_tag_pair = (
                            self.retrieve_svn_git_branch_or_tag_pair_from_line(
                                line, tag_pattern, self.tag_sub_folders
                            )
                        )
                    else:
                        svn_git_tag_pair = None
                    tags.update(
                        svn_git_tag_pair
                    ) if svn_git_tag_pair is not None else None

        if self.has_duplicates(tags):
            duplicates = self.find_duplicates(tags)
            tags = self.modify_duplicate_values(tags, duplicates)

        return tags

    def find(self, pattern, line):
        match = re.match(pattern, line)
        if match:
            return match.group()

    def retrieve_svn_git_branch_or_tag_pair_from_line(self, line, pattern, branches):
        found_pattern = self.find(pattern, line)
        if found_pattern is None:
            return None

        for branch in branches:
            if line.endswith(branch):
                return None

        svn_branch = line
        git_branch = line.replace(found_pattern, "")

        return {svn_branch: git_branch}

    def find_duplicates(self, input_dict):
        value_to_keys = defaultdict(list)
        for key, value in input_dict.items():
            value_to_keys[value].append(key)

        # Find duplicates: values with more than one key
        duplicates = {
            value: keys for value, keys in value_to_keys.items() if len(keys) > 1
        }

        return duplicates

    def modify_duplicate_values(self, input_dict, duplicates):
        modified_dictionary = input_dict
        has_distr = False
        for svn_tag, git_tag in input_dict.items():
            if "distr" in svn_tag:
                modified_dictionary[svn_tag] = f"distr/{git_tag}"
                has_distr = True
        if has_distr is False:
            raise ValueError(f"distr was not found as key in duplicates: {duplicates}")

        return modified_dictionary

    def has_duplicates(self, dictionary):
        values = list(dictionary.values())
        return len(values) != len(set(values))

    def check_for_repositories_without_trunk_branch(self):
        command = "git svn info --url"
        output = execution.subprocess_execution.check_output_execute(
            command, self.repo_path
        )
        print(output)
        path = output.replace("\n", "").replace("http://ag-reposerver/repo/", "")
        branch_configuration = parser.branchConfigurationParser.parse()
        repositories_without_branch = branch_configuration[
            "repositoriesWithoutBranches"
        ]
        for each_repository in repositories_without_branch:
            if each_repository in path:
                return True

        return False

    def is_not_twice_in_string(self, char, string):
        count = 0
        for c in string:
            if c == char:
                count += 1
            if count > 1:
                return False
        return True


if __name__ == "__main__":
    repo_path = r"C:\localSharedPool\ag-curmit"
    # repo_path = r"C:\localSharedPool\ag-econ-w"
    branch_name_conversion = BranchNameConversion(repo_path)
    branches = branch_name_conversion.create_branches_dictionary()
    tags = branch_name_conversion.create_tags_dictionary()

    print(branches)
    print(tags)
