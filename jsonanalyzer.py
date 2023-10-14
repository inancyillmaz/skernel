import json


def extract_is_unit_test(json_string):
    data = json.loads(json_string)
    return data.get("isUnitTest", None)
