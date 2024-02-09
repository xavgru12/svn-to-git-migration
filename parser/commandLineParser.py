import os
import argparse
import data.configuration as configuration


def parse():
    parser = argparse.ArgumentParser(description='Handle svn externals inside a git repository')
    parser.add_argument('--create-gitignore', action='store_true', help='Create a .gitignore file.')
    parser.add_argument('--checkout', action='store_true', help='Checkout svn externals recursively inside git.')
    parser.add_argument('--migrate', action='store_true',
                        help='Migrate svn externals to git in folder SharedComponentsSources/.')
    parser.add_argument('--print', action='store_true', help='Print collected data of externals.')
    parser.add_argument('--local-git-path', required=True, help='Specify path to local git repository.')
    args = parser.parse_args()

    if not os.path.isdir(f"{args.local_git_path}/.git"):
        raise argparse.ArgumentTypeError("path to local git repository is wrong")

    configuration.local_path = args.local_git_path

    return args
