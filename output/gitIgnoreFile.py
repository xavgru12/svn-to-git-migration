import data.configuration as configuration


def create_git_ignore_file(recursive_list):
    with open(f"{configuration.get_local_path()}/.gitignore", "w") as f:
        f.write(
            "DebugConfig\nDebug\nobj\n*uvguix*\n*uvopt*\n.vs\n*.vcxproj*\n*uvproj\n"
        )
        f.write("SharedComponentsSources/\n")
        f.write("BuildVersion.h\n")
        f.write("Version.properties\n")
        f.write("Projects/packages/\n")
        for dependency in recursive_list.dependencies:
            f.write(
                f"{dependency.current.base_folder}/{dependency.current.folder_name}/\n"
            )
            # create git ignore for complete tree
