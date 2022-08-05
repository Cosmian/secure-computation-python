from cosmian_secure_computation_client.util.run_py import validate_run_py, IMPORT_TEMPLATE, IF_MAIN_TEMPLATE, ENTRYPOINT_TEMPLATE

from keys import *

import pytest


def test_valid_runpy():
    validate_run_py("tests/data/cp/enclave-join/run.py")
    assert True


def test_invalid_noimport_runpy():
    with pytest.raises(Exception) as context:
        validate_run_py("tests/data/cp/unit-test/noimport.py")

    assert str(context.value).endswith(IMPORT_TEMPLATE)


def test_invalid_nowith_runpy():
    with pytest.raises(Exception) as context:
        validate_run_py("tests/data/cp/unit-test/nowith.py")

    assert str(context.value).endswith(ENTRYPOINT_TEMPLATE)


def test_invalid_noifmain_runpy():
    with pytest.raises(Exception) as context:
        validate_run_py("tests/data/cp/unit-test/noifmain.py")

    assert str(context.value).endswith(IF_MAIN_TEMPLATE)


def test_invalid_extrastatement_runpy():
    with pytest.raises(Exception) as context:
        validate_run_py("tests/data/cp/unit-test/extrastatement.py")

    assert str(context.value).endswith(ENTRYPOINT_TEMPLATE)


def test_invalid_noreturn_runpy():
    with pytest.raises(Exception) as context:
        validate_run_py("tests/data/cp/unit-test/noreturn.py")

    assert str(context.value).endswith(ENTRYPOINT_TEMPLATE)


def test_invalid_extraifmain_runpy():
    with pytest.raises(Exception) as context:
        validate_run_py("tests/data/cp/unit-test/extraifmain.py")

    assert str(context.value).endswith(IF_MAIN_TEMPLATE)


def test_invalid_badifmain_runpy():
    with pytest.raises(Exception) as context:
        validate_run_py("tests/data/cp/unit-test/badifmain.py")

    assert str(context.value).endswith(IF_MAIN_TEMPLATE)