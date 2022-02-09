from cosmian_client_sgx.api.side import Side

import pytest


@pytest.mark.incremental
class TestAPI:
    @staticmethod
    def test_reset_first(result_owner, algo_name):
        assert result_owner.reset(algo_name=algo_name) is True

    @staticmethod
    def test_ap_handshake(algo_provider):
        response = algo_provider.handshake()

        assert "pub_key" in response and "side" in response
        assert response["side"] == Side.Enclave
        assert response["pub_key"] == bytes.fromhex("6f87e3130637e00d87e2aaca20361c0f58ef4db4113718a4a6dd7009569e3505")
