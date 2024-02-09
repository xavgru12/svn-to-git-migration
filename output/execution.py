import output.checkout as checkout
import output.migration as migration
import output.printRepositoryData as printRepositoryData
import output.gitIgnoreFile as gitIgnoreFile


def execute(arguments, data_dict):
    if arguments.print:
        migration.add_git_remote_branches_configuration(data_dict)
        printRepositoryData.print_info(data_dict)

    if arguments.create_gitignore:
        gitIgnoreFile.createGitIgnoreFile(data_dict)

    if arguments.checkout:
        checkout.checkout_svn_externals(data_dict)

    if arguments.migrate:
        confirm(
            "Preferably copy and paste the already migrated repositories."
            "This process takes one day to finish. Do you still want to continue?")
        migration.migrate_svn_externals_to_git(data_dict)


def confirm(prompt):
    """Prompts for yes or no response from the user. Returns True for yes and
    False for no.

    """
    while True:
        ans = input(prompt + " [y/n]: ")
        if ans.lower() == 'y':
            return True
        elif ans.lower() == 'n':
            return False
        else:
            print("Please enter y or n.")
