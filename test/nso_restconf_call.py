""" Module for dealing with NSO northbound REST api calls """
from pathlib import Path
from datetime import datetime
import logging
import json
import subprocess
import filecmp
import shutil
import re
import requests
import config_trie

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def make_config_into_trie(filename):
    t = config_trie.Trie()
    with open(filename) as f:
        content = f.readlines()
    # remove only line ending return, NOT leading space
    content = [x.rstrip() for x in content]
    context = ""
    for line in content:
        # skip emtpy line and line started with "!"
        if line == "" or re.search(r'^\s*!', line):
            continue

        # print(line)
        # have a space at the front
        # TODO: if multiple levels
        if re.search(r'^\s', line):
            line_with_context = context + " _next_  " + line
            t.insert(line_with_context)
        else:
            context = line
            t.insert(line)
    return t


def config_trie_to_file(outfile, config_list):
    with open(outfile, 'w') as f:
        for line in config_list:
            if "_next_" in line:
                sections = line.split(" _next_ ")
                # TODO: take care of multi-layers
                f.write(" %s\n" % sections[1])
            else:
                f.write("%s\n" % line.rstrip())


class NsoRestconfCall:
    """
    A Class used to deal with NSO northbound REST api calls
    """

    def __init__(self, ip="127.0.0.1", port="80", user="admin", pwd="admin"):
        """
        Args:
            ip (str): IP address of the NSO (default is localhost)
            port (str): the port for connecting NSO restconf
            user (str): username to log into the NSO
            pwd (str): password to log into the NSO
        """
        self.port = port
        self.ip = ip
        self.auth = (user, pwd)

    def __del__(self):
        pass

    def _check_restconf_call_return(self, resp):
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            logger.debug(f'HTTP error occurred: {http_err}')
            logger.debug(json.dumps(resp.json(), sort_keys=True, indent=4))
            # raise Exception(f'HTTP error occurred: {http_err}')
        except Exception as err:
            logger.debug(f'Non HTTPError: {err}')
            logger.debug(json.dumps(resp.json(), sort_keys=True, indent=4))
            # raise Exception(f'Non HTTPError: {err}')
        # code = resp.status_code
        # if code >= 400:
        #     logger.debug(json.dumps(resp.json(), sort_keys=True, indent=4))

    def rollback_n_commit(self, num):
        """ To rollback number of commits

        Since in NSO, the commit file starts with 0. For example, to roll back the
        latest commit, 0 is used.

        Args:
            num: the number of commits to rollback
        """

        url = "http://" + self.ip + ":" + self.port + "/restconf/data/tailf-rollback:rollback-files/apply-rollback-file"
        header = {
            "content-type": "application/yang-data+xml"
        }
        resp = requests.post(
            url, data="<id>" + str(num) + "</id>", headers=header, auth=self.auth
        )
        self._check_restconf_call_return(resp)
        logger.debug(resp.text)

    # the latest rollback is always the file 0
    def rollback_latest_commit(self):
        """To roll back the latest commit"""
        self.rollback_n_commit(0)

    def get_rollback_set(self):
        """ Get the set of rollback files """
        resp = self.get("/restconf/data/tailf-rollback:rollback-files")
        rollback_sets = set()
        for rollback in resp.json()["tailf-rollback:rollback-files"]["file"]:
            rollback_sets.add(int(rollback["id"]))
        # logging.debug("%d: Current rollback set is %s", len(rollback_sets), rollback_sets)
        logging.debug("Total %d rollback files", len(rollback_sets))
        return rollback_sets

    def dev_compare_config(self, dev):
        """Do the devices device compare-config action

        Args:
            dev (str): the name of the device in NSO

        Returns:
            resp (requests return obj):
        """

        url = "http://" + self.ip + ":" + self.port + "/restconf/data/tailf-ncs:devices/device=" + dev + "/compare-config"
        header = {
            "content-type": "application/yang-data+json",
            "Accept": "application/yang-data+json"
        }
        resp = requests.post(url, headers=header, auth=self.auth)
        self._check_restconf_call_return(resp)
        return resp

    def post_services(self, payload, para=""):
        """Post(create) the NSO service

        Args:
            payload (str or Path): the path to the payload
            para (str): the query parameters

        Returns:
            resp (requests return obj):
        """

        url = "http://" + self.ip + ":" + self.port + "/restconf/data/tailf-ncs:services" + para
        header = {
            "content-type": "application/yang-data+json",
            "Accept": "application/yang-data+json"
        }
        # send payload to the service in the json file
        with open(payload) as json_file:
            json_data = json.load(json_file)
        resp = requests.post(url, json=json_data, headers=header, auth=self.auth)
        self._check_restconf_call_return(resp)
        return resp

    def post_live_status(self, device, cmd, dev_type="ios"):
        """Execute live-status command through NSO

        Args:
            device (string): the device name in the NSO
            cmd (str): the command past to the device via NSO

        Returns:
            resp (requests return obj):
        """

        if dev_type == "ios":
            url = "http://" + self.ip + ":" + self.port + "/restconf/data/tailf-ncs:devices/device=" + device + "/live-status/tailf-ned-cisco-ios-stats:exec/any" 
        elif dev_type == "nx":
            url = "http://" + self.ip + ":" + self.port + "/restconf/data/tailf-ncs:devices/device=" + device + "/live-status/tailf-ned-cisco-nx-stats:exec/any" 
        elif dev_type == "xr":
            url = "http://" + self.ip + ":" + self.port + "/restconf/data/tailf-ncs:devices/device=" + device + "/live-status/tailf-ned-cisco-ios-xr-stats:exec/any" 
        header = {
            "content-type": "application/yang-data+json",
            "Accept": "application/yang-data+json"
        }
        action_input = '{"input":{"args":"' + cmd + '"}}'
        resp = requests.post(
            url, data=action_input, headers=header, auth=self.auth
        )
        self._check_restconf_call_return(resp)
        return resp

    def post(self, url, data="", para=""):
        """Post to NSO

        Args:
            url (str): the path to the NSO resource
            data (obj): A dictionary, list of tuples, bytes or a file object
            para (str): the query parameters

        Returns:
            resp (requests return obj):
        """

        url = "http://" + self.ip + ":" + self.port + url + para
        header = {
            "content-type": "application/yang-data+json",
            "Accept": "application/yang-data+json"
        }
        resp = requests.post(url, data=data, headers=header, auth=self.auth)
        self._check_restconf_call_return(resp)
        return resp

    def update(self, url, payload):
        """Update the service

        Args:
            url (str): the path the service that will be updated
            payload (str or Path): the path to the payload

        Returns:
            resp (requests return obj):
        """

        url = "http://" + self.ip + ":" + self.port + url
        header = {"content-type": "application/yang-data+json"}
        # send payload to the service in the json file
        with open(payload) as json_file:
            json_data = json.load(json_file)
        resp = requests.put(url, json=json_data, headers=header, auth=self.auth)
        self._check_restconf_call_return(resp)
        return resp

    def patch(self, url, payload):
        """Update the service

        Args:
            url (str): the path the service that will be updated
            payload (str or Path): the path to the payload

        Returns:
            resp (requests return obj):
        """

        url = "http://" + self.ip + ":" + self.port + url
        header = {"content-type": "application/yang-data+json"}
        # send payload to the service in the json file
        with open(payload) as json_file:
            json_data = json.load(json_file)
        resp = requests.patch(url, json=json_data, headers=header, auth=self.auth)
        self._check_restconf_call_return(resp)
        return resp

    def get(self, url):
        """Query the info a certain NSO path

        Args:
            url (str): the path to the NSO resource

        Returns:
            resp (requests return obj):
        """

        url = "http://" + self.ip + ":" + self.port + url
        header = {
            "content-type": "application/yang-data+json",
            "Accept": "application/yang-data+json"
        }
        resp = requests.get(url, headers=header, auth=self.auth)
        logger.debug(json.dumps(resp.json(), sort_keys=True, indent=4))
        self._check_restconf_call_return(resp)
        return resp

    def delete(self, url):
        """Delete the instance of a certain NSO path

        Args:
            url (str): the path to the NSO resource

        Returns:
            resp (requests return obj):
        """

        url = "http://" + self.ip + ":" + self.port + url
        header = {
            "content-type": "application/yang-data+json",
            "Accept": "application/yang-data+json"
        }
        resp = requests.delete(url, headers=header, auth=self.auth)
        self._check_restconf_call_return(resp)
        return resp

    @classmethod
    def trans_to_abs_path(cls, payload, expected, cur_file):
        """Translate payload and expect into Path objects

        Translate the input payload and expect path into Path. Based on the inputs,
        turn the relative paths into absolute path

        Args:
            payload (str): the path str, either relateive or absolute to the payload
            expected (str): the path str, either relateive or absolute to the expected
                output
            cur_file (str): the current test file
        Returns:
            payload, expcted Path objects
        """

        if not Path(payload).is_absolute():
            payload = Path(cur_file).parent.joinpath(payload)
        else:
            payload = Path(payload)
        if not Path(expected).is_absolute():
            expected = Path(cur_file).parent.joinpath(expected)
        else:
            expected = Path(expected)
        return payload, expected


    def convert_to_abs_path(self, fname, cur_file):
        if not Path(fname).is_absolute():
            abs_path_fname = Path(cur_file).parent.joinpath(fname)
        else:
            abs_path_fname = Path(fname)
        return abs_path_fname


    def commit_payload(self, payload, cur_file="."):
        payload = self.convert_to_abs_path(payload, cur_file)

        if not payload.exists():
            logger.error("Payload %s not found", payload)
            return False

        self.post_services(payload)

    def one_commit_verify(self, payload, expected, dev, cmd, update=False, cur_file="."):
        """Post a service and verify it with the given device config

        Args:
            payload (str): the path str, either relateive or absolute to the payload
            expected (str): the path str, either relateive or absolute to the expected
                output
            dev (str): name of device to get the device config
            cmd (str): the command that runs on the device and get the return string
            update (boolean): update the expected output or not
            cur_file (str): the current test file

        Returns:
            (boolean): if the testing output is the same as the expected output
        """

        # payload, expected = self.trans_to_abs_path(payload, expected, cur_file)
        # if not payload.exists():
        #     logger.error("Payload %s not found", payload)
        #     return False
        # self.post_services(payload)
        # resp = self.post_live_status(dev, cmd)
        # return self._write_commit_compare_update(resp, expected, update)

    def write_ios_show_run_config(self, resp, expected, update, cur_file="."):
        # write the REST response output
        expected = self.convert_to_abs_path(expected, cur_file)
        now = datetime.now()
        timestamp = now.strftime('%Y%m%d-%H%M%S.%f')
        commit_result_file = "/tmp/raw_show_run.output." + timestamp
        # commit_result_file = expected.parent / "raw_show_run.output"
        with open(commit_result_file, "w") as f:
            # formated_json = json.dumps(resp.json()["tailf-ned-cisco-ios-stats:output"]["result"], sort_keys=True, indent=4).replace("\\r\\n", "\n")
            formated_json = json.dumps(resp.json(), sort_keys=True, indent=4).replace("\\r\\n", "\n")
            # only take the config between "version ..." and "end"
            re_result = re.search(r"version .*end", formated_json, re.DOTALL)
            if re_result:
                no_head_tail_str = re_result.group()
            else:
                raise Exception("Config between version:.... and end NOT found")
            ## TODO: fix the filtering hack
            mask_pwd_json = re.sub(r'\$(5|8|9)\$\S+', '[SECRET]', no_head_tail_str)
            mask_pwd_json = re.sub(r'password 7 \S+', 'password 7 [SECRET]', mask_pwd_json)
            mask_pwd_json = re.sub(r'key 7 \S+', 'key 7 [SECRET]', mask_pwd_json)
            f.write(mask_pwd_json)

        logger.debug(f"Wrote the raw device show run output to {commit_result_file}")
        return commit_result_file

    def write_nx_show_run_config(self, resp, expected, update, cur_file="."):
        # write the REST response output
        expected = self.convert_to_abs_path(expected, cur_file)
        now = datetime.now()
        timestamp = now.strftime('%Y%m%d-%H%M%S.%f')
        commit_result_file = "/tmp/raw_show_run.output." + timestamp
        # commit_result_file = expected.parent / "raw_show_run.output"
        with open(commit_result_file, "w") as f:
            formated_json = json.dumps(resp.json()["tailf-ned-cisco-nx-stats:output"]["result"], sort_keys=True, indent=4).replace("\\r\\n", "\n")
            # formated_json = json.dumps(resp.json(), sort_keys=True, indent=4).replace("\\r\\n", "\n")
            formated_json = re.sub(r'(\\r"|"\\r)', '', formated_json)
            mask_pwd_json = re.sub(r'\$(5|8|9)\$\S+', '[SECRET]', formated_json)
            mask_pwd_json = re.sub(r'password 7 \S+', 'password 7 [SECRET]', mask_pwd_json)
            mask_pwd_json = re.sub(r'key 7 \S+', 'key 7 [SECRET]', mask_pwd_json)
            mask_pwd_json = re.sub(r'0x\S+', '[SECRET]', mask_pwd_json)
            f.write(mask_pwd_json)

        logger.debug(f"Wrote the raw device show run output to {commit_result_file}")
        return commit_result_file

    def write_xr_show_run_config(self, resp, expected, update, cur_file="."):
        # write the REST response output
        expected = self.convert_to_abs_path(expected, cur_file)
        now = datetime.now()
        timestamp = now.strftime('%Y%m%d-%H%M%S.%f')
        commit_result_file = "/tmp/raw_show_run.output." + timestamp
        # commit_result_file = expected.parent / "raw_show_run.output"
        with open(commit_result_file, "w") as f:
            formated_json = json.dumps(resp.json()["tailf-ned-cisco-ios-xr-stats:output"]["result"], sort_keys=True, indent=4).replace("\\r\\n", "\n")
            # only take the config between "Building configuration..." and "end"
            re_result = re.search(r"Building configuration....*end", formated_json, re.DOTALL)
            if re_result:
                no_head_tail_str = re_result.group()
            else:
                raise Exception("Config between Building configuration... and end NOT found")
            mask_pwd_json = re.sub(r'key 7 \S+', 'key 7 [SECRET]', no_head_tail_str)
            mask_pwd_json = re.sub(r'encrypted \S+', 'encrypted [SECRET]', mask_pwd_json)
            f.write(mask_pwd_json)

        logger.debug(f"Wrote the raw device show run output to {commit_result_file}")
        return commit_result_file

    def compare_two_configs(self, result, expected, ignore_config, cur_file="."):
        # TODO: need to see if result is a abs path
        expected = self.convert_to_abs_path(expected, cur_file)
        now = datetime.now()
        timestamp = now.strftime('%Y%m%d-%H%M%S.%f')
        # tran_golden_fname = expected.parent / "tran_golden"
        tran_golden_fname = "/tmp/tran_golden." + timestamp
        # tran_this_config_fname = expected.parent / "tran_this_config"
        tran_this_config_fname = "/tmp/tran_this_config." + timestamp

        gold = make_config_into_trie(expected)
        gold.remove_from_list(ignore_config)
        # gold.root.pop('Building', None)
        # del gold.root['license']

        this_config = make_config_into_trie(result)
        this_config.remove_from_list(ignore_config)

        # TODO: need to take care of the file path 
        config_trie_to_file(tran_golden_fname, gold.traverse_whole_trie())
        config_trie_to_file(tran_this_config_fname, this_config.traverse_whole_trie())

        # Not sure why the return whole tree not working
        # if gold.get_whole_trie == this_config.get_whole_trie:
        if gold.root == this_config.root:
            logger.debug("output and expected results are the same")
            is_output_as_expected = True
        else:
            subprocess.call(["diff", "-a", "--unified=5", tran_golden_fname, tran_this_config_fname])
            subprocess.call(["colordiff", "--unified=5", tran_golden_fname, tran_this_config_fname])
            subprocess.call(["icdiff", "-H", tran_golden_fname, tran_this_config_fname])
            is_output_as_expected = False
            is_output_as_expected = False

        return is_output_as_expected


    def overwrite_expected(self, result, expected, update=False, cur_file="."):
        result = self.convert_to_abs_path(result, cur_file)
        expected = self.convert_to_abs_path(expected, cur_file)

        if update:
            # overwrite expected_output with raw device show run
            shutil.copy(result, expected)
            logger.info("%s is updated.", expected)


    def post_dry_run_verify(self, payload, expected, update=False, cur_file="."):
        """Commit dryrun a service and verify it with the dryrun result

        Args:
            payload (str): the path str, either relateive or absolute to the payload
            expected (str): the path str, either relateive or absolute to the expected
                output
            update (boolean): update the expected output or not
            cur_file (str): the current test file

        Returns:
            (boolean): if the testing output is the same as the expected output
        """

        payload, expected = self.trans_to_abs_path(payload, expected, cur_file)
        if not payload.exists():
            logger.error("Payload %s not found", payload)
            return False
        resp = self.post_services(payload, "?dry-run=native")
        return self._write_rest_compare_update(resp, expected, update)

    # def compare_device_config_results_udpate(
    #     self, expected, update=False, cur_file="."  # pylint: disable=C0330
    # ):
        """Compare the devices config with the expected output

        Args:
            expected (str): the path str, either relateive or absolute to the expected
                output
            update (boolean): update the expected output or not
            cur_file (str): the current test file

        Returns:
            (boolean): if the testing output is the same as the expected output
        """
        # if not Path(expected).is_absolute():
        #     expected = Path(cur_file).parent.joinpath(expected)
        # else:
        #     expected = Path(expected)
        # resp = self.get("/api/running/devices/device")
        # return self._write_rest_compare_update(resp, expected, update)

    def _write_rest_compare_update(self, resp, expected, update):
        # write the REST response output
        now = datetime.now()
        timestamp = now.strftime('%Y%m%d-%H%M%S.%f')
        dry_run_file = "/tmp/dryrun.output." + timestamp
        # dry_run_file = expected.parent / "restconf_output"
        logger.debug(f"RESTCONF dryrun output to {dry_run_file}")
        with open(dry_run_file, "w") as f:
            formated_json = json.dumps(resp.json(), sort_keys=True, indent=4).replace("\\n", "\n")
            ## TODO: fix the filtering hack
            mask_pwd_json = re.sub(r'\$(5|8|9)\$\S+', '[SECRET]', formated_json)
            mask_pwd_json = re.sub(r'password 7 \S+', 'password 7 [SECRET]', mask_pwd_json)
            f.write(mask_pwd_json)
        return self._compare_results_update(dry_run_file, expected, update)

    @staticmethod
    def _compare_results_update(output, expected, update):
        if expected.exists() and filecmp.cmp(output, expected):
            logger.debug("output and expected results are the same")
            is_output_as_expected = True
        else:
            subprocess.call(["git", "--no-pager", "diff", "--no-index", "--word-diff", "-U10000", output, expected])
            is_output_as_expected = False

        if update:
            # overwrite expected_output with dry_run_output
            shutil.copy(output, expected)
            logger.info("%s is updated.", expected)

        return is_output_as_expected
