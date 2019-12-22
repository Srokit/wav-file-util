"""The main module for the wav_reader script that handles code entry point.

"""

from sys import argv

from wav_reader.wav_file import WavFile


def main():
    """Code entry point. Called by wav_reader script declared in setup.py.

    """
    # argv[1] should be the wave filename
    wav_file = WavFile(argv[1])
    print("Wav file has no meta data errors!")

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

    wav_file.create_new_wav_file_with_transformation(remove_channel0, "test/wav_files/out/vocal_loop_1_no_right_channel.wav")
    wav_file.create_new_wav_file_with_transformation(remove_channel1, "test/wav_files/out/vocal_loop_1_no_left_channel.wav")
