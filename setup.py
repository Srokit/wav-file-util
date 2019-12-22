from setuptools import setup

setup(
    name="wav_reader",
    version='1.0',
    description="Reads wav files and outputs information about them",
    author="Stan Rokita",
    author_email="srok35@gmail.com",
    packages=["wav_reader"],
    extras_require={
        'dev': ['pylint']
    }
)
