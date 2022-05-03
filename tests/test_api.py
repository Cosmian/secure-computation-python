import pytest

from cosmian_secure_computation_client.api.side import Side

from keys import *


@pytest.mark.incremental
class TestAPI:
    @staticmethod
    def create_computation(code_provider):
        assert True is True

    # def test_first_status(self, code_provider):
    #     assert code_provider.status() == {"pub_keys": {}}

    # @staticmethod
    # def test_hello(code_provider,
    #                data_provider1,
    #                data_provider2,
    #                result_consumer):
    #     assert "success" in code_provider.hello()
    #     assert "success" in data_provider1.hello()
    #     assert "success" in data_provider2.hello()
    #     assert "success" in result_consumer.hello()

    # @staticmethod
    # def test_cp_upload(code_provider, code_path):
    #     response = code_provider.upload(
    #         dir_path=code_path,
    #         exceptions=None,
    #         encrypt=True
    #     )

    #     assert "success" in response

    # def test_status(self, code_provider):
    #     response = code_provider.status()

    #     assert "pub_keys" in response

    #     pubkeys = response["pub_keys"]

    #     assert pubkeys == {
    #         Side.CodeProvider: [CP_PUBKEY],
    #         Side.DataProvider: [DP1_PUBKEY, DP2_PUBKEY],
    #         Side.ResultConsumer: [RC_PUBKEY]
    #     }

    # def test_key_finalize(self,
    #                       code_provider,
    #                       data_provider1,
    #                       data_provider2,
    #                       result_consumer):
    #     cp_resp = code_provider.key_finalize()

    #     assert "pub_key" in cp_resp
    #     assert "side" in cp_resp
    #     assert cp_resp["side"] == Side.Enclave

    #     dp1_resp = data_provider1.key_finalize()

    #     assert "pub_key" in dp1_resp
    #     assert "side" in dp1_resp
    #     assert dp1_resp["side"] == Side.Enclave

    #     dp2_resp = data_provider2.key_finalize()

    #     assert "pub_key" in dp2_resp
    #     assert "side" in dp2_resp
    #     assert dp2_resp["side"] == Side.Enclave

    #     rc_resp = result_consumer.key_finalize()

    #     assert "pub_key" in rc_resp
    #     assert "side" in rc_resp
    #     assert rc_resp["side"] == Side.Enclave

    #     assert (cp_resp["pub_key"] == dp1_resp["pub_key"] ==
    #             dp2_resp["pub_key"] == rc_resp["pub_key"])

    # def test_dp_upload(self,
    #                    data_provider1,
    #                    dp1_root_path,
    #                    data_provider2,
    #                    dp2_root_path,
    #                    code_name):
    #     assert data_provider1.push_files(code_name,
    #                                      dp1_root_path.glob("*.csv"))
    #     assert data_provider1.list_data(code_name) == {"data": ["A.csv.enc"], "total": 1}
    #     assert data_provider2.push_files(code_name,
    #                                      dp2_root_path.glob("*.csv"))
    #     assert data_provider2.list_data(code_name) =={"data": ["B.csv.enc"], "total": 1}

    # @staticmethod
    # def test_key_provisioning(code_provider,
    #                           data_provider1,
    #                           data_provider2,
    #                           result_consumer):
    #     assert "success" in code_provider.key_provisioning()
    #     assert "success" in data_provider1.key_provisioning()
    #     assert "success" in data_provider2.key_provisioning()
    #     assert "success" in result_consumer.key_provisioning()

    # @staticmethod
    # def test_run(result_consumer, rc_root_path, code_name):
    #     assert result_consumer.run(code_name)

    #     result = result_consumer.fetch_result(code_name)
    #     assert result is not None
    #     assert result == (rc_root_path / "result.csv").read_bytes()
