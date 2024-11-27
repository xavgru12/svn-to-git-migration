from __future__ import annotations
from typing import Any
from typing import Optional
import os

import model.svnRepositoryModel
import parser.svnRepositoryParser
import data.configuration as configuration
import output.git_checkout
import output.migration
import output.logger
import output.external_subfolder_migration
import parser.branchConfigurationParser
import output.transformation
import output.git_checkout

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

    def checkout_repositories(self, var=None):
        if var is None:
            output.git_checkout.checkout_top_repository(self.current)

        if var is not None:
            output.git_checkout.add_submodule(self.current)

        if self.dependencies:
            print("has dependencies")
            print("current: ")
            print(self.current)
            for dependency in self.dependencies:
                dependency.checkout_repositories("test")

                output.git_checkout.add_submodule(dependency.current)

            if self.current.folder_name == "ag-mobile-app":
                print("parsed recursively the mobile app")

            if var is not None:
                working_directory = os.path.join(self.current.local_folder_path, self.current.folder_name)
            else:
                working_directory = self.current.local_folder_path
            output.git_checkout.create_and_push_commit(self.current, working_directory)
        else:
            pass
            # print("no more dependencies")
            # print("current: ")
            # print(self.current)


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

    def checkout_repositories_recursively(self):
        self.recursive_list.checkout_repositories()
