from dataclasses import dataclass
from typing import Optional


@dataclass
class BranchModel:
    def __repr__(self):
        return (
            f"--------------------------------------------------------------------------------------------\n"
            f"repoName: {self.repo_name}\n"
            f"remotePath: {self.remote_path}\n"
            f"branches: {self.branches}\n"
            f"ignoreRefs: {self.ignore_refs}\n"
            f"--------------------------------------------------------------------------------------------"
        )

    repo_name: str
    remote_path: str
    branches: Optional[list] = None
    ignore_refs: Optional[list] = None
