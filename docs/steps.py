from os import environ
import os
from pathlib import Path
import time
import pprint
from cosmian_secure_computation_client.crypto.context import CryptoContext


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
    from cosmian_secure_computation_client import ComputationOwnerAPI
    computation_owner = ComputationOwnerAPI(cosmian_token)

    """
    To create a computation, you need to pass :
    - the name of the computation
    - the list of participants and their associated roles
    """
    
    """
    Create your computation :
    You will be the Computation Owner of this computation.
    """
    computation = computation_owner.create_computation(
        'computation name',
        code_provider_email="john@example.org",
        data_providers_emails=["john@example.org"],
        result_consumers_emails=["john@example.org"]
    )

    """
    Then generate three random words. They are you shared secret with all participants.
    Cosmian will never ask for it.
    Send them to your participants by mail, phone or any other mean.
    """
    from cosmian_secure_computation_client.util.mnemonic import random_words
    words = random_words()

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
    

    return computation, words

def step_2_code_provider_registers(cosmian_token, computation_uuid, words):
    """
    You need to create the CodeProvider object to register as a code provider.
    """
    from cosmian_secure_computation_client import CodeProviderAPI
    crypto_context = CryptoContext(words=words)
    code_provider = CodeProviderAPI(cosmian_token, crypto_context)

    """
    To register, pass the UUID of the computation given on the interface and
    your public public key for your role on this computation.
    """

    computation = code_provider.register(computation_uuid)

    return crypto_context

def step_2_data_providers_register(cosmian_token, computation_uuid, words):
    """
    You need to create the DataProvider object to register as a data provider.
    """
    from cosmian_secure_computation_client import DataProviderAPI
    crypto_context = CryptoContext(words=words)
    data_provider = DataProviderAPI(cosmian_token, crypto_context)

    """
    To register, you need to pass the UUID of the computation given on the interface and
    your public public key for your role on this computation.
    """

    computation = data_provider.register(computation_uuid)

    return crypto_context

def step_2_result_consumers_register(cosmian_token, computation_uuid, words):
    """
    You need to create the ResultConsumer object to register as a result consumer.
    """
    from cosmian_secure_computation_client import ResultConsumerAPI
    crypto_context = CryptoContext(words=words)
    result_consumer = ResultConsumerAPI(cosmian_token, crypto_context)

    """
    To register, you need to pass the UUID of the computation given on the interface and
    your public public key for your role on this computation.
    """

    computation = result_consumer.register(computation_uuid)

    return crypto_context

def step_3_code_provider_sends_code(cosmian_token, crypto_context, computation_uuid, path):
    """
    As a code provider, you will send code to the enclave.
    This folder should contains a `run.py` file.
    The `run.py` file will not be encrypted, everything else will be.
    """
    from cosmian_secure_computation_client import CodeProviderAPI
    code_provider = CodeProviderAPI(cosmian_token, crypto_context)

    code_provider.upload(computation_uuid, path)

def step_4_code_provider_sends_sealed_symmetric_key(cosmian_token, crypto_context, computation_uuid):
    """
    You need to check that the computation is correct :
    > You can fetch computation's status and read the enclave manifest.
    > You can check computation owner's signature from the manifest (not available yet).

    The SGX enclave used for the computation provides a few information about the 
    security of the process. You can access these informations from the computation
    object.
    """
    from cosmian_secure_computation_client import CodeProviderAPI
    code_provider = CodeProviderAPI(cosmian_token, crypto_context)

    while True:
        computation = code_provider.get_computation(computation_uuid)
        if computation.enclave.identity is None:
            print("Waiting 5s the generation of the enclave identity…")
            time.sleep(5)
        else:
            break

    manifest = computation.enclave.identity.manifest
    quote = computation.enclave.identity.quote

    """
    Cosmian will provide a function to check the validity of these data by using DCAP
    https://github.com/intel/SGXDataCenterAttestationPrimitives

    For now, you can do your own checks or wait for us to provide the helpers.

    To approve the computation, send your symmetric key sealed with enclave's public key.

    You need to use the same symmetric key as in step 3 (code upload).
    """
    code_provider.key_provisioning(computation.uuid, computation.enclave.identity.public_key)

