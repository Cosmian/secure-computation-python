"""cosmian_client_sgx.api.computations module."""

from dataclasses import dataclass
from typing import Optional, Dict, Union, List, Tuple
from enum import Enum
from datetime import datetime

class Role(Enum):
    ComputationOwner = 'ComputationOwner'
    CodeProvider = 'CodeProvider'
    DataProvider = 'DataProvider'
    ResultConsumer = 'ResultConsumer'

    def __str__(self) -> str:
        return f"{self.name}"


@dataclass(frozen=True)
class PublicKey:
    fingerprint: bytes
    content: str
    uploaded_at: str

    @staticmethod
    def from_json_dict(json):
        return PublicKey(**json)

@dataclass(frozen=True)
class Owner:
    uuid: str
    email: str
    public_key: PublicKey
    manifest_signature: Optional[str]

    @staticmethod
    def from_json_dict(json):
        json['public_key'] = PublicKey.from_json_dict(json['public_key'])

        return Owner(**json)

@dataclass(frozen=True)
class CodeProvider:
    uuid: str
    email: str
    public_key: Optional[PublicKey]
    code_uploaded_at: Optional[str]
    symetric_key_uploaded_at: Optional[str]

    @staticmethod
    def from_json_dict(json):
        json['public_key'] = None if json['public_key'] is None else PublicKey.from_json_dict(json['public_key'])

        return CodeProvider(**json)

@dataclass(frozen=True)
class DataProvider:
    uuid: str
    email: str
    public_key: Optional[PublicKey]
    starting_uploading_at: Optional[str]
    done_uploading_at: Optional[str]
    symetric_key_uploaded_at: Optional[str]

    @staticmethod
    def from_json_dict(json):
        json['public_key'] = None if json['public_key'] is None else PublicKey.from_json_dict(json['public_key'])

        return DataProvider(**json)

@dataclass(frozen=True)
class ResultConsumer:
    uuid: str
    email: str
    public_key: Optional[PublicKey]
    symetric_key_uploaded_at: Optional[str]
    result_downloaded_at: Optional[str]

    @staticmethod
    def from_json_dict(json):
        json['public_key'] = None if json['public_key'] is None else PublicKey.from_json_dict(json['public_key'])

        return ResultConsumer(**json)

@dataclass(frozen=True)
class Enclave:
    public_key: Optional[bytes]
    manifest: Optional[str]

    @staticmethod
    def from_json_dict(json):
        return Enclave(**json)

@dataclass(frozen=True)
class CurrentRun:
    created_at: str

    @staticmethod
    def from_json_dict(json):
        return CurrentRun(**json)

@dataclass(frozen=True)
class PreviousRun:
    created_at: str
    ended_at: str

    @staticmethod
    def from_json_dict(json):
        return PreviousRun(**json)


@dataclass(frozen=True)
class Runs:
    current: Optional[CurrentRun]
    previous: List[PreviousRun]

    @staticmethod
    def from_json_dict(json):
        json['current'] = None if json['current'] is None else CurrentRun.from_json_dict(json['current'])
        json['previous'] = list(map(PreviousRun.from_json_dict, json['previous']))

        return Runs(**json)


@dataclass(frozen=True)
class Computation:
    uuid: str #: The unique identifier for the computation, required to run most of the API endpoints.
    name: str #: User-defined name of the computation.
    owner: Owner #: Information about the computation owner.
    code_provider: CodeProvider #: Information about the computation provider.
    data_providers: List[DataProvider] #: Information about the data providers.
    result_consumers: List[ResultConsumer] #: Information about the result consumers.
    enclave: Enclave #: Information about the enclave. The enclave is the place where the code is running.
    runs: Runs #: List of the current and previous runs of this computation.
    my_roles: List[Role] #: List of your roles in this computation
    created_at: str #: Date of creation of the computation

    @staticmethod
    def from_json_dict(json):
        json['owner'] = Owner.from_json_dict(json['owner'])
        json['code_provider'] = CodeProvider.from_json_dict(json['code_provider'])
        json['data_providers'] = list(map(DataProvider.from_json_dict, json['data_providers']))
        json['result_consumers'] = list(map(ResultConsumer.from_json_dict, json['result_consumers']))
        json['enclave'] = Enclave.from_json_dict(json['enclave'])
        json['runs'] = Runs.from_json_dict(json['runs'])
        json['my_roles'] = list(map(Role, json['my_roles']))

        return Computation(**json)
