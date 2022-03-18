# Cosmian Client SGX

## Overview

Python client library for Cosmian Secure Computation API powered by Intel SGX.

## Install

```console
$ pip install .
```

## Example

```python
from pathlib import Path
import time
from typing import Optional

from cosmian_client_sgx import CodeProviderAPI, DataProviderAPI, ResultConsumerAPI

host: str = "localhost"
port: Optional[int] = None
ssl: bool = True

#
# Code Provider
#
code_provider = CodeProviderAPI(host, port, ssl)

# set your public/private keypair or generate a new one
code_provider.set_keypair(
    public_key=bytes.fromhex("1f80306ddf75ee31bc8f71f29c93768bc6eaba2c1f67bcd7f179ca26d4361331"),
    private_key=bytes.fromhex("deb832a69e996898c835b9779c3a98cd3ba0b437a6aba94dacc33692154a815c")
)  # or code_provider.generate_keypair()

# say hello to the enclave by sending your public key
code_provider.hello()

# upload your Python code (could be encrypted or not)
code_path: Path = Path("tests/data/cp/enclave-join")
code_name: str = code_path.name
code_provider.upload(dir_path=code_path,
                     encrypt=False)

# get enclave's public key bound to the code and each participant public key
code_provider.key_finalize()

# send your symmetric key sealed for the enclave
code_provider.key_provisioning()

# quote to be attested by Intel
quote = code_provider.get_quote()
# Intel's remote attestation
code_provider.remote_attestation(quote)

#
# Data Provider 1
#
data_provider1 = DataProviderAPI(host, port, ssl)

# set your own public/private keypair if you don't want the randomly generated one
data_provider1.set_keypair(
    public_key=bytes.fromhex("08278fc6860d83b598e54462e9c5c68e5eb0bff588de413a0e651a65dd540a29"),
    private_key=bytes.fromhex("dcd1512baa17cb7440078844f3c090dd86c7e3e948065cb6f037f3413b23873f")
)

# say hello to the enclave by sending your public key
data_provider1.hello()

# check participants public key
data_provider1.status()

# get enclave's public key bound to the code and each participant public key
data_provider1.key_finalize()

# send your symmetric key sealed for the enclave
data_provider1.key_provisioning()

# upload your input data for the code (automatically encrypted using a random symmetric key)
data_provider1.push_files(
    code_name,
    Path("tests/data/dp1").glob("*.csv")
)

# check the uploaded datas
print(data_provider1.list_data(code_name))

#
# Data Provider 1
#
data_provider2 = DataProviderAPI(host, port, ssl)

# set your own public/private keypair if you don't want the randomly generated one
data_provider2.set_keypair(
    public_key=bytes.fromhex("6b47b13b4fe3efa09334b079b4cd57ad5f263e4010325510c493cdccc3440b50"),
    private_key=bytes.fromhex("363f07b34144e9b095dfe38b797c6e6012e8d0752a8c621e6d809309e0d83d13")
)

# say hello to the enclave by sending your public key
data_provider2.hello()

# check participants public key
data_provider2.status()

# get enclave's public key bound to the code and each participant public key
data_provider2.key_finalize()

# send your symmetric key sealed for the enclave
data_provider2.key_provisioning()

# upload your input data for the code (automatically encrypted using a random symmetric key)
data_provider2.push_files(
    code_name,
    Path("tests/data/dp2").glob("*.csv")
)

# check the uploaded datas
print(data_provider2.list_data(code_name))

#
# Result Consumer
#
result_consumer = ResultConsumerAPI(host, port, ssl)

# set your own public/private keypair if you don't want the randomly generated one
result_consumer.set_keypair(
    public_key=bytes.fromhex("bd2c17ec62bf8424fda8e36429be0d73f794fd64d92b57c17c17dccf76d6f62e"),
    private_key=bytes.fromhex("697d565f2b421e72635329aaa539fca57e8bc8eaf108ff0ce30e114981ad1f23")
)

# say hello to the enclave by sending your public key
result_consumer.hello()

# check participants public key
result_consumer.status()

# get enclave's public key bound to the code and each participant public key
result_consumer.key_finalize()

# send your symmetric key sealed for the enclave
result_consumer.key_provisioning()

# run the code over data send by Data Providers
result_consumer.run(algo_name=code_name)

# download the results when ready
while result := result_consumer.fetch_result(code_name) is None:
    time.sleep(10)

# write the result
result_path: Path = Path("result.csv")
result_path.write_bytes(result)
```

## Test

```console
$ pytest
```

Optional arguments:

- `--host HOST`, default to `"127.0.0.1"`
- `--port PORT`, default to `None`
- `--ssl`, default to `False`
- `--user`, default to `None` (for HTTP auth)
- `--pass`, default to `None` (for HTTP auth)
