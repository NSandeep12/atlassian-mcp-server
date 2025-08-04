#!/usr/bin/env python3
"""
Setup script for Atlassian MCP Server
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open(os.path.join(this_directory, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="atlassian-mcp-server",
    version="1.0.0",
    author="Sandeep Nalam",
    author_email="nsandeep12@gmail.com",
    description="Model Context Protocol server for Atlassian products (Jira & Bitbucket) integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/atlassian-mcp-server",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/atlassian-mcp-server/issues",
        "Documentation": "https://github.com/yourusername/atlassian-mcp-server/blob/main/README.md",
        "Source Code": "https://github.com/yourusername/atlassian-mcp-server",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Office/Business :: Groupware",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "pre-commit>=3.0.0",
        ],
        "prod": [
            "uvicorn>=0.23.0",
            "gunicorn>=21.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "atlassian-mcp-server=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml", "*.json"],
    },
    keywords=[
        "mcp", "model-context-protocol", "atlassian", "jira", "bitbucket",
        "ai", "assistant", "amazon-q", "claude", "python", "docker"
    ],
    zip_safe=False,
)
