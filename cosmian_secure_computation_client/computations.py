"""cosmian_secure_computation_client.computations module."""

from dataclasses import dataclass
from typing import Optional, Dict, List
from enum import Enum

import inspect


class Role(Enum):
    """Subdict in Computation.my_roles."""

    ComputationOwner = "ComputationOwner"
    CodeProvider = "CodeProvider"
    DataProvider = "DataProvider"
    ResultConsumer = "ResultConsumer"

    def __str__(self) -> str:
        """Use name for string representation."""
        return f"{self.name}"


@dataclass(frozen=True)
class PublicKey:
    """Subdict in Computation.enclave.identity.public_key."""

    fingerprint: bytes
    content: str
    uploaded_at: str

    @staticmethod
    def from_json_dict(json):
        """Construct dataclass from dict."""
        return construct_dataclass(PublicKey, json)


@dataclass(frozen=True)
class Owner:
    """Subdict in Computation.owner."""

    uuid: str
    email: str

    @staticmethod
    def from_json_dict(json):
        """Construct dataclass from dict."""
        return construct_dataclass(Owner, json)


@dataclass(frozen=True)
class CodeProvider:
    """Subdict in Computation.code_provider."""

    uuid: str
    email: str
    public_key: Optional[PublicKey]
    code_uploaded_at: Optional[str]
    symmetric_key_uploaded_at: Optional[str]

    @staticmethod
    def from_json_dict(json):
        """Construct dataclass from dict."""
        json['public_key'] = (None if json['public_key'] is None else
                              PublicKey.from_json_dict(json['public_key']))

        return construct_dataclass(CodeProvider, json)


@dataclass(frozen=True)
class DataProvider:
    """Subdict in Computation.data_providers."""

    uuid: str
    email: str
    public_key: Optional[PublicKey]
    starting_uploading_at: Optional[str]
    done_uploading_at: Optional[str]
    symmetric_key_uploaded_at: Optional[str]

    @staticmethod
    def from_json_dict(json):
        """Construct dataclass from dict."""
        json['public_key'] = (None if json['public_key'] is None else
                              PublicKey.from_json_dict(json['public_key']))

        return construct_dataclass(DataProvider, json)


@dataclass(frozen=True)
class ResultConsumer:
    """Subdict in Computation.result_consumers."""

    uuid: str
    email: str
    public_key: Optional[PublicKey]
    symmetric_key_uploaded_at: Optional[str]
    result_downloaded_at: Optional[str]

    @staticmethod
    def from_json_dict(json):
        """Construct dataclass from dict."""
        json['public_key'] = (None if json['public_key'] is None else
                              PublicKey.from_json_dict(json['public_key']))

        return construct_dataclass(ResultConsumer, json)


@dataclass(frozen=True)
class EnclaveIdentity:
    """Subdict in Computation.enclave.identity."""

    public_key: bytes
    # Some endpoints omit the manifest in the response for performance reasons,
    # please call `get_computation()` to fetch it
    manifest: Optional[str]
    quote: str

    @staticmethod
    def from_json_dict(json):
        """Construct dataclass from dict."""
        json['public_key'] = bytes(json['public_key'])

        return construct_dataclass(EnclaveIdentity, json)


@dataclass(frozen=True)
class Enclave:
    """Subdict in Computation.enclave."""

    identity: Optional[EnclaveIdentity]

    @staticmethod
    def from_json_dict(json):
        """Construct dataclass from dict."""
        if json['identity'] is not None:
            json['identity'] = EnclaveIdentity.from_json_dict(json['identity'])

        return construct_dataclass(Enclave, json)


@dataclass(frozen=True)
class Run:
    """Subdict in Computation.run."""

    uuid: str
    created_at: str
    ended_at: str
    exit_code: int
    output: str
    results_fetches_datetimes_by_result_consumers_uuid: Dict[str, str]

    @staticmethod
    def from_json_dict(json):
        """Construct dataclass from dict."""
        return construct_dataclass(Run, json)


class EnclaveStateType(Enum):
    """State enum of an enclave."""

    Init = "Init"
    IdentityProcessing = "IdentityProcessing"
    SetupInput = "SetupInput"
    Running = "Running"
    Success = "Success"
    Failure = "Failure"

    def __str__(self) -> str:
        """Use name for string representation."""
        return f"{self.name}"


@dataclass(frozen=True)
class EnclaveState:
    """State of the computation enclave."""

    state: EnclaveStateType
    inner: Optional[dict]

    @staticmethod
    def from_json_dict(json):
        """Construct dataclass from dict."""
        if isinstance(json, dict):
            state = next(iter(json))
            return EnclaveState(EnclaveStateType[state], json[state])
        return EnclaveState(EnclaveStateType[json], None)


class ComputationStatusType(Enum):
    """State enum of a computation."""

    NotStarted = "NotStarted"
    Archived = "Archived"
    Removed = "Removed"
    Started = "Started"


@dataclass(frozen=True)
class ComputationStatus:
    """Status of the computation."""

    status: ComputationStatusType
    enclave_state: Optional[EnclaveState]

    def has_enclave_identity(self) -> bool:
        """Check if the status means that the computation has an identity."""
        if self.status != ComputationStatusType.Started:
            return False

        if not self.enclave_state:
            return False

        enclave_state: EnclaveState = self.enclave_state

        return enclave_state.state not in (EnclaveStateType.Init,
                                           EnclaveStateType.IdentityProcessing)

    def has_result(self) -> bool:
        """Check if the status means that the computation has an run result."""
        if self.status != ComputationStatusType.Started:
            return False

        if not self.enclave_state:
            return False

        enclave_state: EnclaveState = self.enclave_state

        return enclave_state.state in (EnclaveStateType.Success,
                                       EnclaveStateType.Failure)

    @staticmethod
    def from_json_dict(json):
        """Construct dataclass from dict."""
        if isinstance(json, dict):
            state = next(iter(json))
            return ComputationStatus(ComputationStatusType[state],
                                     EnclaveState.from_json_dict(json[state]))

        return ComputationStatus(ComputationStatusType[json], None)


@dataclass(frozen=True)
class Computation:
    """Computation dataclass representing JSON response."""

    uuid: str
    name: str
    owner: Owner
    code_provider: CodeProvider
    data_providers: List[DataProvider]
    result_consumers: List[ResultConsumer]
    enclave: Enclave
    runs: List[Run]
    my_roles: List[Role]
    created_at: str

    @staticmethod
    def from_json_dict(json):
        """Construct dataclass from dict."""
        json['owner'] = Owner.from_json_dict(json['owner'])
        json['code_provider'] = CodeProvider.from_json_dict(
            json['code_provider'])
        json['data_providers'] = list(
            map(DataProvider.from_json_dict, json['data_providers']))
        json['result_consumers'] = list(
            map(ResultConsumer.from_json_dict, json['result_consumers']))
        json['enclave'] = Enclave.from_json_dict(json['enclave'])
        json['runs'] = list(map(Run.from_json_dict, json['runs']))
        json['my_roles'] = list(map(Role, json['my_roles']))

        return construct_dataclass(Computation, json)


def construct_dataclass(dc, json):
    """Dataclass builder."""
    sig = inspect.signature(dc)
    filter_keys = [
        param.name
        for param in sig.parameters.values()
        if param.kind == param.POSITIONAL_OR_KEYWORD
    ]
    filtered_dict = {
        filter_key: json.get(filter_key, None) for filter_key in filter_keys
    }
    return dc(**filtered_dict)
