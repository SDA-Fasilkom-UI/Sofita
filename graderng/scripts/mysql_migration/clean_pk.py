import json
import os


def run(*args):
    if len(args) == 0 or not os.path.isfile(args[0]):
        raise FileNotFoundError("file not found")

    print("[*] Running...")

    filename = args[0]
    with open(filename) as f:
        items = json.load(f)
        num_items = len(items)
        for idx, item in enumerate(items):
            if idx % 500 == 0:
                print("[*] Running... {} of {}".format(idx+1, num_items))

            remove_pk_models = [
                "grader.submission",
                "job.mossjob",
                "job.reportjob",
                "app.token",
            ]

            if item["model"] in remove_pk_models:
                item.pop("pk", 0)

    print("[*] Writing...")
    with open(filename + "-cleaned.json", "w") as g:
        json.dump(items, g)

    print("[*] Done.")
