"""cosmian_client_sgx.api.side module."""

from enum import Enum


class Side(Enum):
    Enclave = 1
    CodeProvider = 2
    DataProvider = 3
    ResultConsumer = 4

    def __str__(self) -> str:
        return f"{self.name}"
