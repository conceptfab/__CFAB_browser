"""
Setup script for Rust Scanner
"""
from setuptools import setup
from pyo3_setuptools_rust import Cargo, RustExtension

setup(
    name="scanner-rust",
    version="0.1.0",
    author="CFAB Browser",
    author_email="developer@cfab.com",
    description="Rust implementation of asset scanner for CFAB Browser",
    long_description=open("README.md", "r", encoding="utf-8").read() if __name__ == "__main__" else "",
    long_description_content_type="text/markdown",
    url="https://github.com/cfab-browser/scanner-rust",
    rust_extensions=[RustExtension("scanner_rust.scanner_rust", "Cargo.toml")],
    packages=["scanner_rust"],
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[
        "pyo3>=0.20.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Rust",
    ],
) 