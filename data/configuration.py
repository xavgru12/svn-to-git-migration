import json
import os


def write(args):
    configuration = dict()
    args.migrate_econ_folder
    if args.remote_url:
        configuration["remote_url"] = args.remote_url
    if args.local_path:
        configuration["local_path"] = args.local_path
    configuration["base_server_url"] = args.base_server_url
    configuration["branch_path"] = args.branch_path
    configuration["migration_output_path"] = args.migration_output_path
    configuration["publish_output_path"] = args.publish_output_path
    configuration["migrate_econ_folder"] = args.migrate_econ_folder
    configuration["transformation_output_path"] = args.transformation_output_path

    file = "cache/configuration.json"
    os.makedirs(os.path.dirname(file), exist_ok=True)
    with open("cache/configuration.json", "w+") as f:
        json.dump(configuration, f, indent=4)


def load():
    with open("cache/configuration.json", "r") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise Exception("reading command line configuration failed")
    return data


def get_remote_url():
    data = load()
    return data["remote_url"]


def get_base_server_url():
    data = load()
    return data["base_server_url"]


def get_local_path():
    data = load()
    return data.get("local_path")


def get_branch_path():
    data = load()
    return data["branch_path"]


def get_migration_output_path():
    data = load()
    return data["migration_output_path"]


def get_publish_output_path():
    data = load()
    return data["publish_output_path"]


def get_transformation_output_path():
    data = load()
    return data["transformation_output_path"]
