import re
import parser.branchConfigurationParser

import pdb


class ExternalChecker:
    def __init__(self, branch_name, branches, tags, remote_path) -> None:
        self.branch_name = f"origin/{branch_name}"
        self.branches = branches
        self.tags = tags
        self.remote_path = remote_path
        self.subfolder = None
        self.extracted_branch_name = None

    def get_subfolder(self):
        return self.subfolder

    def get_extracted_branch_name(self):
        return self.extracted_branch_name  # .replace("origin/", "")

    def find_suitable_names(self, branches):
        checker_list = []
        for branch in branches:
            branch_without_sub = branch.replace("sub", "")
            if branch_without_sub in self.branch_name:
                extra_string = self.branch_name.replace(branch_without_sub, "")
                count = len(extra_string)
                checker_pair = (branch_without_sub, branch, count)
                checker_list.append(checker_pair)

        if self.branch_name == "origin/distr":
            checker_pair = (self.branch_name, self.branch_name, 0)
            checker_list.append(checker_pair)

        return checker_list

    def has_subfolder(self):
        checker_list = self.find_suitable_names(self.branches)
        checker_list.extend(self.find_suitable_names(self.tags))

        branch_configuration = parser.branchConfigurationParser.parse()
        repositories_without_branch = branch_configuration[
            "repositoriesWithoutBranches"
        ]
        if self.remote_path in repositories_without_branch:
            return False

        branch_without_sub, branch_with_sub, number = self.find_smallest_int(
            checker_list
        )
        if number == 0:
            self.extracted_branch_name = branch_with_sub
            return False
        else:
            self.subfolder = self.branch_name.replace(f"{branch_without_sub}/", "")
            self.extracted_branch_name = branch_with_sub
            return True

    def find_smallest_int(self, pairs):
        """Finds the smallest integer among string and integer pairs.

        Args:
            pairs: A list of tuples, where each tuple contains a string and an integer.

        Returns:
            The smallest integer found in the pairs, or None if no integers are found.
        """

        smallest_int = None
        for branch_without_sub, branch_with_sub, number in pairs:
            if isinstance(number, int) and (
                smallest_int is None or number < smallest_int
            ):
                smallest_int = number
                branch_without_sub_smallest_int = branch_without_sub
                branch_with_sub_smallest_int = branch_with_sub
        if smallest_int is None:
            breakpoint()
            raise ValueError("parsing all branches finds nothing")

        return (
            branch_without_sub_smallest_int,
            branch_with_sub_smallest_int,
            smallest_int,
        )


def is_type_external_subfolders(branch_name):
    possible_branch_names = (
        parser.branchConfigurationParser.get_all_variations_as_list()
    )
    for possible_branch_name in possible_branch_names:
        if possible_branch_name == branch_name:
            return None

    suitable_branch = find_most_suitable_branch_name(branch_name)
    if suitable_branch is not None:
        possible_subfolder_branch = branch_name.replace(f"{suitable_branch}/", "")
        if "/" in possible_subfolder_branch:
            cut_off_branch_from_subfolder = re.sub(
                r"^.*?/", "", possible_subfolder_branch
            )
            return cut_off_branch_from_subfolder

    return None


def find_most_suitable_branch_name(branch_name):
    possible_branch_names = (
        parser.branchConfigurationParser.get_all_variations_as_list()
    )
    for possible_branch_name in possible_branch_names:
        if possible_branch_name in branch_name:
            return possible_branch_name
