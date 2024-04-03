from dataclasses import dataclass


@dataclass
class SvnRepositoryModel:
    def __repr__(self):
        return (
            f"--------------------------------------------------------------------------------------------\n"
            f"folderName: {self.name}\nbaseFolder: {self.base_folder}\n"
            f"folderPath: {self.local_folder_path}\n"
            f"remotePath: {self.remote_path}\nbranchName: {self.branch_name}\n"
            f"commitRevision: {self.commit_revision}\n"
            f"--------------------------------------------------------------------------------------------"
        )

    name: str
    base_folder: str
    local_folder_path: str
    remote_path: str
    branch_name: str
    commit_revision: str
