from typing import Optional, Dict, Union, List, Tuple

from cosmian_client_sgx import Computation, ComputationOwner, CodeProviderAPI, DataProviderAPI, ResultConsumerAPI
from os import environ
import os
import subprocess
from pathlib import Path
import time

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
    To create your first computation, create the ComputationOwner object with your secret token.
    """
    computation_owner = ComputationOwner(cosmian_token)

    """
    To create a computation, you need to pass :
    - the name of the computation
    - your PGP public key for the computation
    - the list of participants and their associated roles

    To generate your PGP key, you can use `gpg` as follow: *TODO explicit gpg creation examples*
    """
    public_key = "your_own_gpg_public_key"

    """
    Create your computation :
    You will be the Computation Owner of this computation.
    """
    computation = computation_owner.create_computation(
        'computation name',
        owner_public_key=public_key,
        code_provider_email="code.provider@example.org",
        data_providers_emails=["data.provider@example.org"],
        result_consumers_emails=["result.consumer@example.org"]
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
    To create your first computation, create the ComputationOwner object with your secret token.
    """
    computation_owner = ComputationOwner(cosmian_token)

    """
    To create a computation, you need to pass :
    - the name of the computation
    - your PGP public key for the computation
    - the list of participants and their associated roles

    To simplify the example, we'll say that all participants are
    yourself (me@example.org).

    To generate your PGP key, you can use `gpg` as follow: *TODO explicit gpg creation examples*
    """
    public_key = "your_own_gpg_public_key"

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
    code_provider = CodeProviderAPI(cosmian_token)

    """
    To register, pass the UUID of the computation given on the interface and
    your PGP public key for your role on this computation.
    
    To generate your PGP key, you can use `gpg` as follow: *TODO explicit gpg creation examples*
    """
    public_key = "your_own_gpg_public_key"

    computation = code_provider.register(computation_uuid, public_key)

def step_2_data_providers_register(cosmian_token, computation_uuid):
    """
    You need to create the DataProvider object to register as a data provider.
    """
    data_provider = DataProviderAPI(cosmian_token)

    """
    To register, you need to pass the UUID of the computation given on the interface and
    your PGP public key for your role on this computation.
    
    To generate your PGP key, you can use `gpg` as follow: *TODO explicit gpg creation examples*
    """
    public_key = "your_own_gpg_public_key"

    computation = data_provider.register(computation_uuid, public_key)

def step_2_result_consumers_register(cosmian_token, computation_uuid):
    """
    You need to create the ResultConsumer object to register as a result consumer.
    """
    result_consumer = ResultConsumerAPI(cosmian_token)

    """
    To register, you need to pass the UUID of the computation given on the interface and
    your PGP public key for your role on this computation.
    
    To generate your PGP key, you can use `gpg` as follow: *TODO explicit gpg creation examples*
    """
    public_key = "your_own_gpg_public_key"

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
    code_provider = CodeProviderAPI(cosmian_token)

    code_provider.upload(computation_uuid, symetric_key, path)

    return symetric_key

def step_4_computation_owner_approves_participants(cosmian_token, computation_uuid):
    """
    You need to check that the list of participants is correct. To do so, you can 
    fetch computation's status and read the enclave manifest.

    TODO explain how Cosmian cannot change the participants list because
    it's signed by the enclave / check enclave public key / check manifest signature.

    TODO explain how to fetch the manifest.
    """
    computation_owner = ComputationOwner(cosmian_token)

    computation = computation_owner.get_computation(computation_uuid)

    """
    To approve participants, you need to sign the enclave's manifest.
    After that, each participant will be able to see that you've approved this computation
    and check your signature with your provided public key.

    TODO crypto stuff here / PGP sign with external run? / bytes or string for signature?
    """
    computation_owner.approve_participants(computation.uuid, "TODO_compute_signature_here")

