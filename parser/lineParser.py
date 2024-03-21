import data.configuration as configuration


class LineParser:
    possible_branch_names = [
        "/trunk",
        "/tags",
        "/distr",
        "/ProtoGen",
        "/Branches",
        "/branches",
        "/Trunk",
        "/Plugin",
    ]

    def __init__(self, line):
        self.line = line

    def is_line_with_new_base_folder(self):
        if " - ^" in self.line or " - " in self.line:
            return True
        else:
            return False

    def cut_off_branch_name(self, line):
        for branch_name in self.possible_branch_names:
            if branch_name in line:
                return line.split(branch_name)[0]

        raise Exception(f"branch name analysis failed: line: {line}")

    def parse_remote_path(self):
        line_cut_off_beginning = self.line.split("^/")[-1].split(" - ")[-1]
        line_cut_off_revision_tag = line_cut_off_beginning.split("@")[0]
        line_cut_off_branch_name = self.cut_off_branch_name(line_cut_off_revision_tag)
        line_cut_off_base_server_url = line_cut_off_branch_name.replace(
            f"{configuration.get_base_server_url()}/", ""
        )
        remote_branch_name = line_cut_off_base_server_url

        return remote_branch_name

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
        line = self.line.split("@")[0]

        if "^/" in line:
            line = line.split("^/")[-1]
        if "- ^/" in line:
            line = line.split("- ^/")[-1]
        line = line.split()[0]
        print(f"branch line: {line}")
        for branch_name in self.possible_branch_names:
            if branch_name in line:
                modified_line = branch_name + line.split(branch_name)[1]
                return modified_line

    def parse_repo_name(self):
        remote_path = self.parse_remote_path()
        name = remote_path.split("/")[-1]
        if name == "HC-Q":
            return "ag-nor-image-creator"
        elif name == "CuRMiT":
            return "ag-curmit"
        replace_underscore = name.replace("_", "-")

        replace_capitals = self.replace_capitals_with_lower_case_dash(
            replace_underscore
        )

        replace_stm_string = (
            replace_capitals.replace("stm32-f4", "stm32f4")
            .replace("stm32-l4xx", "stm32l4xx")
            .replace("stm32-f7", "stm32f7")
        )
        repo_name = replace_stm_string.replace("--", "-")
        ag_repo_name = "ag-" + repo_name
        return ag_repo_name

    @staticmethod
    def replace_capitals_with_lower_case_dash(name):
        final_name = ""
        sequence = False

        for index, char in enumerate(name):
            if char.isupper() and sequence is False and index != 0:
                final_name = final_name + "-" + char.lower()
            else:
                final_name = final_name + char.lower()

            if char.isupper():
                sequence = True
            else:
                sequence = False

        return final_name
