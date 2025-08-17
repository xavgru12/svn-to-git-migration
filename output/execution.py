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
import output.fetch


def execute(arguments):
    if arguments.reset_migration_output_path:
        print("reset migration output path...")
        migration.reset_migration_output_path()
    if (
        arguments.print
        or arguments.create_gitignore
        or arguments.checkout_svn
        or arguments.checkout_git
        or arguments.migrate
        or arguments.upload_no_externals
        or arguments.upload_no_externals_subfolders
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

    if arguments.fetch_and_publish_all:
        output.fetch.fetch_and_publish_all()

    if arguments.print:
        tree.print_tree()

    if arguments.create_gitignore:
        gitIgnoreFile.create_git_ignore_file(
            tree.recursive_list
        )  # rework for recursive

    if arguments.checkout_svn:
        svnCheckout.checkout_svn_externals(tree.recursive_list)

    if arguments.checkout_git:
        tree.checkout_repositories_recursively()

    if arguments.migrate:
        tree.migrate_repositories_recursively()

    if arguments.upload_no_externals:
        tree.upload_repositories_recursively()

    if arguments.upload_no_externals_subfolders:
        tree.upload_subfolder_repositories_recursively()

    if arguments.publish:
        output.publish.publish()

    if arguments.migrate_econ_folder:
        migration.migrate_econ_folder()

    if arguments.upload_econ_folder:
        migration.upload_econ_folder()

    if arguments.upload_econ_folder_subfolders:
        migration.upload_econ_folder_subfolders()
