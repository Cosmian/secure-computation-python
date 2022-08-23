"""cosmian_secure_computation_client.participant.code_provider module."""

from pathlib import Path
import tempfile
from typing import List, Optional, Set

import requests

from cosmian_secure_computation_client.api.provider import upload_code, reset_code
from cosmian_secure_computation_client.util.fs import tar
from cosmian_secure_computation_client.participant.base import BaseAPI
from cosmian_secure_computation_client.side import Side
from cosmian_secure_computation_client.crypto.context import CryptoContext
from cosmian_secure_computation_client.util.entrypoint import validate_entrypoint


class CodeProviderAPI(BaseAPI):
    """CodeProviderAPI class derived from BaseAPI.

    Parameters
    ----------
    token : str
        Refresh token to authenticate with Cosmian's backend.
    ctx : CryptoContext
        Context with cryptographic secrets.

    """

    def __init__(self, token: str, ctx: CryptoContext) -> None:
        """Init constructor of CodeProviderAPI."""
        if ctx.side != Side.CodeProvider:
            raise Exception(
                f"Can't create {self.__class__} with CryptoContext side {ctx.side}"
            )
        super().__init__(token, ctx)

    def upload_code(self,
                    computation_uuid: str,
                    directory_path: Path,
                    patterns: Optional[List[str]] = None,
                    file_exceptions: Optional[List[str]] = None,
                    dir_exceptions: Optional[List[str]] = None) -> Path:
        """Send your Python code encrypted on a specific `computation_uuid`."""
        if not (directory_path / "run.py").exists():
            raise FileNotFoundError("Entrypoint 'run.py' not found!")

        self.log.debug("Checking run.py content...")
        validate_entrypoint(directory_path / "run.py")

        enc_directory_path: Path = (Path(tempfile.gettempdir()) / "cscc" /
                                    f"{computation_uuid}" / directory_path.name)

        self.log.debug("Encrypt code in %s to %s...", directory_path,
                       enc_directory_path)

        whitelist: Set[str] = {"run.py", "requirements.txt"}
        self.ctx.encrypt_directory(
            dir_path=directory_path,
            patterns=(["*"] if patterns is None else patterns),
            exceptions=(list(whitelist) if file_exceptions is None else
                        list(set(file_exceptions) | whitelist)),
            dir_exceptions=([] if dir_exceptions is None else dir_exceptions),
            out_dir_path=enc_directory_path)
        tar_path = tar(dir_path=enc_directory_path,
                       tar_path=enc_directory_path /
                       f"{enc_directory_path.name}.tar")
        self.log.debug("Tar encrypted code in '%s'", tar_path.name)

        r: requests.Response = upload_code(conn=self.conn,
                                           computation_uuid=computation_uuid,
                                           tar_path=tar_path)

        self.log.info("Encrypted code '%s' sent", tar_path.name)

        if not r.ok:
            raise Exception(
                f"Unexpected response ({r.status_code}): {r.content!r}")

        return tar_path

    def reset(self, computation_uuid: str) -> None:
        """Delete the Python code of `computation_uuid` on Cosmian's backend."""
        self.log.info("Reset code sent")
        r: requests.Response = reset_code(conn=self.conn,
                                          computation_uuid=computation_uuid)

        if not r.ok:
            raise Exception(
                f"Unexpected response ({r.status_code}): {r.content!r}")
