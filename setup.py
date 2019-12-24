from setuptools import setup

setup(
    name="wav_file_util",
    version='1.0',
    description="Reads wav files and outputs information about them",
    author="Stan Rokita",
    author_email="srok35@gmail.com",
    packages=["wav_file_util"],
    extras_require={
        'dev': ['pylint']
    },
    entry_points={
        'console_scripts': [
            'wav_file_util = wav_file_util.__main__:main'
        ]
    }
)

