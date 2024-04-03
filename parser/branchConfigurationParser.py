import json


def parse():
    with open("data/branchConfiguration.json", "r") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise Exception("reading branch configuration failed")

    return data


def parse_repo_name(remote_path):
    name = remote_path.split("/")[-1]
    if name == "HC-Q":
        return "ag-nor-image-creator"
    elif name == "CuRMiT":
        return "ag-curmit"
    replace_underscore = name.replace("_", "-")
    replace_capitals = replace_capitals_with_lower_case_dash(replace_underscore)

    replace_stm_string = (
        replace_capitals.replace("stm32-f4", "stm32f4")
        .replace("stm32-l4xx", "stm32l4xx")
        .replace("stm32-f7", "stm32f7")
    )
    repo_name = replace_stm_string.replace("--", "-")
    ag_repo_name = "ag-" + repo_name
    return ag_repo_name


def replace_capitals_with_lower_case_dash(name):
    final_name = ""
    sequence = False

    for index, char in enumerate(name):
        if char.isupper() and sequence is False and index != 0:
            final_name = final_name + "-" + char.lower()
        else:
            final_name = final_name + char.lower()

        if char.isupper():
            sequence = True
        else:
            sequence = False

    return final_name


def debug():
    generic = dict()
    generic["trunk"] = {"folders": ["trunk", "Trunk", "current", "ProtoGen", "Plugin"]}
    generic["branches"] = {
        "folders": ["branches", "Branch", "Branches"],
        "subfolders": [
            "AMU",
            "AMU1",
            "FNE",
            "LBR",
            "MVE",
            "feature",
            "work",
            "release",
            "evaluation",
            "patches",
        ],
    }
    generic["tags"] = {
        "folders": ["tags", "distribution", "distr"],
        "subfolders": ["review", "release"],
    }

    specific = dict()
    specific["OS"] = {
        "branches": [
            "Projects/enAbleX1/SW/SharedComponents/CMSIS/Device/ST/STM32F7xx/{branches}"
        ]
    }
    specific["X1FlashCreator"] = {
        "tags": ["Projects/enAbleX1/SW/Tools/X1FlashCreator/{distr}"]
    }
    specific["edes"] = {"tags": ["Projects/enAbleX1/SW/Tools/Edes/{tags}"]}

    dictionary = dict()
    dictionary["generic"] = generic
    dictionary["specific"] = specific

    generic = dict()

    with open("data/branchConfiguration.json", "w+") as f:
        json.dump(dictionary, f, indent=4)

    # data= parse()

    test = dictionary["generic"]["branches"]["subfolders"]
    test = dictionary["generic"]["trunk"]
    print("print keys: ")
    for trunk_keys in test.keys():
        output = dictionary["generic"]["trunk"].get(trunk_keys)
        print(
            f'key: {trunk_keys}, dictionary["generic"]["trunk"].get(trunk_keys): {output}'
        )


if __name__ == "__main__":
    debug()
