"""setup module."""

from pathlib import Path

from setuptools import setup, find_packages

setup(name="cosmian_secure_computation_client",
      version="0.5.0",
      url="https://cosmian.com",
      license="MIT",
      author="Cosmian Tech",
      author_email="tech@cosmian.com",
      long_description=Path("README.md").read_text(),
      long_description_content_type="text/markdown",
      python_requires=">=3.8.0",
      description="Python client library for Cosmian Secure Computation",
      packages=find_packages(),
      zip_safe=True,
      install_requires=[
          "requests>=2.28.1,<3.0.0", "pynacl>=1.5.0,<1.6.0",
          "cryptography>=38.0.1,<39.0.0", "pyjwt>=2.5.0,<2.6.0",
          "urllib3>=1.26.12,<1.27.0"
      ],
      tests_require=["pytest>=7.1.3,<7.2.0"],
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Console", "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9"
      ])
