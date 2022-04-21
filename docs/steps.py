from typing import Optional, Dict, Union, List, Tuple

from cosmian_client_sgx import Computation, ComputationOwnerAPI, CodeProviderAPI, DataProviderAPI, ResultConsumerAPI
from os import environ
import os
import subprocess
from pathlib import Path
import time
import pprint
import struct

def run_subprocess(command: List[str]) -> Optional[str]:
    process = subprocess.Popen(command, stdout=subprocess.PIPE,  stderr=subprocess.PIPE, universal_newlines=True)
    stdout, stderr = process.communicate()

    # if stderr != "":
    #     print("Non empty stderr during command:")
    #     print(stderr)
    #     return None

    return stdout

def step_1_create_computation():
    """
    Fetch your Cosmian token from the web console: https://console.cosmian.com/secret-token
    Store your token inside env variable, file, whatever suit's your security needs.
    For the example, we'll fetch the token from an env variable.
    """
    cosmian_token = environ.get('COSMIAN_TOKEN')

    """
    To create your first computation, create the ComputationOwnerAPI object with your secret token.
    """
    from cosmian_client_sgx import ComputationOwnerAPI
    computation_owner = ComputationOwnerAPI(cosmian_token)

    """
    To create a computation, you need to pass :
    - the name of the computation
    - your PGP public key for the computation
    - the list of participants and their associated roles

    To generate your PGP key, you can use `gpg` as follow: 
    ```
    gpg --batch --passphrase --quick-generate-key "John Doe <john@example.org>" ed25519 cert never
    gpg --export --armor john@example.org
    ```

    /!\/!\/!\ WARNING /!\/!\/!\

    If you share multiple roles in the computation, you must use different PGP key for each role.
    You can generate a new PGP key for an alias of your email address "john+data_provider@example.org".

    /!\/!\/!\ WARNING /!\/!\/!\
    """
    public_key = """
-----BEGIN PGP PUBLIC KEY BLOCK-----

mDMEYksDzBYJKwYBBAHaRw8BAQdA3ARj30Dc6+h+CpZBoh+gbRLqMQidUgSb15j6
uI4gmsC0IVRoaWJhdWQgRG9lIDx0aGliYXVkQGV4YW1wbGUub3JnPoiQBBMWCAA4
FiEEyTCpzMklYuj4MsIrH++EVqAxpd8FAmJLA8wCGwEFCwkIBwIGFQoJCAsCBBYC
AwECHgECF4AACgkQH++EVqAxpd8tbgEAnVlpFCjhzaR3sg4R0wHe4Sf0BF94WzA1
UQRy1f1YLP8A/jNjCWL1nlrTkHpKHG5d6N9ihdpRaGvM/QhteS5Z+FAH
=HqGK
-----END PGP PUBLIC KEY BLOCK-----
    """

    """
    Create your computation :
    You will be the Computation Owner of this computation.
    """
    computation = computation_owner.create_computation(
        'computation name',
        owner_public_key=public_key,
        code_provider_email="thibaud.dauce@cosmian.com",
        data_providers_emails=["thibaud.dauce@cosmian.com"],
        result_consumers_emails=["thibaud.dauce@cosmian.com"]
    )

    return computation

