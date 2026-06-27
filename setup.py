"""shared-models: Unified Pydantic v2 data contracts across all modules"""
from setuptools import setup, find_packages

setup(
    name="shared-models",
    version="0.1.0",
    description="Unified Pydantic v2 data models shared across the one-stop video generation platform",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=["pydantic>=2.7", "python-jose[cryptography]>=3.3", "passlib[bcrypt]>=1.7"],
)
