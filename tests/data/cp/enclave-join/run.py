"""run module."""

from io import BytesIO
import struct
from typing import Iterator

from cosmian_lib_sgx import Enclave


def input_reader(datas: Iterator[BytesIO]) -> Iterator[float]:
    for data in datas:  # type: BytesIO
        x, *_ = struct.unpack("f", data)
        yield x


def main() -> int:
    with Enclave() as enclave:
        datas: Iterator[float] = input_reader(enclave.read())

        data_0_1: float = next(datas)
        data_0_2: float = next(datas)

        data_1_1: float = next(datas)
        data_1_2: float = next(datas)

        result: bytes = struct.pack(
            "ffff",
            data_0_1,
            data_0_2,
            data_1_1,
            data_1_2
        )

        enclave.write(result)

    return 0


if __name__ == "__main__":
    main()