def step_1_create_computation_seed():
    """
    Fetch your Cosmian token from the web console: https://console.cosmian.com/secret-token
    Store your token inside env variable, file, whatever suit's your security needs.
    For the example, we'll fetch the token from an env variable.
    """
    cosmian_token = environ.get('COSMIAN_TOKEN')

    """
    To create your first computation, create the ComputationOwnerAPI object with your secret token.
    """
    from cosmian_client_sgx import ComputationOwnerAPI
    computation_owner = ComputationOwnerAPI(cosmian_token)

    """
    To create a computation, you need to pass :
    - the name of the computation
    - your PGP public key for the computation
    - the list of participants and their associated roles

    To simplify the example, we'll say that all participants are
    yourself (me@example.org).

    To generate your PGP key, you can use `gpg` as follow: 
    ```
    gpg --batch --passphrase --quick-generate-key "John Doe <john@example.org>" ed25519 cert never
    gpg --export --armor john@example.org
    ```

    /!\/!\/!\ WARNING /!\/!\/!\

    If you share multiple roles in the computation, you must use different PGP key for each role.
    You can generate a new PGP key for an alias of your email address "john+data_provider@example.org".

    /!\/!\/!\ WARNING /!\/!\/!\
    """
    public_key = """
-----BEGIN PGP PUBLIC KEY BLOCK-----

mDMEYksDzBYJKwYBBAHaRw8BAQdA3ARj30Dc6+h+CpZBoh+gbRLqMQidUgSb15j6
uI4gmsC0IVRoaWJhdWQgRG9lIDx0aGliYXVkQGV4YW1wbGUub3JnPoiQBBMWCAA4
FiEEyTCpzMklYuj4MsIrH++EVqAxpd8FAmJLA8wCGwEFCwkIBwIGFQoJCAsCBBYC
AwECHgECF4AACgkQH++EVqAxpd8tbgEAnVlpFCjhzaR3sg4R0wHe4Sf0BF94WzA1
UQRy1f1YLP8A/jNjCWL1nlrTkHpKHG5d6N9ihdpRaGvM/QhteS5Z+FAH
=HqGK
-----END PGP PUBLIC KEY BLOCK-----
    """

    """
    Create your computation :
    You will be the Computation Owner of this computation.
    """
    computation = computation_owner.create_computation(
        'computation name',
        owner_public_key=public_key,
        code_provider_email=environ.get('SEED_EMAIL'),
        data_providers_emails=[environ.get('SEED_EMAIL')],
        result_consumers_emails=[environ.get('SEED_EMAIL')]
    )

    return computation


def step_2_code_provider_registers(cosmian_token, computation_uuid):
    """
    You need to create the CodeProvider object to register as a code provider.
    """
    from cosmian_client_sgx import CodeProviderAPI
    code_provider = CodeProviderAPI(cosmian_token)

    """
    To register, pass the UUID of the computation given on the interface and
    your PGP public key for your role on this computation.
    
    To generate your PGP key, you can use `gpg` as follow: 
    ```
    gpg --batch --passphrase --quick-generate-key "John Doe <john@example.org>" ed25519 cert never
    gpg --export --armor john@example.org
    ```

    /!\/!\/!\ WARNING /!\/!\/!\

    If you share multiple roles in the computation, you must use different PGP key for each role.
    You can generate a new PGP key for an alias of your email address "john+data_provider@example.org".

    /!\/!\/!\ WARNING /!\/!\/!\
    """
    public_key = """
-----BEGIN PGP PUBLIC KEY BLOCK-----

mDMEYk1S+RYJKwYBBAHaRw8BAQdA+VDkJGp6qVxh/4T2dpEUklXIISmXJiwrdivp
uYVrpNe0L1RoaWJhdWQgRG9lIDx0aGliYXVkK2NvZGVfcHJvdmlkZXJAZXhhbXBs
ZS5vcmc+iJAEExYIADgWIQTpIgxK3InT95bDpzKMdEHyAiaBsQUCYk1S+QIbAQUL
CQgHAgYVCgkICwIEFgIDAQIeAQIXgAAKCRCMdEHyAiaBsWLxAP9A0ewYV31r1DK/
2tKUs9YrVviAXYmaxuIIe6i9sSXE2AEAqw/CUMXQ4Zzc7whl9jjFShTl7+C7HS+G
DHNRnGIH6QI=
=WNuo
-----END PGP PUBLIC KEY BLOCK-----
    """

    computation = code_provider.register(computation_uuid, public_key)

def step_2_data_providers_register(cosmian_token, computation_uuid):
    """
    You need to create the DataProvider object to register as a data provider.
    """
    from cosmian_client_sgx import DataProviderAPI
    data_provider = DataProviderAPI(cosmian_token)

    """
    To register, you need to pass the UUID of the computation given on the interface and
    your PGP public key for your role on this computation.
    
    To generate your PGP key, you can use `gpg` as follow: 
    ```
    gpg --batch --passphrase --quick-generate-key "John Doe <john@example.org>" ed25519 cert never
    gpg --export --armor john@example.org
    ```

    /!\/!\/!\ WARNING /!\/!\/!\

    If you share multiple roles in the computation, you must use different PGP key for each role.
    You can generate a new PGP key for an alias of your email address "john+data_provider@example.org".

    /!\/!\/!\ WARNING /!\/!\/!\
    """
    public_key = """
-----BEGIN PGP PUBLIC KEY BLOCK-----

mDMEYk1S+hYJKwYBBAHaRw8BAQdA48hxvxb4BkadoWu9puAzgvpNfoACr2lkofbC
ZKnjEr60L1RoaWJhdWQgRG9lIDx0aGliYXVkK2RhdGFfcHJvdmlkZXJAZXhhbXBs
ZS5vcmc+iJAEExYIADgWIQRrFoMhI0RLogfK9Vrl25B3ixK0eQUCYk1S+gIbAQUL
CQgHAgYVCgkICwIEFgIDAQIeAQIXgAAKCRDl25B3ixK0eb0QAQCNLTP+4rFTftDy
h3xBNL13paB8OQH+JLlWPAE9x306HQEA+aoDB71PlrN1SwOcw4O6jr2LOEODy/Gj
0MEG2ZPJUAI=
=/4oo
-----END PGP PUBLIC KEY BLOCK-----
    """

    computation = data_provider.register(computation_uuid, public_key)

