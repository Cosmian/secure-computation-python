from typing import Optional, Dict, Union, List, Tuple

from cosmian_client_sgx import ComputationOwner, CodeProviderAPI, DataProviderAPI, ResultConsumerAPI
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
    First, you need to fetch your Cosmian token from the web console: TODO add link here
    Store your token inside env variable, file, whatever suit's your security needs.
    For the example, we'll fetch the token from an env variable.
    """
    cosmian_token = environ.get('COSMIAN_TOKEN')

    """
    Next, you need to create the ComputationOwner object to create your first computation.
    """
    computation_owner = ComputationOwner(cosmian_token)

    """
    To create a computation, you need to pass the name of the computation,
    your PGP public key for the computation and the list of participants.
    To simplify the example, we'll say that all participants are
    yourself (thibaud@example.org).

    To generate your PGP key, you can use `gpg` as follow:
    """
    run_subprocess(['gpg', '--batch', '--passphrase', '', '--quick-generate-key', 'Thibaud Doe <thibaud@example.org>', 'ed25519', 'cert', 'never'])
    public_key = run_subprocess(['gpg', '--export', '--armor', 'thibaud@example.org'])

    computation = computation_owner.create_computation(
        'Lifeline',
        owner_public_key=public_key,
        code_provider_email="thibaud@example.org",
        data_providers_emails=["thibaud@example.org"],
        result_consumers_emails=["thibaud@example.org"]
    )

    return computation

def step_1_create_computation_seed():
    """
    First, you need to fetch your Cosmian token from the web console: TODO add link here
    Store your token inside env variable, file, whatever suit's your security needs.
    For the example, we'll fetch the token from an env variable.
    """
    cosmian_token = environ.get('COSMIAN_TOKEN')

    """
    Next, you need to create the ComputationOwner object to create your first computation.
    """
    computation_owner = ComputationOwner(cosmian_token)

    """
    To create a computation, you need to pass the name of the computation,
    your PGP public key for the computation and the list of participants.
    To simplify the example, we'll say that all participants are
    yourself (thibaud@example.org).

    To generate your PGP key, you can use `gpg` as follow:
    """
    run_subprocess(['gpg', '--batch', '--passphrase', '', '--quick-generate-key', 'Thibaud Doe <thibaud@example.org>', 'ed25519', 'cert', 'never'])
    public_key = run_subprocess(['gpg', '--export', '--armor', 'thibaud@example.org'])

    computation = computation_owner.create_computation(
        'Lifeline',
        owner_public_key=public_key,
        code_provider_email=environ.get('SEED_EMAIL'),
        data_providers_emails=[environ.get('SEED_EMAIL')],
        result_consumers_emails=[environ.get('SEED_EMAIL')]
    )

    return computation


def step_2_code_provider_registers(cosmian_token, computation):
    """
    You need to create the CodeProvider object to register.
    """
    code_provider = CodeProviderAPI(cosmian_token)

    """
    To register, you need to pass the UUID of the computation given on the interface and
    your PGP public key for your role on this computation.
    
    To generate your PGP key, you can use `gpg` as follow:
    """
    run_subprocess(['gpg', '--batch', '--passphrase', '', '--quick-generate-key', 'Thibaud Doe <thibaud+code_provider@example.org>', 'ed25519', 'cert', 'never'])
    public_key = run_subprocess(['gpg', '--export', '--armor', 'thibaud+code_provider@example.org'])

    computation = code_provider.register(computation['uuid'], public_key)

def step_2_data_providers_register(cosmian_token, computation):
    """
    You need to create the DataProvider object to register.
    """
    data_provider = DataProviderAPI(cosmian_token)

    """
    To register, you need to pass the UUID of the computation given on the interface and
    your PGP public key for your role on this computation.
    
    To generate your PGP key, you can use `gpg` as follow:
    """
    run_subprocess(['gpg', '--batch', '--passphrase', '', '--quick-generate-key', 'Thibaud Doe <thibaud+data_provider@example.org>', 'ed25519', 'cert', 'never'])
    public_key = run_subprocess(['gpg', '--export', '--armor', 'thibaud+data_provider@example.org'])

    computation = data_provider.register(computation['uuid'], public_key)

def step_2_result_consumers_register(cosmian_token, computation):
    """
    You need to create the ResultConsumer object to register.
    """
    result_consumer = ResultConsumerAPI(cosmian_token)

    """
    To register, you need to pass the UUID of the computation given on the interface and
    your PGP public key for your role on this computation.
    
    To generate your PGP key, you can use `gpg` as follow:
    """
    run_subprocess(['gpg', '--batch', '--passphrase', '', '--quick-generate-key', 'Thibaud Doe <thibaud+result_consumer@example.org>', 'ed25519', 'cert', 'never'])
    public_key = run_subprocess(['gpg', '--export', '--armor', 'thibaud+result_consumer@example.org'])

    computation = result_consumer.register(computation['uuid'], public_key)

def step_3_code_provider_sends_code(cosmian_token, computation, path):
    code_provider = CodeProviderAPI(cosmian_token)

    """
    To send your code, you first need to generate a symetric key. The Cosmian client
    provides a function for that, but you can use whatever suit's your security needs.
    *TODO explain what type of key is required*

    Please store this symetric key somewhere. It'll be required later to send it to 
    the enclave.
    """
    from cosmian_client_sgx.crypto.helper import random_symkey
    symetric_key = random_symkey()

    """
    Next, you can upload your code folder. This folder should contains a `run.py` file.
    This `run.py` file will not be encrypted. Everything else will be.
    """
    code_provider.upload(computation['uuid'], symetric_key, path)

    return symetric_key

def step_4_computation_owner_approves_participants(cosmian_token, computation):
    """
    You need to check that the list of participants is correct. To do that, you can 
    fetch the status of the computation and read the enclave manifest.

    TODO explain how Cosmian cannot change the participants list because
    it's signed by the enclave / check enclave public key / check manifest signature.
    """
    computation_owner = ComputationOwner(cosmian_token)

    computation = computation_owner.get_computation(computation['uuid'])

    """
    To approve the participants, you need to sign the manifest.
    Every participant can check your signature with your public key to check
    if you're ok with this computation.

    TODO crypto stuff here / PGP sign with external run? / bytes or string for signature?
    """
    computation_owner.approve_participants(computation['uuid'], "TODO_compute_signature_here")

def step_5_code_provider_sends_sealed_symetric_key(cosmian_token, computation, symetric_key):
    """
    You need to check that the computation is correct. To do that, you can 
    fetch the status of the computation and read the enclave manifest. You can also
    check the manifest's signature of the computation owner.

    TODO explain how Cosmian cannot change the participants list because
    it's signed by the enclave / check enclave public key / check manifest signature.
    """
    code_provider = CodeProviderAPI(cosmian_token)

    computation = code_provider.get_computation(computation['uuid'])

    """
    To approve the computation, you need to send your symetric key sealed with the public key of the enclave.

    You need to fetch back your symetric key from the step 3, when you've uploaded your code and sealed it with the
    enclave public key.
    """
    from cosmian_client_sgx.crypto.helper import seal
    sealed_symetric_key = seal(symetric_key, bytes(computation['enclave']['public_key'])) # TODO when Computation'll be a class and not a Dict we'll convert it before handling it to the client

    code_provider.key_provisioning(computation['uuid'], sealed_symetric_key)

def step_6_data_providers_send_data_and_sealed_symetric_keys(cosmian_token, computation, path_1, path_2):
    """
    You need to check that the computation is correct. To do that, you can 
    fetch the status of the computation and read the enclave manifest. You can also
    check the manifest's signature of the computation owner.

    TODO explain how Cosmian cannot change the participants list because
    it's signed by the enclave / check enclave public key / check manifest signature.
    """
    data_provider = DataProviderAPI(cosmian_token)

    computation = data_provider.get_computation(computation['uuid'])

    """
    To send your data, you first need to generate a symetric key. The Cosmian client
    provides a function for that, but you can use whatever suit's your security needs.
    *TODO explain what type of key is required*
    """
    from cosmian_client_sgx.crypto.helper import random_symkey
    symetric_key = random_symkey()

    """
    You can next send your encrypted data
    """
    data_provider.push_files(computation['uuid'], symetric_key, [path_1, path_2])

    """
    When you have finished uploading your files, you need to tell it to the server so
    it knows data are ready
    """
    data_provider.done(computation['uuid'])

    """
    You also need to send your symetric key sealed with the public key of the enclave.
    """
    from cosmian_client_sgx.crypto.helper import seal
    sealed_symetric_key = seal(symetric_key, bytes(computation['enclave']['public_key'])) # TODO when Computation'll be a class and not a Dict we'll convert it before handling it to the client

    data_provider.key_provisioning(computation['uuid'], sealed_symetric_key)


def step_7_result_consumers_send_sealed_symetric_keys(cosmian_token, computation):
    """
    You need to check that the computation is correct. To do that, you can 
    fetch the status of the computation and read the enclave manifest. You can also
    check the manifest's signature of the computation owner.

    TODO explain how Cosmian cannot change the participants list because
    it's signed by the enclave / check enclave public key / check manifest signature.
    """
    result_consumer = ResultConsumerAPI(cosmian_token)

    computation = result_consumer.get_computation(computation['uuid'])

    """
    To fetch your results after the computation ran, you first need to generate a symetric key.
    The Cosmian client provides a function for that, but you can use whatever suit's your security needs.
    *TODO explain what type of key is required*
    """
    from cosmian_client_sgx.crypto.helper import random_symkey
    symetric_key = random_symkey()

    """
    You then need to send your symetric key sealed with the public key of the enclave.
    """
    from cosmian_client_sgx.crypto.helper import seal
    sealed_symetric_key = seal(symetric_key, bytes(computation['enclave']['public_key'])) # TODO when Computation'll be a class and not a Dict we'll convert it before handling it to the client

    result_consumer.key_provisioning(computation['uuid'], sealed_symetric_key)

    return symetric_key


def step_8_result_consumers_get_results(cosmian_token, computation, symetric_key):
    """
    When the computation is over, you can fetch the results.
    """
    result_consumer = ResultConsumerAPI(cosmian_token)

    encrypted_results = result_consumer.fetch_results(computation['uuid'])
    print(encrypted_results)

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