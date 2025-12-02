from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="crypto-portfolio-tracker",
    version="3.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Advanced cryptocurrency portfolio management and tax calculation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mgenrique/crypto_tracker",
    project_urls={
        "Bug Tracker": "https://github.com/mgenrique/crypto_tracker/issues",
        "Documentation": "https://github.com/mgenrique/crypto_tracker/wiki",
        "Source Code": "https://github.com/mgenrique/crypto_tracker",
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial",
    ],
    python_requires=">=3.10",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "sqlalchemy>=2.0.0",
        "web3>=6.0.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.7.0",
        ],
        "test": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "crypto-tracker=main:app",
        ],
    },
)
