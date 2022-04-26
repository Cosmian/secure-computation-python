from typing import Optional, Dict, Union, List, Tuple

from cosmian_client_sgx import Computation, ComputationOwnerAPI, CodeProviderAPI, DataProviderAPI, ResultConsumerAPI
from os import environ
import os
from pathlib import Path
import time
import pprint
import struct

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
    import subprocess
    subprocess.Popen(['gpg', '--batch', '--passphrase', '', '--quick-generate-key', 'John Doe <john@example.org>', 'ed25519', 'cert', 'never'], stdout=subprocess.PIPE,  stderr=subprocess.PIPE, universal_newlines=True).communicate()
    public_key, stderr = subprocess.Popen(['gpg', '--export', '--armor', 'john@example.org'], stdout=subprocess.PIPE,  stderr=subprocess.PIPE, universal_newlines=True).communicate()

    """
    Create your computation :
    You will be the Computation Owner of this computation.
    """
    computation = computation_owner.create_computation(
        'computation name',
        owner_public_key=public_key,
        code_provider_email="john@example.org",
        data_providers_emails=["john@example.org"],
        result_consumers_emails=["john@example.org"]
    )

    """
    If you put emails of persons outside Cosmian, they will need to create an account 
    with the exact same email to join the computation.
    """
    if computation.code_provider.uuid is None:
        print(f"Code Provider {computation.code_provider.email} does not have a Cosmian account. Please invite him to create an account.")
    for data_provider in computation.data_providers:
        if data_provider.uuid is None:
            print(f"Data Provider {data_provider.email} does not have a Cosmian account. Please invite him to create an account.")

    for result_consumer in computation.result_consumers:
        if result_consumer.uuid is None:
            print(f"Result Consumer {result_consumer.email} does not have a Cosmian account. Please invite him to create an account.")
    

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
    import subprocess
    subprocess.Popen(['gpg', '--batch', '--passphrase', '', '--quick-generate-key', 'John Doe <john@example.org>', 'ed25519', 'cert', 'never'], stdout=subprocess.PIPE,  stderr=subprocess.PIPE, universal_newlines=True).communicate()
    public_key, stderr = subprocess.Popen(['gpg', '--export', '--armor', 'john@example.org'], stdout=subprocess.PIPE,  stderr=subprocess.PIPE, universal_newlines=True).communicate()

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
    You can generate a new PGP key for an alias of your email address "john+code_provider@example.org".

    /!\/!\/!\ WARNING /!\/!\/!\
    """
    import subprocess
    subprocess.Popen(['gpg', '--batch', '--passphrase', '', '--quick-generate-key', 'John Doe <john+code_provider@example.org>', 'ed25519', 'cert', 'never'], stdout=subprocess.PIPE,  stderr=subprocess.PIPE, universal_newlines=True).communicate()
    public_key, stderr = subprocess.Popen(['gpg', '--export', '--armor', 'john+code_provider@example.org'], stdout=subprocess.PIPE,  stderr=subprocess.PIPE, universal_newlines=True).communicate()

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
    import subprocess
    subprocess.Popen(['gpg', '--batch', '--passphrase', '', '--quick-generate-key', 'John Doe <john+data_provider@example.org>', 'ed25519', 'cert', 'never'], stdout=subprocess.PIPE,  stderr=subprocess.PIPE, universal_newlines=True).communicate()
    public_key, stderr = subprocess.Popen(['gpg', '--export', '--armor', 'john+data_provider@example.org'], stdout=subprocess.PIPE,  stderr=subprocess.PIPE, universal_newlines=True).communicate()

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
    You can generate a new PGP key for an alias of your email address "john+result_consumer@example.org".

    /!\/!\/!\ WARNING /!\/!\/!\
    """
    import subprocess
    subprocess.Popen(['gpg', '--batch', '--passphrase', '', '--quick-generate-key', 'John Doe <john+result_consumer@example.org>', 'ed25519', 'cert', 'never'], stdout=subprocess.PIPE,  stderr=subprocess.PIPE, universal_newlines=True).communicate()
    public_key, stderr = subprocess.Popen(['gpg', '--export', '--armor', 'john+result_consumer@example.org'], stdout=subprocess.PIPE,  stderr=subprocess.PIPE, universal_newlines=True).communicate()

    computation = result_consumer.register(computation_uuid, public_key)

def step_3_code_provider_sends_code(cosmian_token, computation_uuid, path):
    """
    As a code provider, you will send code to the enclave.
    > First, you have to generate a symmetric key. The Cosmian client
    provides a function for that, but you can also use whatever suit's your security needs.
    *TODO explain what type of key is required*

    You need to store this symmetric key somewhere safe. It'll be required later for you to send it to 
    the enclave.
    """
    from cosmian_client_sgx.crypto.helper import random_symkey
    symmetric_key = random_symkey()

    """
    > Next, upload your code folder, specifying its path.
    This folder should contains a `run.py` file.
    The `run.py` file will not be encrypted, everything else will be.
    """
    from cosmian_client_sgx import CodeProviderAPI
    code_provider = CodeProviderAPI(cosmian_token)

    code_provider.upload(computation_uuid, symmetric_key, path)

    return symmetric_key

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
    is already done when he sends his sealed symmetric key.

    If, as in the example, you send only the string "Missing Signature", the other participants
    will see this. You can also sign the manifest and the quote with your PGP key and tell the other
    participants to check this.
    """
    computation_owner.approve_participants(computation.uuid, "Missing Signature")

def step_5_code_provider_sends_sealed_symmetric_key(cosmian_token, computation_uuid, symmetric_key):
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

    To approve the computation, send your symmetric key sealed with enclave's public key.

    You need to use the same symmetric key as in step 3 (code upload).
    """
    from cosmian_client_sgx.crypto.helper import seal
    sealed_symmetric_key = seal(symmetric_key, computation.enclave.public_key)

    code_provider.key_provisioning(computation.uuid, sealed_symmetric_key)

