import os
import argparse
import data.configuration as configuration


def parse():
    parser = argparse.ArgumentParser(
        description="Handle svn externals inside a git repository"
    )
    parser.add_argument(
        "--create-gitignore", action="store_true", help="Create a .gitignore file."
    )
    parser.add_argument(
        "--checkout-svn",
        action="store_true",
        help="Checkout svn externals recursively inside git.",
    )
    parser.add_argument(
        "--checkout-git",
        action="store_true",
        help="Checkout the top repository including all external git repositories recursively.",
    )
    parser.add_argument(
        "--migrate",
        action="store_true",
        help="Migrate svn externals to git in folder SharedComponentsSources/.",
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help='Publish and backup from "--migration-output-path" to "--publish-output-path"',
    )
    parser.add_argument(
        "--publish-output-path",
        default="J:\\XGR\\sharedPool",
        help="Specify path to publish output",
    )
    parser.add_argument(
        "--migrate-econ-folder",
        action="store_true",
        help="Print collected data of externals.",
    )
    parser.add_argument(
        "--print", action="store_true", help="Print collected data of externals."
    )
    parser.add_argument("--local-path", help="Specify path to local git repository.")
    parser.add_argument(
        "--migration-output-path",
        default="C:\\localSharedPool",
        help="Specify path migration output.",
    )
    parser.add_argument(
        "--base-server-url",
        help="Specify path to the server.",
        default="http://ag-reposerver/repo",
    )
    parser.add_argument(
        "--remote-url",
        help="Specify path to the specific repository in the server.",
    )
    parser.add_argument(
        "--branch-path", help="Specify path to a branch.", default="trunk"
    )
    args = parser.parse_args()

    if not (args.publish or args.migrate_econ_folder):
        if args.remote_url is None:
            parser.error("--remote-url missing")

    if args.checkout_svn or args.create_gitignore or args.checkout_git:
        if args.local_path is None:
            parser.error("--local-path missing")

    configuration.write(args)

    return args
