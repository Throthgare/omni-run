#!/usr/bin/env python3
"""
Smart Launcher v3.0 - Ultimate Multi-Platform Executable Discovery and Management System

Setup script for PyPI packaging.
"""

from setuptools import setup, find_packages
import os

# Read README for long description
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="omni-run",
    version="3.0.0",
    author="Throthgare",
    author_email="realmselection@gmail.com",
    description="Ultimate Multi-Platform Executable Discovery and Management System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Throthgare/omni-run",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Software Distribution",
        "Topic :: Utilities",
    ],
    keywords="development launcher executable discovery automation dependencies framework cli tool",
    python_requires=">=3.8",
    install_requires=[
        "PyYAML>=6.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "watch": [
            "watchdog>=2.1.0",
        ],
        "all": [
            "watchdog>=2.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "omni-run=omni_run:main",
            "or=omni_run:main",  # Short alias
        ],
    },
    include_package_data=True,
    zip_safe=False,
    project_urls={
        "Bug Reports": "https://github.com/Throthgare/omni-run/issues",
        "Source": "https://github.com/Throthgare/omni-run",
        "Documentation": "https://github.com/Throthgare/omni-run#readme",
        "PyPI": "https://pypi.org/project/omni-run/",
    },
)