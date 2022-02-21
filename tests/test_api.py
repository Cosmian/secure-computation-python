from cosmian_client_sgx.api.side import Side

import pytest


@pytest.mark.incremental
class TestAPI:
    # @staticmethod
    # def test_reset_first(result_owner):
    #     assert result_owner.reset() is True

    def test_first_status(self, algo_provider):
        assert algo_provider.status() == {"pub_keys": {}}

    @staticmethod
    def test_ap_hello(algo_provider):
        response = algo_provider.hello()

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
    def test_ro_hello(result_owner):
        response = result_owner.hello()

        assert "success" in response

    def test_status(self, algo_provider):
        response = algo_provider.status()
        print(response)
        # assert response == {"pub_keys": {}}

    # @staticmethod
    # def test_ap_handshake(algo_provider):
    #     response = algo_provider.handshake()
    #
    #     assert "pub_key" in response and "side" in response
    #     assert response["side"] == Side.Enclave
    #     assert response["pub_key"] == bytes.fromhex("6f87e3130637e00d87e2aaca20361c0f58ef4db4113718a4a6dd7009569e3505")

    # @staticmethod
    # def test_ap_ra(algo_provider):
    #     quote = algo_provider.get_quote()
    #     print(quote)
    #     assert algo_provider.remote_attestation(quote) is True