def step_2_result_consumers_register(cosmian_token, computation_uuid):
    """
    You need to create the ResultConsumer object to register as a result consumer.
    """
    from cosmian_client_sgx import ResultConsumerAPI
    result_consumer = ResultConsumerAPI(cosmian_token)

    """
    To register, you need to pass the UUID of the computation given on the interface and
    your PGP public key for your role on this computation.
    
    To generate your PGP key, you can use `gpg` as follow: 
    ```
    gpg --batch --passphrase --quick-generate-key "John Doe <john@example.org>" ed25519 cert never
    gpg --export --armor john@example.org
    ```

    /!\/!\/!\ WARNING /!\/!\/!\

    If you share multiple roles in the computation, you must use different PGP key for each role.
    You can generate a new PGP key for an alias of your email address "john+data_provider@example.org".

    /!\/!\/!\ WARNING /!\/!\/!\
    """
    public_key = """
-----BEGIN PGP PUBLIC KEY BLOCK-----

mDMEYk1S+xYJKwYBBAHaRw8BAQdAatwSPGAK8j1HBTQjHKFDCm2+KaDz1fJPBIjX
pgUmwVS0MVRoaWJhdWQgRG9lIDx0aGliYXVkK3Jlc3VsdF9jb25zdW1lckBleGFt
cGxlLm9yZz6IkAQTFggAOBYhBCEEpkOFVeXMXfkvU/UjPZ2e1dlFBQJiTVL7AhsB
BQsJCAcCBhUKCQgLAgQWAgMBAh4BAheAAAoJEPUjPZ2e1dlF7LkA/1QUz9dKjAbD
fkz02A4i7Lw6RVRVAx3oWppXUVuh29jrAQDCvjksDI0O0guspHed5Y0Aax9vefHg
+hfz9O5GiLm2Bg==
=TGEi
-----END PGP PUBLIC KEY BLOCK-----
    """

    computation = result_consumer.register(computation_uuid, public_key)

def step_3_code_provider_sends_code(cosmian_token, computation_uuid, path):
    """
    As a code provider, you will send code to the enclave.
    > First, you have to generate a symetric key. The Cosmian client
    provides a function for that, but you can also use whatever suit's your security needs.
    *TODO explain what type of key is required*

    You need to store this symetric key somewhere safe. It'll be required later for you to send it to 
    the enclave.
    """
    from cosmian_client_sgx.crypto.helper import random_symkey
    symetric_key = random_symkey()

    """
    > Next, upload your code folder, specifying its path.
    This folder should contains a `run.py` file.
    The `run.py` file will not be encrypted, everything else will be.
    """
    from cosmian_client_sgx import CodeProviderAPI
    code_provider = CodeProviderAPI(cosmian_token)

    code_provider.upload(computation_uuid, symetric_key, path)

    return symetric_key

def step_4_computation_owner_approves_participants(cosmian_token, computation_uuid):
    """
    You need to check that the list of participants is correct. To do so, you can 
    fetch computation's status and read the enclave manifest.

    The SGX enclave used for the computation provides a few information about the 
    security of the process. You can access these informations from the computation
    object.
    """
    from cosmian_client_sgx import ComputationOwnerAPI
    computation_owner = ComputationOwnerAPI(cosmian_token)

    computation = computation_owner.get_computation(computation_uuid)
    
    manifest = computation.enclave.manifest
    quote = computation.enclave.quote

    """
    Cosmian will provide a function to check the validity of these data by using DCAP
    https://github.com/intel/SGXDataCenterAttestationPrimitives

    For now, you can do your own checks or wait for us to provide the helpers.
    """

    """
    To approve participants, you need to sign the enclave's manifest.
    After that, each participant will be able to see that you've approved this computation
    and check your signature with your provided public key.

    Right now, Cosmian doesn't provide a way to sign the manifest.
    This operation is not required for the enclave to run in secure mode. It's only
    to provide a way for all the participants to check that the computation owner
    is ok with the parameters of this computation (the computation owner is the only 
    participant with no role inside the SGX enclave).
    If the computation owner is also code provider (or any other role), it's approval 
    is already done when he sends his sealed symetric key.

    If, as in the example, you send only the string "Missing Signature", the other participants
    will see this. You can also sign the manifest and the quote with your PGP key and tell the other
    participants to check this.
    """
    computation_owner.approve_participants(computation.uuid, "Missing Signature")

