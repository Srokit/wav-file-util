"""The main module for the wav_reader script that handles code entry point.

"""

from sys import argv

from wav_reader.wav_file import WavFile


def main():
    """Code entry point. Called by wav_reader script declared in setup.py.

    """
    # argv[1] should be the wave filename
    wav_file = WavFile(argv[1])
    is_meta_data_valid, meta_data_errors = wav_file.validate_meta_data()
    if not is_meta_data_valid:
        print("Wav file meta data errors:")
        for err in meta_data_errors:
            print(err)
    else:
        print("Wav file has no meta data errors!")

