"""setup module."""

from setuptools import setup, find_packages


setup(
    name="cosmian_client_sgx",
    version="1.0.0",
    python_requires=">=3.8.0",
    description="Interaction with the REST API of Cosmian Confidential Microservice",
    packages=find_packages(),
    zip_safe=True,
    entry_points={
        "console_scripts": [
            "cosmian_client_sgx = cosmian_client_sgx.cli:main"
        ]
    },
    install_requires=[
        "requests>=2.27.0,<3.0.0",
        "pynacl>=1.5.0,<1.6.0",
        "cryptography>=36.0.1,<37.0.0"
    ],
    test_requires=[
        "pytest>=7.0.0,<8.0.0"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9"
    ]
)
