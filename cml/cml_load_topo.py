import argparse
import time
import os
from functools import wraps
from virl2_client import ClientLibrary


def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} ==> {(end - start)} s")

        return result

    return wrapper


epilog = """

  Load start up config into the CML device

"""


def parseArgs():
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=epilog,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--config",
        help="path to the location of the device running-config",
        required=True,
    )

    return parser.parse_args()


@timeit
def main(args):
    cml_id = "developer"
    cml_pw = "C1sco12345"
    cml_url = "https://10.10.20.161"
    lab_title = "TWO_CSR1kv"
    cml = ClientLibrary(cml_url, cml_id, cml_pw, allow_http=False, ssl_verify=False)

    # clean the same title lab
    if cml.find_labs_by_title(lab_title):
        for lab_obj in cml.find_labs_by_title(lab_title):
            lab_id = lab_obj.id
            lab = cml.join_existing_lab(lab_id)
            lab.stop()
            lab.wipe()
            lab.remove()
        print("Finish cleaning up lab")

    lab = cml.import_lab_from_path(args.config, title=lab_title)
    lab.start()


if __name__ == "__main__":
    main(parseArgs())
