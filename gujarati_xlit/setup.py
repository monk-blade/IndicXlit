"""
Setup script for Gujarati Transliteration Engine
"""
from setuptools import setup, find_packages
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text(encoding='utf-8')

setup(
    name="gujarati-xlit",
    version="1.0.0",
    description="Minimal Gujarati Transliteration Server - Roman to Gujarati and vice versa",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Based on AI4Bharat IndicXlit",
    author_email="",
    url="https://github.com/AI4Bharat/IndicXlit",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask>=2.0.0",
        "fairseq>=0.12.0",
        "ujson>=5.0.0",
        "pydload>=1.0.0",
        "indic-nlp-library>=0.91",
        "torch>=1.10.0",
        "sacremoses>=0.0.43",
        "tqdm>=4.62.0",
    ],
    python_requires='>=3.8',
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    entry_points={
        'console_scripts': [
            'gujarati-xlit-server=server:main',
            'gujarati-xlit-cli=cli:main',
        ],
    },
    keywords='gujarati transliteration indic nlp ai4bharat',
)
