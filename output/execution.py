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


def execute(arguments):
    if (
        arguments.print
        or arguments.create_gitignore
        or arguments.checkout_svn
        or arguments.checkout_git
        or arguments.migrate
    ):  # reverse this if check, set sys.exit()
        #rename local_git_path to local_path, make check at svnCheckout that it needs to be a git repository
        remote_path = configuration.get_remote_url().replace(f"{configuration.get_base_server_url()}/", "")
        name = parser.branchConfigurationParser.parse_repo_name(remote_path)
        local_path = configuration.get_local_git_path()
        print(local_path)
        if arguments.checkout_git:
            local_path = os.path.join(local_path, name)

        branch_name = configuration.get_branch_path()

        top = model.svnRepositoryModel.SvnRepositoryModel(name, "", local_path, remote_path, branch_name, "")

        tree = output.repositoryTree.RepositoryTree(top) 
        tree.parseRecursively()                 
        tree.printTree()    

        remote_paths = tree.get_list_of_remote_paths_recursively() #maybe remote_paths: repo:name dict

    if arguments.print:
        tree.printTree()

    if arguments.create_gitignore:
        gitIgnoreFile.create_git_ignore_file(tree.recursive_list) #rework for recursive

    if arguments.checkout_svn:
        svnCheckout.checkout_svn_externals(tree.recursive_list) 

    if arguments.checkout_git:
        tree.checkout_git_repositories_recursively()
#if checkout git: use tree plus remote_paths:repo_name dict, would be easier to save repo_name in svn_repo_model
# take repositories from public shared pool, copy them to right folder and do a git checkout, do this recursively using recursive_list
  
  
    if arguments.migrate:
        migration.migrate_svn_externals_to_git(remote_paths)

    if arguments.publish:
        output.publish.publish()

    if arguments.migrate_econ_folder:
        migration.migrate_econ_folder()
