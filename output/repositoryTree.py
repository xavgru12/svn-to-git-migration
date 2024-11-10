from __future__ import annotations
from typing import Any
from typing import Optional
import os
import shutil

import model.svnRepositoryModel
import parser.svnRepositoryParser
import data.configuration as configuration
import output.git_checkout
import output.migration
import output.logger

import output.external_subfolder_migration
import parser.branchConfigurationParser
import output.transformation
import execution.subprocess_execution
import execution.shutil_execution
import execution.git_execution

import pdb

class RecursiveList:
    def __init__(
        self,
        current: Optional[model.svnRepositoryModel.SvnRepositoryModel],
        dependencies: Optional[RecursiveList],
    ) -> None:
        """Initialize a new recursive list."""
        self.current = current
        self.dependencies = dependencies

    def parse_externals(self, current_folder_path=None):
        if current_folder_path is None:
            current_folder_path = self.current.local_folder_path

        logger = output.logger.LoggerFactory.create("logger")
        logger.debug(self.current)

        if self.current.branch_name is not None:
            branch_name = f"/{self.current.branch_name}"
        else:
            branch_name = ""

        if "cmake-os" in branch_name:
            branch_dict = {}
        else:
            branch_dict = parser.svnRepositoryParser.parse(
                f"{configuration.get_base_server_url()}/{self.current.remote_path}{branch_name}",
                current_folder_path,
                self.current.commit_revision,
            )
        self.dependencies = []
        for dependency in branch_dict.values():
            self.dependencies.append(RecursiveList(dependency, (None, None)))

        for repository in self.dependencies:
            dependency_folder_path = f"{current_folder_path}{repository.current.base_folder}/{repository.current.folder_name}"
            repository.parse_externals(dependency_folder_path)

    def get_remote_paths(self, remote_paths, iterator=None):
        if iterator is None:
            iterator = [self]
            remote_paths.append(self.current.remote_path)

        for recursive_list in iterator:
            for dependency in recursive_list.dependencies:
                path = dependency.current.remote_path
                if path not in remote_paths:
                    remote_paths.append(dependency.current.remote_path)

            self.get_remote_paths(remote_paths, recursive_list.dependencies)

    def get_repositories(self, repositories, iterator=None):
        if iterator is None:
            iterator = [self]
            repositories.append(self.current)

        for recursive_list in iterator:
            for dependency in recursive_list.dependencies:
                repositories.append(dependency.current)

            self.get_repositories(repositories, recursive_list.dependencies)

    def print(self, iterator=None):
        if iterator is None:
            iterator = [self]

        for recursive_list in iterator:
            name = self.current.folder_name.replace("/", "_")
            log_name = f"logs/repositoryTrees/{name}"
            os.makedirs(os.path.dirname(log_name), exist_ok=True)
            logger = output.logger.LoggerFactory.create(
                f"{name}-logger", f"{log_name}.log"
            )
            logger.debug(50 * "-" + "\n")
            logger.debug(f"current:\n {recursive_list.current},\n dependencies: ")
            for repository in recursive_list.dependencies:
                logger.debug(f"{repository.current}")
            logger.debug(50 * "-" + "\n")
            self.print(recursive_list.dependencies)


    def checkout_git_repositories(
        self, remote_paths, iterator=None
    ):  # remote_paths is not needed at all for git checkout
        if iterator is None:
            iterator = [self]
            print(
                f"checkout git top: {iterator[0].current.remote_path}"
            )  # self.current.remote_path
            # need to inverse the recursive list here
            output.git_checkout.checkout(self.current)
            print()

        for recursive_list in iterator:
            for dependency in recursive_list.dependencies:
                print(f"checkout git: {dependency.current.remote_path}")
                output.git_checkout.checkout(dependency.current)
                print()

            self.checkout_git_repositories(remote_paths, recursive_list.dependencies)

    def migrate_repositories(self, remote_paths, repositories):
        name = self.current.folder_name.replace("/", "_")
        log_name = f"logs/branchModels/{name}"
        os.makedirs(os.path.dirname(log_name), exist_ok=True)
        logger = output.logger.LoggerFactory.create(
            f"{name}-branchmodel", f"{log_name}.log"
        )

        output.migration.migrate_svn_externals_to_git(remote_paths, logger)

    def upload_repositories(self, repository_names):
        output.transformation.upload(repository_names)

    def upload_subfolder_repositories(self, repositories):
        output.external_subfolder_migration.migrate(repositories)

    def find_nodes(self, var=None):
        if var is None:
            self.checkout_top_repository()

        if var is not None:
            self.clone_repository(self.current)

        if self.dependencies:
            print("has dependencies")
            print("current: ")
            print(self.current)
            for dependency in self.dependencies:
                dependency.find_nodes("test")

                self.add_submodule(dependency.current)

            if self.current.folder_name == "ag-mobile-app":
                print("parsed recursively the mobile app")

            if var is not None:
                working_directory = os.path.join(self.current.local_folder_path, self.current.folder_name)
            else:
                working_directory = self.current.local_folder_path
            self.create_and_push_commit(self.current, working_directory)
        else:
            pass
            # print("no more dependencies")
            # print("current: ")
            # print(self.current)


    def clone_repository(self, repository):
        repository_name = parser.branchConfigurationParser.parse_repo_name(repository.remote_path)
        repository_name_no_externals = f"{repository_name}-no-externals"
        folder_name = repository.folder_name
        local_folder_path = repository.local_folder_path

        clone_command = f"git submodule add --force git@bitbucket.org:curtisinst/{repository_name_no_externals}.git ./{folder_name}"

        if folder_name.endswith(".cs"):
            print(f"path is file (no submodule): {folder_name}")
            return

        os.makedirs(local_folder_path, exist_ok=True)

        execution.subprocess_execution.check_output_execute(
                clone_command, local_folder_path
            )
        
        repository_folder = os.path.join(local_folder_path, folder_name)

        print_mode = True

        execution.git_execution.add_remote_upload(repository_name, repository_folder)
        if execution.git_execution.check_remote_upload_exists(repository_folder):
            push_repository_as_live = "git push upload --mirror"
            execution.subprocess_execution.check_output_execute(
                    push_repository_as_live, repository_folder
                )
        else:
            if print_mode:
                self.add_missing_remote_to_file(repository_name)
                print(f"added missing remote: {repository_name}")
            else:
                raise ValueError(
                    f'error: remote origin for repository: "{repository_name}" does not exist'
                )


    def create_and_push_commit(self, repository, working_directory):
        print("push repository:")
        print(repository)
        repository_name = parser.branchConfigurationParser.parse_repo_name(repository.remote_path)

        add_command = "git add -A"
        execution.subprocess_execution.check_output_execute(
                add_command, working_directory
            )

        commit_command = ["git", "commit", "-m", "activate git submodules"]
        execution.subprocess_execution.check_output_execute(
                commit_command, working_directory
            )
        
        print_mode = True

        if execution.git_execution.check_remote_upload_exists(working_directory):
            push_command = "git push upload main --force"
            execution.subprocess_execution.check_output_execute(
                    push_command, working_directory
                )
        else:
            if print_mode:
                self.add_missing_remote_to_file(repository_name)
                print(f"added missing remote: {repository_name}")
            else:
                raise ValueError(
                    f'error: remote origin for repository: "{repository_name}" does not exist'
                )

    def add_missing_remote_to_file(self, name):
        file_path = "remotes.txt"

        with open(file_path, "a") as file:
            file.write(f"{name}\n")

    def checkout_top_repository(self):
        repository = self.current
        repository_name = parser.branchConfigurationParser.parse_repo_name(repository.remote_path)
        repository_name_no_externals = f"{repository_name}-no-externals"

        local_folder_path = repository.local_folder_path
        folder_name = os.path.basename(local_folder_path)
        base_directory = os.path.dirname(local_folder_path)

        execution.shutil_execution.delete(local_folder_path)

        command = f"git clone git@bitbucket.org:curtisinst/{repository_name_no_externals}.git ./{folder_name}"
        print(command)

        execution.subprocess_execution.check_output_execute(
                command, base_directory
            )
        execution.git_execution.add_remote_upload(repository_name, local_folder_path)


    def add_submodule(self, repository):
        repository_name = parser.branchConfigurationParser.parse_repo_name(repository.remote_path)

        local_folder_path = repository.local_folder_path
        folder_name = repository.folder_name

        if folder_name.endswith(".cs"):
            print(f"path is file (no submodule): {folder_name}")
            return

        root_git_path = self.get_root_git_path(local_folder_path)
        subpath = local_folder_path[len(root_git_path) + 1:]
        print(subpath)

        self.git_delete_folder(folder_name, local_folder_path, subpath, root_git_path)
        execution.shutil_execution.delete(os.path.join(local_folder_path, folder_name))
        os.makedirs(local_folder_path, exist_ok=True)

        command = f"git submodule add --force git@bitbucket.org:curtisinst/{repository_name}.git ./{folder_name}"
        print(command)

        execution.subprocess_execution.check_output_execute(
                command, local_folder_path
            )

    def get_root_git_path(self, local_folder_path):
        local_path = configuration.get_local_path()
        remove_folder = local_folder_path
        root_git_path = local_folder_path

        while remove_folder != local_path:
            root_git_path = remove_folder
            remove_folder = os.path.dirname(remove_folder)

        print(f"root git path: {root_git_path}")
        return root_git_path


    def git_delete_folder(self, folder, path, relative_path, root_git_path):
        if os.path.exists(os.path.join(path, folder)):
            command = f"git rm {folder} -rf"
            execution.subprocess_execution.check_output_execute(
                    command, path
                )
            execution.shutil_execution.delete(os.path.join(root_git_path, f".git/modules/{relative_path}/{folder}"))
        

