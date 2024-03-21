import output.checkout as checkout
import output.migration as migration
import output.printRepositoryData as printRepositoryData
import output.gitIgnoreFile as gitIgnoreFile


def execute(arguments, data_dict):
    if arguments.print:
        printRepositoryData.print_info(data_dict)

    if arguments.create_gitignore:
        gitIgnoreFile.create_git_ignore_file(data_dict)

    if arguments.checkout:
        checkout.checkout_svn_externals(data_dict)

    if arguments.migrate:
        migration.migrate_svn_externals_to_git(data_dict)
