from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gptree",
    version="1.0.0",
    author="Basheq Tarifi",
    author_email="btarifi08@gmail.com",
    description="Flatten repos and generate trees for LLM contexts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/btarifi/gptree",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'gptree=src.cli:cli',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'click>=8.0',
        'pathspec>=0.9.0'
    ],
)