def step_6_data_providers_send_data_and_sealed_symmetric_keys(cosmian_token, computation_uuid, path_1, path_2):
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
    > First, you have to generate a symmetric key. The Cosmian client
    provides a function for that, but you can also use whatever suit's your security needs.
    *TODO explain what type of key is required*
    """
    from cosmian_client_sgx.crypto.helper import random_symkey
    symmetric_key = random_symkey()

    """
    > Next, send your encrypted data to the enclave, specifying the different paths :
    """
    data_provider.push_files(computation_uuid, symmetric_key, [path_1, path_2])

    """
    When you're done uploading your files, notify the server so it knows that data are ready :
    """
    data_provider.done(computation_uuid)

    """
    > Finally, send your symmetric key sealed with enclave's public key :
    """
    from cosmian_client_sgx.crypto.helper import seal
    sealed_symmetric_key = seal(symmetric_key, computation.enclave.public_key)

    data_provider.key_provisioning(computation_uuid, sealed_symmetric_key)


def step_7_result_consumers_send_sealed_symmetric_keys(cosmian_token, computation_uuid):
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
    you have to send you symmetric key, sealed with enclave's public key :
    > First, you have to generate a symmetric key. The Cosmian client
    provides a function for that, but you can also use whatever suit's your security needs.
    *TODO explain what type of key is required*
    """
    from cosmian_client_sgx.crypto.helper import random_symkey
    symmetric_key = random_symkey()

    """
    > Next, send your symmetric key sealed with enclave's public key :
    """
    from cosmian_client_sgx.crypto.helper import seal
    sealed_symmetric_key = seal(symmetric_key, computation.enclave.public_key)

    result_consumer.key_provisioning(computation.uuid, sealed_symmetric_key)

    return symmetric_key


def step_8_result_consumers_get_results(cosmian_token, computation_uuid, symmetric_key):
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

        if computation.runs.current is None and len(computation.runs.previous) == 0:
            """
            The computation didn't start running. Maybe you miss one of the previous states?
            You can check the UI or check if everything is set in the computation with Python.
            Right now it's a manual (and tedious) process, maybe in the future the API will
            provide a list of messages for the missing steps.
            """
            if computation.code_provider.public_key is None:
                print("Code Provider didn't register.")
            if computation.code_provider.code_uploaded_at is None:
                print("Code Provider didn't provide its code.")
            if computation.code_provider.symmetric_key_uploaded_at is None:
                print("Code Provider didn't send its sealed symmetric key.")

            for data_provider in computation.data_providers:
                if data_provider.public_key is None:
                    print(f"Data Provider {data_provider.email} didn't register.")
                if data_provider.done_uploading_at is None:
                    print(f"Data Provider {data_provider.email} is not done uploading data.")
                if data_provider.symmetric_key_uploaded_at is None:
                    print(f"Data Provider {data_provider.email} didn't send its sealed symmetric key.")

            for result_consumer in computation.result_consumers:
                if result_consumer.public_key is None:
                    print(f"Result Consumer {result_consumer.email} didn't register.")
                if result_consumer.symmetric_key_uploaded_at is None:
                    print(f"Result Consumer {result_consumer.email} didn't send its sealed symmetric key.")

            return

        if len(computation.runs.previous) == 1:
            run = computation.runs.previous[0]

            """
            You can check a few information on the run to check
            if everything worked.
            """
            print("\n\n### Exit Code ###\n")
            print(run.exit_code)
            print("\n\n### stdout ###\n")
            print(run.stdout)
            print("\n\n### stderr ###\n")
            print(run.stderr)
            print("\n\n")

            if run.exit_code != 0:
                raise "Run fail."
            else:
                break
        else:
            print("Waiting 2s end of computation…")
            time.sleep(2)

    encrypted_results = result_consumer.fetch_results(computation.uuid)

    from cosmian_client_sgx.crypto.helper import decrypt
    results = decrypt(encrypted_results, symmetric_key)

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
    code_provider_symmetric_key = step_3_code_provider_sends_code(cosmian_token, computation.uuid, Path(os.path.dirname(__file__) + "/../tests/data/cp/enclave-join"))
    
    if until < 6: return

    print("### step_4_computation_owner_approves_participants")
    step_4_computation_owner_approves_participants(cosmian_token, computation.uuid)
    
    if until < 7: return

    print("### step_5_code_provider_sends_sealed_symmetric_key")
    step_5_code_provider_sends_sealed_symmetric_key(cosmian_token, computation.uuid, code_provider_symmetric_key)
    
    if until < 8: return

    print("### step_6_data_providers_send_data_and_sealed_symmetric_keys")
    step_6_data_providers_send_data_and_sealed_symmetric_keys(cosmian_token, computation.uuid, Path(os.path.dirname(__file__) + "/../tests/data/dp1/A.csv"), Path(os.path.dirname(__file__) + "/../tests/data/dp2/B.csv"))
    
    if until < 9: return

    print("### step_7_result_consumers_send_sealed_symmetric_keys")
    result_consumer_symmetric_key = step_7_result_consumers_send_sealed_symmetric_keys(cosmian_token, computation.uuid)

    if until < 10: return

    print("### step_8_result_consumers_get_results")
    step_8_result_consumers_get_results(cosmian_token, computation.uuid, result_consumer_symmetric_key)


def run_all():
    print(f"Seeding for {environ.get('SEED_EMAIL')}…\n\n")
    for i in range(1,11):
        print(f"\n\n###### Running until {i} ######\n")
        run(i)

run(10) if environ.get('SEED_EMAIL') is None else run_all()