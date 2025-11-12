from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="visionguard",
    version="0.1.0",
    author="shuldeshoff",
    description="Микросервис для анализа видео с производственных камер",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shuldeshoff/visionguard",
    packages=find_packages(exclude=["tests*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.1",
            "black>=23.12.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
        ],
    },
)

