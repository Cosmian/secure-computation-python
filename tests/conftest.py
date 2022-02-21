from pathlib import Path
from typing import Dict, Tuple

import pytest
from cosmian_client_sgx import CodeProviderAPI, DataProviderAPI, ResultConsumerAPI

from keys import *


def pytest_addoption(parser):
    parser.addoption("--host",
                     action="store",
                     default="127.0.0.1")
    parser.addoption("--port",
                     action="store",
                     default=None)
    parser.addoption("--ssl",
                     action="store_true",
                     default=False)


@pytest.fixture(scope="session")
def host(pytestconfig):
    return pytestconfig.getoption("host")


@pytest.fixture(scope="session")
def port(pytestconfig):
    return pytestconfig.getoption("port")


@pytest.fixture(scope="session")
def ssl(pytestconfig):
    return pytestconfig.getoption("ssl")


@pytest.fixture(scope="module")
def cp_root_path():
    return Path(__file__).parent / "data" / "cp"


@pytest.fixture(scope="module")
def code_path():
    return Path(__file__).parent / "data" / "cp" / "enclave-join"


@pytest.fixture(scope="module")
def code_name():
    return (Path(__file__).parent / "data" / "cp" / "enclave-join").name


@pytest.fixture(scope="module")
def dp1_root_path():
    return Path(__file__).parent / "data" / "dp1"


@pytest.fixture(scope="module")
def dp2_root_path():
    return Path(__file__).parent / "data" / "dp2"


@pytest.fixture(scope="module")
def rc_root_path():
    return Path(__file__).parent / "data" / "rc"


@pytest.fixture(scope="module")
def code_provider(host, port, ssl):
    cp = CodeProviderAPI(host, port, ssl)
    cp.set_keypair(
        public_key=CP_PUBKEY,
        private_key=CP_PRIVKEY
    )
    cp.set_symkey(CP_SYMKEY)

    yield cp


@pytest.fixture(scope="module")
def data_provider1(host, port, ssl):
    dp = DataProviderAPI(host, port, ssl)
    dp.set_keypair(
        public_key=DP1_PUBKEY,
        private_key=DP1_PRIVKEY
    )
    dp.set_symkey(DP1_SYMKEY)

    yield dp


@pytest.fixture(scope="module")
def data_provider2(host, port, ssl):
    dp = DataProviderAPI(host, port, ssl)
    dp.set_keypair(
        public_key=DP2_PUBKEY,
        private_key=DP2_PRIVKEY
    )
    dp.set_symkey(DP2_SYMKEY)

    yield dp


@pytest.fixture(scope="module")
def result_consumer(host, port, ssl):
    rc = ResultConsumerAPI(host, port, ssl)
    rc.set_keypair(
        public_key=RC_PUBKEY,
        private_key=RC_PRIVKEY
    )
    rc.set_symkey(RC_SYMKEY)

    yield rc


_test_failed_incremental: Dict[str, Dict[Tuple[int, ...], str]] = {}


def pytest_runtest_makereport(item, call):
    if "incremental" in item.keywords:
        if call.excinfo is not None:
            cls_name = str(item.cls)
            parametrize_index = (
                tuple(item.callspec.indices.values())
                if hasattr(item, "callspec")
                else ()
            )
            test_name = item.originalname or item.name
            _test_failed_incremental.setdefault(cls_name, {}).setdefault(
                parametrize_index, test_name
            )


def pytest_runtest_setup(item):
    if "incremental" in item.keywords:
        cls_name = str(item.cls)
        if cls_name in _test_failed_incremental:
            parametrize_index = (
                tuple(item.callspec.indices.values())
                if hasattr(item, "callspec")
                else ()
            )
            test_name = _test_failed_incremental[cls_name].get(
                parametrize_index, None
            )
            if test_name is not None:
                pytest.xfail("previous test failed ({})".format(test_name))
