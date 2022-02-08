import pytest


@pytest.mark.incremental
class TestAPI:
    @staticmethod
    def test_reset_first(result_owner, algo_name):
        assert result_owner.reset(algo_name=algo_name) is True

    # @staticmethod
    # def test_ap_handshake(algo_provider):
    #     response = algo_provider.handshake()
    #     print(response)