def step_5_data_providers_send_data_and_sealed_symmetric_keys(cosmian_token, crypto_context, computation_uuid, path_1, path_2):
    """
    You need to check that the computation is correct :
    > You can fetch computation's status and read the enclave manifest.
    > You can check computation owner's signature from the manifest.

    The SGX enclave used for the computation provides a few information about the 
    security of the process. You can access these informations from the computation
    object.
    """
    from cosmian_secure_computation_client import DataProviderAPI
    data_provider = DataProviderAPI(cosmian_token, crypto_context)

    while True:
        computation = data_provider.get_computation(computation_uuid)
        if computation.enclave.identity is None:
            print("Waiting 5s the generation of the enclave identity…")
            time.sleep(5)
        else:
            break

    manifest = computation.enclave.identity.manifest
    quote = computation.enclave.identity.quote

    """
    Cosmian will provide a function to check the validity of these data by using DCAP
    https://github.com/intel/SGXDataCenterAttestationPrimitives

    For now, you can do your own checks or wait for us to provide the helpers.
    """

    """
    As a data provider, you will send data to the enclave.
    """
    data_provider.push_files(computation_uuid, [path_1, path_2])

    """
    When you're done uploading your files, notify the server so it knows that data are ready :
    """
    data_provider.done(computation_uuid)

    """
    > Finally, send your symmetric key sealed with enclave's public key :
    """
    data_provider.key_provisioning(computation_uuid, computation.enclave.identity.public_key)


def step_6_result_consumers_send_sealed_symmetric_keys(cosmian_token, crypto_context, computation_uuid):
    """
    You need to check that the computation is correct :
    > You can fetch computation's status and read the enclave manifest.
    > You can check computation owner's signature from the manifest.

    The SGX enclave used for the computation provides a few information about the 
    security of the process. You can access these informations from the computation
    object.
    """
    from cosmian_secure_computation_client import ResultConsumerAPI
    result_consumer = ResultConsumerAPI(cosmian_token, crypto_context)

    while True:
        computation = result_consumer.get_computation(computation_uuid)
        if computation.enclave.identity is None:
            print("Waiting 5s the generation of the enclave identity…")
            time.sleep(5)
        else:
            break

    manifest = computation.enclave.identity.manifest
    quote = computation.enclave.identity.quote

    """
    Cosmian will provide a function to check the validity of these data by using DCAP
    https://github.com/intel/SGXDataCenterAttestationPrimitives

    For now, you can do your own checks or wait for us to provide the helpers.
    """

    """
    As a result consumer, you will retrieve results after computation's run. But before,
    you have to send you symmetric key, sealed with enclave's public key :
    """
    result_consumer.key_provisioning(computation.uuid, computation.enclave.identity.public_key)


def step_7_result_consumers_get_results(cosmian_token, crypto_context, computation_uuid):
    """
    When the computation is over, you can fetch results.
    """
    from cosmian_secure_computation_client import ResultConsumerAPI
    result_consumer = ResultConsumerAPI(cosmian_token, crypto_context)

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
    results = result_consumer.ctx.decrypt(encrypted_results)

    print(results)


print("### step_1_create_computation")
computation, words = step_1_create_computation()

pp = pprint.PrettyPrinter(indent=2)
pp.pprint(computation)

print("Sleeping on Docker creation…")
time.sleep(5)

print("Continuing…")
cosmian_token = environ.get('COSMIAN_TOKEN')

print("### step_2_code_provider_registers")
code_provider_crypto_context = step_2_code_provider_registers(cosmian_token, computation.uuid, words)

print("### step_2_data_providers_register")
data_provider_crypto_context = step_2_data_providers_register(cosmian_token, computation.uuid, words)

print("### step_2_result_consumers_register")
result_consumer_crypto_context = step_2_result_consumers_register(cosmian_token, computation.uuid, words)

print("### step_3_code_provider_sends_code")
step_3_code_provider_sends_code(cosmian_token, code_provider_crypto_context, computation.uuid, Path(os.path.dirname(__file__) + "/../tests/data/cp/enclave-join"))

print("### step_4_code_provider_sends_sealed_symmetric_key")
step_4_code_provider_sends_sealed_symmetric_key(cosmian_token, code_provider_crypto_context, computation.uuid)

print("### step_5_data_providers_send_data_and_sealed_symmetric_keys")
step_5_data_providers_send_data_and_sealed_symmetric_keys(cosmian_token, data_provider_crypto_context, computation.uuid, Path(os.path.dirname(__file__) + "/../tests/data/dp1/A.csv"), Path(os.path.dirname(__file__) + "/../tests/data/dp2/B.csv"))

print("### step_6_result_consumers_send_sealed_symmetric_keys")
step_6_result_consumers_send_sealed_symmetric_keys(cosmian_token, result_consumer_crypto_context, computation.uuid)

print("### step_7_result_consumers_get_results")
step_7_result_consumers_get_results(cosmian_token, result_consumer_crypto_context, computation.uuid)