def step_5_code_provider_sends_sealed_symetric_key(cosmian_token, computation_uuid, symetric_key):
    """
    You need to check that the computation is correct :
    > You can fetch computation's status and read the enclave manifest.
    > You can check computation owner's signature from the manifest.

    TODO explain how Cosmian cannot change the participants list because
    it's signed by the enclave / check enclave public key / check manifest signature.

    TODO explain how to fetch the manifest.
    """
    code_provider = CodeProviderAPI(cosmian_token)

    computation = code_provider.get_computation(computation_uuid)

    """
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

    TODO explain how Cosmian cannot change the participants list because
    it's signed by the enclave / check enclave public key / check manifest signature.

    TODO explain how to fetch the manifest.
    """
    data_provider = DataProviderAPI(cosmian_token)

    computation = data_provider.get_computation(computation_uuid)

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
    data_provider.push_files(computation.uuid, symetric_key, [path_1, path_2])

    """
    When you're done uploading your files, notify the server so it knows that data are ready :
    """
    data_provider.done(computation.uuid)

    """
    > Finally, send your symetric key sealed with enclave's public key :
    """
    from cosmian_client_sgx.crypto.helper import seal
    sealed_symetric_key = seal(symetric_key, computation.enclave.public_key)

    data_provider.key_provisioning(computation.uuid, sealed_symetric_key)


def step_7_result_consumers_send_sealed_symetric_keys(cosmian_token, computation_uuid):
    """
    You need to check that the computation is correct :
    > You can fetch computation's status and read the enclave manifest.
    > You can check computation owner's signature from the manifest.

    TODO explain how Cosmian cannot change the participants list because
    it's signed by the enclave / check enclave public key / check manifest signature.

    TODO explain how to fetch the manifest.
    """
    result_consumer = ResultConsumerAPI(cosmian_token)

    computation = result_consumer.get_computation(computation_uuid)

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
    result_consumer = ResultConsumerAPI(cosmian_token)

    while True:
        """
        First we'll check that the computation ended and one computation is in previous runs.
        """
        print("Waiting end of computation…")
        time.sleep(2)
        computation = result_consumer.get_computation(computation_uuid)

        if computation.runs.current is None and len(computation.runs.previous) == 1:
            run = computation.runs.previous[0]
            if run.exit_code != 0:
                print("\n\n### Exit Code ###\n")
                print(run.exit_code)
                print("\n\n### stdout ###\n")
                print(run.stdout)
                print("\n\n### stderr ###\n")
                print(run.stderr)
                print("\n\n")
                raise "Run fail."

            break

    encrypted_results = result_consumer.fetch_results(computation.uuid)

    from cosmian_client_sgx.crypto.helper import decrypt
    results = decrypt(encrypted_results, symetric_key)

    print(results)


def run(until = 12):
    print("### step_1_create_computation")
    computation = step_1_create_computation() if environ.get('SEED_EMAIL') is None else step_1_create_computation_seed()
    print(computation)

    if until < 2: return

    print("Sleeping on Docker creation…")
    time.sleep(5)

    print("Continuing…")
    cosmian_token = environ.get('COSMIAN_TOKEN')

    print("### step_2_code_provider_registers")
    step_2_code_provider_registers(cosmian_token, computation)

    if until < 3: return

    print("### step_2_data_providers_register")
    step_2_data_providers_register(cosmian_token, computation)
    
    if until < 4: return

    print("### step_2_result_consumers_register")
    step_2_result_consumers_register(cosmian_token, computation)
    
    if until < 5: return

    print("### step_3_code_provider_sends_code")
    code_provider_symetric_key = step_3_code_provider_sends_code(cosmian_token, computation, Path(os.path.dirname(__file__) + "/../tests/data/cp/enclave-join"))
    
    if until < 6: return

    print("### step_4_computation_owner_approves_participants")
    step_4_computation_owner_approves_participants(cosmian_token, computation)
    
    if until < 7: return

    print("### step_5_code_provider_sends_sealed_symetric_key")
    step_5_code_provider_sends_sealed_symetric_key(cosmian_token, computation, code_provider_symetric_key)
    
    if until < 8: return

    print("### step_6_data_providers_send_data_and_sealed_symetric_keys")
    step_6_data_providers_send_data_and_sealed_symetric_keys(cosmian_token, computation, Path(os.path.dirname(__file__) + "/../tests/data/dp1/A.csv"), Path(os.path.dirname(__file__) + "/../tests/data/dp2/B.csv"))
    
    if until < 9: return

    print("### step_7_result_consumers_send_sealed_symetric_keys")
    result_consumer_symetric_key = step_7_result_consumers_send_sealed_symetric_keys(cosmian_token, computation)
    
    if until < 10: return

    print("### step_8_result_consumers_get_results")
    step_8_result_consumers_get_results(cosmian_token, computation, result_consumer_symetric_key)


def run_all():
    print(f"Seeding for {environ.get('SEED_EMAIL')}…\n\n")
    for i in range(1,11):
        print(f"\n\n###### Running until {i} ######\n")
        run(i)

run(10) if environ.get('SEED_EMAIL') is None else run_all()