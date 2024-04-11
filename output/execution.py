import output.checkout as checkout
import output.migration as migration
import output.printRepositoryData as printRepositoryData
import output.gitIgnoreFile as gitIgnoreFile
import output.publish
import parser.svnRepositoryParser
import data.configuration as configuration


def execute(arguments):
    if (
        arguments.print
        or arguments.create_gitignore
        or arguments.checkout
        or arguments.migrate
    ):
        data_dict = parser.svnRepositoryParser.parse(configuration.get_remote_url())

    if arguments.print:
        printRepositoryData.print_info(data_dict)

    if arguments.create_gitignore:
        gitIgnoreFile.create_git_ignore_file(data_dict)

    if arguments.checkout:
        checkout.checkout_svn_externals(data_dict)

    if arguments.migrate:
        migration.migrate_svn_externals_to_git(data_dict)

    if arguments.publish:
        output.publish.publish()

    if arguments.migrate_econ_folder:
        migration.migrate_econ_folder()
