import pytest

from cosmian_client_sgx.api.side import Side

from keys import *


@pytest.mark.incremental
class TestAPI:
    @staticmethod
    def test_reset_first(code_provider):
        assert code_provider.reset() is True

    def test_first_status(self, code_provider):
        assert code_provider.status() == {"pub_keys": {}}

    @staticmethod
    def test_cp_hello(code_provider):
        response = code_provider.hello()

        assert "success" in response

    @staticmethod
    def test_dp1_hello(data_provider1):
        response = data_provider1.hello()

        assert "success" in response

    @staticmethod
    def test_dp2_hello(data_provider2):
        response = data_provider2.hello()

        assert "success" in response

    @staticmethod
    def test_rc_hello(result_consumer):
        response = result_consumer.hello()

        assert "success" in response

    def test_status(self, code_provider):
        response = code_provider.status()

        assert "pub_keys" in response

        pubkeys = response["pub_keys"]

        assert pubkeys[Side.CodeProvider][0] == CP_PUBKEY
        assert pubkeys[Side.DataProvider][0] == DP1_PUBKEY
        assert pubkeys[Side.DataProvider][1] == DP2_PUBKEY
        assert pubkeys[Side.ResultConsumer][0] == RC_PUBKEY
