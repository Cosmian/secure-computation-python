"""cosmian_client_sgx.api.side module."""

from enum import Enum


class Side(Enum):
    Enclave = 1
    AlgoProvider = 2
    DataProvider = 3
    ResultOwner = 4

    def __str__(self) -> str:
        return f"{self.name}"
