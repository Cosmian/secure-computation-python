from pathlib import Path
from typing import Dict, Tuple

import pytest

from cosmian_client_sgx import AlgoProviderAPI, DataProviderAPI, ResultOwnerAPI


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
def ap_root_path():
    return Path(__file__).parent / "data" / "ap"


@pytest.fixture(scope="module")
def algo_name():
    return (Path(__file__).parent / "data" / "ap" / "enclave-join").name


@pytest.fixture(scope="module")
def dp1_root_path():
    return Path(__file__).parent / "data" / "dp1"


@pytest.fixture(scope="module")
def dp2_root_path():
    return Path(__file__).parent / "data" / "dp2"


@pytest.fixture(scope="module")
def ro_root_path():
    return Path(__file__).parent / "data" / "ro"


@pytest.fixture(scope="module")
def algo_provider(host, port, ssl):
    ap = AlgoProviderAPI(host, port, ssl)
    ap.set_keypair(
        public_key=bytes.fromhex("1f80306ddf75ee31bc8f71f29c93768bc6eaba2c1f67bcd7f179ca26d4361331"),
        private_key=bytes.fromhex("deb832a69e996898c835b9779c3a98cd3ba0b437a6aba94dacc33692154a815c")
    )

    yield ap


@pytest.fixture(scope="module")
def data_provider1(host, port, ssl):
    dp = DataProviderAPI(host, port, ssl)
    dp.set_keypair(
        public_key=bytes.fromhex("08278fc6860d83b598e54462e9c5c68e5eb0bff588de413a0e651a65dd540a29"),
        private_key=bytes.fromhex("dcd1512baa17cb7440078844f3c090dd86c7e3e948065cb6f037f3413b23873f")
    )

    yield dp


@pytest.fixture(scope="module")
def data_provider2(host, port, ssl):
    dp = DataProviderAPI(host, port, ssl)
    dp.set_keypair(
        public_key=bytes.fromhex("6b47b13b4fe3efa09334b079b4cd57ad5f263e4010325510c493cdccc3440b50"),
        private_key=bytes.fromhex("363f07b34144e9b095dfe38b797c6e6012e8d0752a8c621e6d809309e0d83d13")
    )

    yield dp


@pytest.fixture(scope="module")
def result_owner(host, port, ssl):
    ro = ResultOwnerAPI(host, port, ssl)
    ro.set_keypair(
        public_key=bytes.fromhex("bd2c17ec62bf8424fda8e36429be0d73f794fd64d92b57c17c17dccf76d6f62e"),
        private_key=bytes.fromhex("697d565f2b421e72635329aaa539fca57e8bc8eaf108ff0ce30e114981ad1f23")
    )

    yield ro


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
