from __future__ import annotations
from typing import Any
from typing import Optional
import os
import shutil

import model.svnRepositoryModel
import parser.svnRepositoryParser
import data.configuration as configuration
import output.gitCheckout
import output.migration
import output.logger

import output.external_subfolder_migration
import parser.branchConfigurationParser
import output.transformation
import execution.subprocess_execution
import execution.shutil_execution

import pdb

class RecursiveList:
    def __init__(
        self,
        #parent: Optional[RecursiveList,
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

    def find_node_which_childs_have_no_externals():
        #when found, checkout current repo, create submodules for all dependencies and upload, then go up to parent and repeat
        # do this for every "branch" of nodes by iterating over all dependencies
        # first step: find node and print the node along with some information, best would be to get back to root level showing the complete branch node
        # second step: find more nodes like this in this branch, show complete node branch
        # go up the levels until root

        pass

    def checkout_git_repositories(
        self, remote_paths, iterator=None
    ):  # remote_paths is not needed at all for git checkout
        if iterator is None:
            iterator = [self]
            print(
                f"checkout git top: {iterator[0].current.remote_path}"
            )  # self.current.remote_path
            # need to inverse the recursive list here
            output.gitCheckout.checkout(self.current)
            print()

        for recursive_list in iterator:
            for dependency in recursive_list.dependencies:
                print(f"checkout git: {dependency.current.remote_path}")
                output.gitCheckout.checkout(dependency.current)
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
        # if has dependency: add and commit (make a function that prints add and comment)
        # do for each on this node_level. if done, go to parent and do add and commit immediately,
        # since we already made sure all the child nodes are checked

        if var is None:
            self.checkout_top_repository()

        if self.dependencies:
            print("has dependencies")
            print("current: ")
            print(self.current)
            for dependency in self.dependencies:
                #if dependency.dependencies
                dependency.find_nodes("test")
                self.add_submodule(dependency.current)
            #add and commit all dependencies in self.dependencies
            if self.current.folder_name == "ag-mobile-app":
                print("parsed recursively the mobile app")
            # git commit and git push, save updated commit hash in repository model
        else:
            pass
            # print("no more dependencies")
            # print("current: ")
            # print(self.current)

        # go up routine


    def checkout_top_repository(self):
        repository = self.current
        repository_name = parser.branchConfigurationParser.parse_repo_name(repository.remote_path)
        repository_name_no_externals = f"{repository_name}-no-externals"

        local_folder_path = repository.local_folder_path
        folder_name = os.path.basename(local_folder_path)
        base_directory = os.path.dirname(local_folder_path)

        execution.shutil_execution.delete(local_folder_path)

        command = f"git clone -b main --depth 1 git@bitbucket.org:curtisinst/{repository_name_no_externals}.git ./{folder_name}"
        print(command)

        execution.subprocess_execution.check_output_execute(
                command, base_directory
            )
        # git clone git@bitbucket.org:curtisinst/ag-ats-no-externals.git


    def add_submodule(self, repository):
        print(f"git submodule add {repository.folder_name}")
        # git checkout

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
