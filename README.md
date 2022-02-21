# Cosmian Client SGX

## Overview

Client to communicate with `enclave-http` API powered by Intel SGX.

## Install

```console
$ pip install .
```

## Example

```python
from pathlib import Path
from typing import Optional

from cosmian_client_sgx import CodeProviderAPI, DataProviderAPI, ResultConsumerAPI

# host of `cosmian_server`
host: str = "localhost"
# port of `cosmian_server`
port: Optional[int] = 9999
ssl: bool = False

algo_provider = CodeProviderAPI(host, port, ssl)
algo_provider.set_keypair(
    public_key=bytes.fromhex("1f80306ddf75ee31bc8f71f29c93768bc6eaba2c1f67bcd7f179ca26d4361331"),
    private_key=bytes.fromhex("deb832a69e996898c835b9779c3a98cd3ba0b437a6aba94dacc33692154a815c")
)  # or algo_provider.generate_keypair()
ret = algo_provider.handshake()
print("=> AP handshake with Enclave...")
print(ret)
quote = algo_provider.get_quote()
print("==> Received quote")
print(quote)
# git clone http://gitlab.cosmian.com/fcolas/enclave-join.git /tmp/enclave-join
algo_path: Path = Path("/tmp/enclave-join")
algo_name: str = algo_path.name
print(f"==> Uploading algo {algo_name} located in {algo_path}")
algo_provider.upload(dir_path=algo_path,
                     encrypt=False)

data_provider = DataProviderAPI(host, port, ssl)
data_provider.set_keypair(
    public_key=bytes.fromhex("08278fc6860d83b598e54462e9c5c68e5eb0bff588de413a0e651a65dd540a29"),
    private_key=bytes.fromhex("dcd1512baa17cb7440078844f3c090dd86c7e3e948065cb6f037f3413b23873f")
)
print("=> DP 1 handshake with Enclave...")
ret = data_provider.handshake()
print(ret)
data_provider.push_data(
    algo_name,
    "A.csv",
    Path("/tmp/enclave-join/data/A.csv").read_bytes()
)
print("==> Data uploaded:")
print(data_provider.list_data(algo_name))

data_provider2 = DataProviderAPI(host, port, ssl)
data_provider2.set_keypair(
    public_key=bytes.fromhex("6b47b13b4fe3efa09334b079b4cd57ad5f263e4010325510c493cdccc3440b50"),
    private_key=bytes.fromhex("363f07b34144e9b095dfe38b797c6e6012e8d0752a8c621e6d809309e0d83d13")
)
print("=> DP 2 handshake with Enclave...")
data_provider2.handshake()
data_provider2.push_data(
    algo_name,
    "B.csv",
    Path("/tmp/enclave-join/data/B.csv").read_bytes()
)
print(data_provider2.list_data(algo_name))

result_owner = ResultConsumerAPI(host, port, ssl)
result_owner.set_keypair(
    public_key=bytes.fromhex("bd2c17ec62bf8424fda8e36429be0d73f794fd64d92b57c17c17dccf76d6f62e"),
    private_key=bytes.fromhex("697d565f2b421e72635329aaa539fca57e8bc8eaf108ff0ce30e114981ad1f23")
)
print("=> RO handshake with Enclave...")
result_owner.handshake()

ret = result_owner.status()
print(ret)
print(f"==> Running {algo_name}...")
success = result_owner.run(algo_name=algo_name, entrypoint="run.py")

if not success:
    raise Exception("Problem when running algo!")

print("==> Fetch and decrypt result:")
result = result_owner.fetch_result(algo_name=algo_name)

result_path: Path = Path("result.csv")
result_path.write_bytes(result)

print("==> Result saved in result.csv")

result_owner.reset(algo_name=algo_name)
```

## Test

```console
$ pytest
```

Optional arguments:

- `--host HOST`, default to `"127.0.0.1"`
- `--port PORT`, default to `None`
- `--ssl`, default to `False`