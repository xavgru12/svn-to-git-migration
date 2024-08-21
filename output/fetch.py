import os
import multiprocessing

import data.configuration as configuration
import output.migration
import output.publish


def fetch_and_publish_all():
    fetch()
    output.publish.publish()


def fetch():
    migration_output_path = configuration.get_migration_output_path()
    repository_names = [
        repository_name
        for repository_name in os.listdir(migration_output_path)
        if ".txt" not in repository_name
    ]

    # debug
    # for repository in repository_names:
    #     output.migration.migrate_each(repository)
    with multiprocessing.Pool() as pool:
        for result in pool.imap(output.migration.migrate_each, repository_names):
            if isinstance(result, Exception):
                print("Got exception: {}".format(result))
        pool.close()
        pool.join()
