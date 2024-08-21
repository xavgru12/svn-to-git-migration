import data.configuration as configuration
import os
import shutil
import datetime


def publish():
    local_pool_path = configuration.get_migration_output_path()
    publish_path = configuration.get_publish_output_path()
    print(f"migration_output_path: {local_pool_path}")
    print(f"publish_output_path: {publish_path}")
    zip_repositories_at(local_pool_path)
    backup(publish_path)
    move_zips(local_pool_path, publish_path)
    delete_zips_at(local_pool_path)


def zip_repositories_at(repository_path):
    for name in os.listdir(repository_path):
        if not name.endswith(".zip") and not name.endswith(".txt"):
            dir = os.path.join(repository_path, name)
            print(f"zipped: {dir}")
            shutil.make_archive(dir, "zip", dir)


def move_zips(source, destination):
    timestamp = get_timestamp()
    with open(os.path.join(destination, "latest", "timestamp.txt"), "w+") as f:
        f.write(timestamp)

    for name in os.listdir(source):
        if name.endswith(".zip"):
            zipped = os.path.join(source, name)
            destination_latest = os.path.join(destination, "latest")
            os.makedirs(destination_latest, exist_ok=True)
            print(f"publish from: {zipped} to: {destination_latest}")
            shutil.copy(zipped, destination_latest)


def get_timestamp():
    return datetime.datetime.now().strftime("%d-%m-%Y_%H-%M")


def backup(cwd_path):
    file = os.path.join(cwd_path, "latest", "timestamp.txt")

    if not os.path.isfile(file):
        raise Exception("timestamp.txt does not exist in /latest/")

    with open(os.path.join(cwd_path, "latest", "timestamp.txt"), "r") as f:
        timestamp = f.readlines()[0]

    if not timestamp:
        raise Exception("latest/timestamp.txt is empty")

    latest_path = os.path.join(cwd_path, "latest")
    if not os.path.exists(latest_path):
        raise Exception(f"/latest directory does not exist at: {cwd_path}")

    for name in os.listdir(latest_path):
        if name.endswith(".zip"):
            zipped = os.path.join(latest_path, name)
            destination = os.path.join(cwd_path, "backup", timestamp)
            os.makedirs(destination, exist_ok=True)
            print(f"backup from: {zipped} to: {destination}")
            shutil.copy(zipped, destination)


def delete_zips_at(cwd_path):
    for name in os.listdir(cwd_path):
        if name.endswith(".zip"):
            zipped = os.path.join(cwd_path, name)
            os.remove(zipped)