def step_5_code_provider_sends_sealed_symetric_key(cosmian_token, computation_uuid, symetric_key):
    """
    You need to check that the computation is correct :
    > You can fetch computation's status and read the enclave manifest.
    > You can check computation owner's signature from the manifest (not available yet).

    The SGX enclave used for the computation provides a few information about the 
    security of the process. You can access these informations from the computation
    object.
    """
    from cosmian_client_sgx import CodeProviderAPI
    code_provider = CodeProviderAPI(cosmian_token)

    computation = code_provider.get_computation(computation_uuid)
    manifest = computation.enclave.manifest
    quote = computation.enclave.quote

    """
    Cosmian will provide a function to check the validity of these data by using DCAP
    https://github.com/intel/SGXDataCenterAttestationPrimitives

    For now, you can do your own checks or wait for us to provide the helpers.

    To approve the computation, send your symetric key sealed with enclave's public key.

    You need to use the same symetric key as in step 3 (code upload).
    """
    from cosmian_client_sgx.crypto.helper import seal
    sealed_symetric_key = seal(symetric_key, computation.enclave.public_key)

    code_provider.key_provisioning(computation.uuid, sealed_symetric_key)

def step_6_data_providers_send_data_and_sealed_symetric_keys(cosmian_token, computation_uuid, path_1, path_2):
    """
    You need to check that the computation is correct :
    > You can fetch computation's status and read the enclave manifest.
    > You can check computation owner's signature from the manifest.

    The SGX enclave used for the computation provides a few information about the 
    security of the process. You can access these informations from the computation
    object.
    """
    from cosmian_client_sgx import DataProviderAPI
    data_provider = DataProviderAPI(cosmian_token)

    computation = data_provider.get_computation(computation_uuid)
    manifest = computation.enclave.manifest
    quote = computation.enclave.quote

    """
    Cosmian will provide a function to check the validity of these data by using DCAP
    https://github.com/intel/SGXDataCenterAttestationPrimitives

    For now, you can do your own checks or wait for us to provide the helpers.
    """

    """
    As a data provider, you will send data to the enclave.
    > First, you have to generate a symetric key. The Cosmian client
    provides a function for that, but you can also use whatever suit's your security needs.
    *TODO explain what type of key is required*
    """
    from cosmian_client_sgx.crypto.helper import random_symkey
    symetric_key = random_symkey()

    """
    > Next, send your encrypted data to the enclave, specifying the different paths :
    """
    data_provider.push_data(computation_uuid, symetric_key, "A", struct.pack("f", 0.1))
    data_provider.push_data(computation_uuid, symetric_key, "B", struct.pack("f", 0.2))
    data_provider.push_data(computation_uuid, symetric_key, "C", struct.pack("f", 1.1))
    data_provider.push_data(computation_uuid, symetric_key, "D", struct.pack("f", 1.2))

    """
    When you're done uploading your files, notify the server so it knows that data are ready :
    """
    data_provider.done(computation_uuid)

    """
    > Finally, send your symetric key sealed with enclave's public key :
    """
    from cosmian_client_sgx.crypto.helper import seal
    sealed_symetric_key = seal(symetric_key, computation.enclave.public_key)

    data_provider.key_provisioning(computation_uuid, sealed_symetric_key)