class RepositoryTree:
    recursive_list = Optional[RecursiveList]
    top = Optional[model.svnRepositoryModel.SvnRepositoryModel]

    def __init__(self, top):
        self.top = top
        self.remote_paths = []
        self.repositories = []
        self.repository_names = []

    def parse_recursively(self):
        self.recursive_list = RecursiveList(self.top, (None, None))
        self.recursive_list.parse_externals()

    def print_tree(self):
        self.recursive_list.print()

    def get_list_of_remote_paths_recursively(self):
        self.recursive_list.get_remote_paths(self.remote_paths)
        return self.remote_paths

    def get_list_of_repository_names_recursively(self):
        if not self.remote_paths:
            self.recursive_list.get_remote_paths(self.remote_paths)

        self.repository_names = []
        for remote_path in self.remote_paths:
            repository_name = parser.branchConfigurationParser.parse_repo_name(
                remote_path
            )
            self.repository_names.append(repository_name)

        return self.repository_names

    def get_list_of_repositories_recursively(self):
        self.recursive_list.get_repositories(self.repositories)
        return self.repositories

    def checkout_git_repositories_recursively(self):
        if not self.remote_paths:
            self.get_list_of_remote_paths_recursively()

        if not self.repositories:
            self.get_list_of_repositories_recursively()

        self.recursive_list.checkout_git_repositories(self.remote_paths)

    def migrate_repositories_recursively(self):
        if not self.remote_paths:
            self.get_list_of_remote_paths_recursively()

        if not self.repositories:
            self.get_list_of_repositories_recursively()

        self.recursive_list.migrate_repositories(self.remote_paths, self.repositories)

    def upload_repositories_recursively(self):
        if not self.repository_names:
            self.get_list_of_repository_names_recursively()

        self.recursive_list.upload_repositories(self.repository_names)

    def upload_subfolder_repositories_recursively(self):
        if not self.repositories:
            self.get_list_of_repositories_recursively()

        self.recursive_list.upload_subfolder_repositories(self.repositories)

    def find_nodes_recursively(self):
        self.recursive_list.find_nodes()
