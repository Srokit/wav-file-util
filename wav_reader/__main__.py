"""The main module for the wav_reader script that handles code entry point.

"""

from sys import argv

from wav_reader.wav_file import WavFile


def main():
    """Code entry point. Called by wav_reader script declared in setup.py.

    """
    # argv[1] should be the wave filename
    wav_file = WavFile.open_existing(argv[1])

    def remove_channel1(channel_index, sample_value):
        if channel_index == 1:
            return 0
        else:
            return sample_value

    def remove_channel0(channel_index, sample_value):
        if channel_index == 0:
            return 0
        else:
            return sample_value

    WavFile.create_new_wav_file_with_transformation(wav_file, "test/wav_files/out/vocal_loop_1_no_channel0.wav", remove_channel0)
    print("Created wav file: test/wav_files/out/vocal_loop_1_no_channel0.wav")
    WavFile.create_new_wav_file_with_transformation(wav_file, "test/wav_files/out/vocal_loop_1_no_channel1.wav", remove_channel0)
    print("Created wav file: test/wav_files/out/vocal_loop_1_no_channel1.wav")

