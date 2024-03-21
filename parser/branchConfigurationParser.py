import json


def parse():
    with open("data/branchConfiguration.json", "r") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise Exception("reading branch configuration failed")

    return data


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

    with open(f"data/branchConfiguration.json", "w+") as f:
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
