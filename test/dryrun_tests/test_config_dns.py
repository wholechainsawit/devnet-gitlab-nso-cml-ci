# pylint: disable=invalid-name
"""Pytest for testing commit dry-run"""
import logging
import pytest
from nso_restconf_call import NsoRestconfCall

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def test_config_dns(update_flag):
    payload = "payload/dns.json"
    expected = "expected/dns.dryrun.output"

    nso = NsoRestconfCall()
    assert nso.post_dry_run_verify(
        payload, expected, update_flag
    ), "dry-run and expected not matched"
