def get(checker):
    if checker is True:
        return "key", "value"
    else:
        return None


key1, value1 = get(True)

key2, value2 = get(False)

print(key1)
print(value1)

print(key2)
print(value2)