def step_7_result_consumers_send_sealed_symetric_keys(cosmian_token, computation_uuid):
    """
    You need to check that the computation is correct :
    > You can fetch computation's status and read the enclave manifest.
    > You can check computation owner's signature from the manifest.

    The SGX enclave used for the computation provides a few information about the 
    security of the process. You can access these informations from the computation
    object.
    """
    from cosmian_client_sgx import ResultConsumerAPI
    result_consumer = ResultConsumerAPI(cosmian_token)

    computation = result_consumer.get_computation(computation_uuid)
    manifest = computation.enclave.manifest
    quote = computation.enclave.quote

    """
    Cosmian will provide a function to check the validity of these data by using DCAP
    https://github.com/intel/SGXDataCenterAttestationPrimitives

    For now, you can do your own checks or wait for us to provide the helpers.
    """

    """
    As a result consumer, you will retrieve results after computation's run. But before,
    you have to send you symetric key, sealed with enclave's public key :
    > First, you have to generate a symetric key. The Cosmian client
    provides a function for that, but you can also use whatever suit's your security needs.
    *TODO explain what type of key is required*
    """
    from cosmian_client_sgx.crypto.helper import random_symkey
    symetric_key = random_symkey()

    """
    > Next, send your symetric key sealed with enclave's public key :
    """
    from cosmian_client_sgx.crypto.helper import seal
    sealed_symetric_key = seal(symetric_key, computation.enclave.public_key)

    result_consumer.key_provisioning(computation.uuid, sealed_symetric_key)

    return symetric_key


def step_8_result_consumers_get_results(cosmian_token, computation_uuid, symetric_key):
    """
    When the computation is over, you can fetch results.
    """
    from cosmian_client_sgx import ResultConsumerAPI
    result_consumer = ResultConsumerAPI(cosmian_token)

    while True:
        """
        First we'll check that the computation ended and one computation is in previous runs.
        """
        computation = result_consumer.get_computation(computation_uuid)

        if computation.runs.current is None and len(computation.runs.previous) == 1:
            run = computation.runs.previous[0]

            """
            You can check a few information on the run to check
            if everything worked.
            """
            if run.exit_code != 0:
                print("\n\n### Exit Code ###\n")
                print(run.exit_code)
                print("\n\n### stdout ###\n")
                print(run.stdout)
                print("\n\n### stderr ###\n")
                print(run.stderr)
                print("\n\n")
                raise "Run fail."
            else:
                break
        else:
            print("Waiting 2s end of computation…")
            time.sleep(2)

    encrypted_results = result_consumer.fetch_results(computation.uuid)

    from cosmian_client_sgx.crypto.helper import decrypt
    results = decrypt(encrypted_results, symetric_key)

    print(results)


def run(until = 12):
    print("### step_1_create_computation")
    computation = step_1_create_computation() if environ.get('SEED_EMAIL') is None else step_1_create_computation_seed()

    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(computation)

    if until < 2: return

    print("Sleeping on Docker creation…")
    time.sleep(5)

    print("Continuing…")
    cosmian_token = environ.get('COSMIAN_TOKEN')

    print("### step_2_code_provider_registers")
    step_2_code_provider_registers(cosmian_token, computation.uuid)

    if until < 3: return

    print("### step_2_data_providers_register")
    step_2_data_providers_register(cosmian_token, computation.uuid)
    
    if until < 4: return

    print("### step_2_result_consumers_register")
    step_2_result_consumers_register(cosmian_token, computation.uuid)
    
    if until < 5: return

    print("### step_3_code_provider_sends_code")
    code_provider_symetric_key = step_3_code_provider_sends_code(cosmian_token, computation.uuid, Path(os.path.dirname(__file__) + "/../tests/data/cp/enclave-join"))
    
    if until < 6: return

    print("### step_4_computation_owner_approves_participants")
    step_4_computation_owner_approves_participants(cosmian_token, computation.uuid)
    
    if until < 7: return

    print("### step_5_code_provider_sends_sealed_symetric_key")
    step_5_code_provider_sends_sealed_symetric_key(cosmian_token, computation.uuid, code_provider_symetric_key)
    
    if until < 8: return

    print("### step_6_data_providers_send_data_and_sealed_symetric_keys")
    step_6_data_providers_send_data_and_sealed_symetric_keys(cosmian_token, computation.uuid, Path(os.path.dirname(__file__) + "/../tests/data/dp1/A.csv"), Path(os.path.dirname(__file__) + "/../tests/data/dp2/B.csv"))
    
    if until < 9: return

    print("### step_7_result_consumers_send_sealed_symetric_keys")
    result_consumer_symetric_key = step_7_result_consumers_send_sealed_symetric_keys(cosmian_token, computation.uuid)
    
    if until < 10: return

    print("### step_8_result_consumers_get_results")
    step_8_result_consumers_get_results(cosmian_token, computation.uuid, result_consumer_symetric_key)


def run_all():
    print(f"Seeding for {environ.get('SEED_EMAIL')}…\n\n")
    for i in range(1,11):
        print(f"\n\n###### Running until {i} ######\n")
        run(i)

run(10) if environ.get('SEED_EMAIL') is None else run_all()