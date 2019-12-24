"""The main module for the wav_file_util cmdline script that handles code entry point.

"""

from wav_file_util.wav_file import WavFile
from wav_file_util.generation import wave_forms_by_name

import click


def remove_left_channel(channel_index, sample_value):
        if channel_index == 1:
            return 0
        else:
            return sample_value


def remove_right_channel(channel_index, sample_value):
        if channel_index == 0:
            return 0
        else:
            return sample_value


@click.command()
@click.option('-l', '--no-right-channel', 'nrc_file', default=None)
@click.option('-r', '--no-left-channel', 'nlc_file', default=None)
@click.option('-w', '--wave-type', type=click.Choice(list(wave_forms_by_name.keys())), default=None)
@click.option('-f', '--frequency', default=440)
@click.argument('out_filename', required=True)
def main(nrc_file, nlc_file, wave_type, frequency, out_filename):
    """Wave file utility program that will allow you to do one of several
    commands at a time. You can remove the right channel data from stereo
    wav file, remove the left, or generate a whole new wav file that
    contains a signal with a certain waveform and frequency.
    """
    if nrc_file is not None:
        in_wav_file = WavFile.open_existing(nrc_file)
        WavFile.create_new_wav_file_with_transformation(in_wav_file, out_filename, remove_right_channel)
        click.echo("Removed right channel from %s and output to %s" % (nrc_file, out_filename))
    elif nlc_file is not None:
        in_wav_file = WavFile.open_existing(nlc_file)
        WavFile.create_new_wav_file_with_transformation(in_wav_file, out_filename, remove_left_channel)
        click.echo("Removed left channel from %s and output to %s" % (nlc_file, out_filename))
    elif wave_type is not None:
        WavFile.create_new_wav_file_with_wave_form(out_filename, wave_forms_by_name[wave_type](frequency))
        click.echo("Generated wave form %s at %d Hz and output to %s" % (wave_type, frequency, out_filename))
    else:
        click.echo("No options passed!")
        with click.Context(main) as ctx:
            click.echo(main.get_help(ctx))

