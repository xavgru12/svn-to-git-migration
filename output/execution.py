import os
import output.svnCheckout as svnCheckout
import output.migration as migration
import output.printRepositoryData as printRepositoryData
import output.gitIgnoreFile as gitIgnoreFile
import output.publish
import parser.branchConfigurationParser
import parser.svnRepositoryParser
import data.configuration as configuration
import output.repositoryTree
import model.svnRepositoryModel
import output.logger


def execute(arguments):
    if (
        arguments.print
        or arguments.create_gitignore
        or arguments.checkout_svn
        or arguments.checkout_git
        or arguments.migrate
    ):
        remote_path = configuration.get_remote_url().replace(
            f"{configuration.get_base_server_url()}/", ""
        )
        name = parser.branchConfigurationParser.parse_repo_name(remote_path)
        local_path = configuration.get_local_path()

        if arguments.checkout_git:
            local_path = os.path.join(local_path, name)

        print(f"local_path: {local_path}")

        branch_name = configuration.get_branch_path()

        top = model.svnRepositoryModel.SvnRepositoryModel(
            name, "", local_path, remote_path, branch_name, ""
        )

        tree = output.repositoryTree.RepositoryTree(top)
        tree.parse_recursively()
        tree.print_tree()

        remote_paths = tree.get_list_of_remote_paths_recursively()

    if arguments.print:
        tree.print_tree()

    if arguments.create_gitignore:
        gitIgnoreFile.create_git_ignore_file(
            tree.recursive_list
        )  # rework for recursive

    if arguments.checkout_svn:
        svnCheckout.checkout_svn_externals(tree.recursive_list)

    if arguments.checkout_git:
        tree.checkout_git_repositories_recursively()

    if arguments.migrate:
        log_name = f"logs/branchModels/{name}"
        os.makedirs(os.path.dirname(log_name), exist_ok=True)
        logger = output.logger.LoggerFactory.create(
            f"{name}-branchmodel", f"{log_name}.log"
        )
        migration.migrate_svn_externals_to_git(remote_paths, logger)

    if arguments.publish:
        output.publish.publish()

    if arguments.migrate_econ_folder:
        migration.migrate_econ_folder()
