import data.configuration as configuration
import parser.branchConfigurationParser
import re


class LineParser:
    def __init__(self, line):
        self.line = line

        self.possible_branch_names = []
        branch_configuration = parser.branchConfigurationParser.parse()
        generic_configuration = branch_configuration["generic"]

        for branch_type in generic_configuration.keys():
            self.possible_branch_names.extend(
                generic_configuration[branch_type]["folders"]
            )

        self.repositories_without_trunk_branch = branch_configuration[
            "repositoriesWithoutBranches"
        ]

    def is_line_with_new_base_folder(self):
        if " - ^" in self.line or " - " in self.line:
            return True
        else:
            return False

    def cut_off_branch_name(self, line):
        for branch_name in self.possible_branch_names:
            if branch_name in line:
                return line.split(f"/{branch_name}")[0]

        for remote_path in self.repositories_without_trunk_branch:
            if remote_path in line:
                return remote_path

        raise Exception(f"branch name analysis failed: line: {line}")

    def parse_remote_path(self):
        if self.line.startswith("-r"):
            possibly_removed_revision = self.remove_duplicate_revision(self.line)
        else:
            possibly_removed_revision = self.line

        line_cut_off_beginning = possibly_removed_revision.split("^/")[-1].split(" - ")[
            -1
        ]
        line_cut_off_revision_tag = line_cut_off_beginning.split("@")[0]
        line_cut_off_branch_name = self.cut_off_branch_name(line_cut_off_revision_tag)
        line_cut_off_base_server_url = line_cut_off_branch_name.replace(
            f"{configuration.get_base_server_url()}/", ""
        )
        remote_branch_name = line_cut_off_base_server_url
        remote_branch_name = remote_branch_name.replace(
            "LogicalComponents", "LogicalComponents (obsolete)"
        )
        return remote_branch_name

    def remove_duplicate_revision(self, s):
        # Define the regex pattern for the prefix
        pattern = r"^-r \d+ "
        # Use re.sub to replace the prefix with an empty string if it exists
        return re.sub(pattern, "", s)

    def parse_commit_revision(self):
        modified_line = self.line.split("@")[-1].split(" ")[0]
        try:
            modified_line = int(modified_line)
        except ValueError:
            modified_line = None

        return modified_line

    def parse_name(self):
        modified_line = self.line.split(" ")[-1]
        return modified_line

    def parse_base_folder_name(self, branch_url, current_folder=None):
        if current_folder is None:
            current_folder = ""
        if self.is_line_with_new_base_folder():
            base_folder = self.line.split()[0].replace("%20", " ")
            base_folder = base_folder.removeprefix(branch_url)
            return base_folder
        else:
            return current_folder

    def parse_branch(self):
        if self.line.startswith("-r"):
            possibly_removed_revision = self.remove_duplicate_revision(self.line)
        else:
            possibly_removed_revision = self.line

        line = possibly_removed_revision.split("@")[0]

        if "^/" in line:
            line = line.split("^/")[-1]
        if "- ^/" in line:
            line = line.split("- ^/")[-1]
        if " - " in line:
            line = line.split(" - ")[-1]

            # these splits are needed to get branch and remote path, how about a function that splits this and which can be used in several locations?
        line = line.split()[0]
        for branch_name in self.possible_branch_names:
            if branch_name in line:
                modified_line = branch_name + line.split(branch_name)[1]
                return modified_line

        for remote_path in self.repositories_without_trunk_branch:
            if remote_path in line:
                branch = line.replace(f"{remote_path}", "")
                branch = branch[1:] if branch.startswith("/") else branch
                return branch
