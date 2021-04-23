"""Utility tools"""
import logging
from pathlib import Path


def prep_payload_matched_output(cur_test_location, output_suffix):
    """Prepare the payload and expected files matching

    assume this current test file has same level directories as, payload/ and
    expected/ which store json payloads and expected results
    sample payload file is payload/ntp.json
    sample expected output is expected/ntp.dryrun.output
    output_suffix can be ".dryrun.output" or ".config.output"

    Args:
        cur_test_location (str): current test file location
        output_suffix (str): the added suffix of payload for matching expected output

    Returns:
        A list of tuples. In each tuple, (path to payload, path to expected output)
    """

    payload = glob_payload(cur_test_location)
    return list(
        zip(payload, find_matching_output(payload, cur_test_location, output_suffix))
    )


def glob_payload(cur_test):
    """Glob all the payload files in the payload/"""
    payload_files = []
    for json in cur_test.parent.glob("payload/*.json"):
        payload_files.append(str(json))
    logging.debug(payload_files)
    return payload_files


def find_matching_output(payload_files, cur_test, output_suffix):
    """Find the matching expected ouputs"""
    cur_dir = cur_test.parent
    expected_files = []
    for file in payload_files:
        expected_files.append(
            str(cur_dir / "expected" / (Path(file).stem + output_suffix))
        )
    logging.debug(expected_files)
    return expected_files
