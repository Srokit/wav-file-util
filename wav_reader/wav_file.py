"""Wav file class is described in this module.

"""

import struct


class WavFileMetaData:
    """The class containing observed wav file metadata as well as constants
    that are used to find the right offset to read data from wav file and
    to check correct formatting of expected values.

    """

    NUM_BYTES_BEFORE_DATA_STARTS = 44

    # WAV meta data byte offset from start of file
    SUPER_CHUNK_ID_OFFSET = 0
    SUPER_CHUNK_SIZE_OFFSET = 4
    SUPER_CHUNK_FORMAT_OFFSET = 8

    FORMAT_CHUNK_ID_OFFSET = 12
    FORMAT_CHUNK_SIZE_OFFSET = 16
    FORMAT_CHUNK_AUDIO_FORMAT_OFFSET = 20
    FORMAT_CHUNK_NUM_CHANNELS_OFFSET = 22
    FORMAT_CHUNK_SAMPLE_RATE_OFFSET = 24
    FORMAT_CHUNK_BYTE_RATE_OFFSET = 28
    FORMAT_CHUNK_BLOCK_ALIGN_OFFSET = 32
    FORMAT_CHUNK_BITS_PER_SAMPLE_OFFSET = 34

    DATA_CHUNK_ID_OFFSET = 36
    DATA_CHUNK_SIZE_OFFSET = 40
    DATA_CHUNK_DATA_OFFSET = 44 # Actual sound data starts here

    # WAV meta data expected values to ensure correct format in WAV files
    SUPER_CHUNK_ID_EXPECTED = 0x52494646 # "RIFF" in ascii (Big-endian)
    SUPER_CHUNK_FORMAT_EXPECTED = 0x57415645 # "WAVE" in ascii (Big-endian)

    FORMAT_CHUNK_ID_EXPECTED = 0x666D7420 # "fmt " in ascii (Big-endian)
    FORMAT_CHUNK_SIZE_EXPECTED = 16

    FORMAT_CHUNK_AUDIO_FORMAT_EXPECTED = 1 # PCM (Linear)
    FORMAT_CHUNK_NUM_CHANNELS_EXPECTED = 2 # Stereo

    DATA_CHUNK_ID_EXPECTED = 0x64617461 # "data" in ascii (Big-endian)

    def __init__(self):
        self.super_chunk_id = 0x0
        self.super_chunk_size = 0x0
        self.super_chunk_format = 0x0
        self.format_chunk_id = 0x0
        self.format_chunk_size = 0x0
        self.format_chunk_audio_format = 0x0
        self.format_chunk_num_channels = 0x0
        self.format_chunk_sample_rate = 0x0
        self.format_chunk_byte_rate = 0x0
        self.format_chunk_block_align = 0x0
        self.format_chunk_bits_per_sample = 0x0
        self.data_chunk_id = 0x0
        self.data_chunk_size = 0x0


class WavFile:
    """The class that represents a wav file read from dics. Also the class that
    contains methods to validate data.

    """

    def __init__(self, filename):

        with open(filename, 'rb') as wav_file_obj:
            meta_data_bytes = wav_file_obj.read(WavFileMetaData.NUM_BYTES_BEFORE_DATA_STARTS)
        self.meta_data = self._parse_meta_data(meta_data_bytes)


    def validate_meta_data(self):
        """Returns bool, List[string] combo. The list of strings are the error
            that occured or None if no errors. The bool is true on no errors but
            false if there were errors.
        """
        success = True
        errors = []
        if self.meta_data.super_chunk_id != WavFileMetaData.SUPER_CHUNK_ID_EXPECTED:
            success = False
            errors.append("super_chunk_id | actual = %d expected = %d" %
                    (self.meta_data.super_chunk_id, WavFileMetaData.SUPER_CHUNK_ID_EXPECTED))
        if self.meta_data.super_chunk_format != WavFileMetaData.SUPER_CHUNK_FORMAT_EXPECTED:
            success = False
            errors.append("super_chunk_format | actual = %d expected = %d" %
                    (self.meta_data.super_chunk_format, WavFileMetaData.SUPER_CHUNK_FORMAT_EXPECTED))
        if self.meta_data.format_chunk_id != WavFileMetaData.FORMAT_CHUNK_ID_EXPECTED:
            success = False
            errors.append("format_chunk_id | actual = %d expected = %d" %
                    (self.meta_data.format_chunk_id, WavFileMetaData.FORMAT_CHUNK_ID_EXPECTED))
        if self.meta_data.format_chunk_size != WavFileMetaData.FORMAT_CHUNK_SIZE_EXPECTED:
            success = False
            errors.append("format_chunk_size | actual = %d expected = %d" %
                    (self.meta_data.format_chunk_size, WavFileMetaData.FORMAT_CHUNK_SIZE_EXPECTED))
        if self.meta_data.format_chunk_audio_format != WavFileMetaData.FORMAT_CHUNK_AUDIO_FORMAT_EXPECTED:
            success = False
            errors.append("format_chunk_audio_format | actual = %d expected = %d" %
                    (self.meta_data.format_chunk_audio_format, WavFileMetaData.FORMAT_CHUNK_AUDIO_FORMAT_EXPECTED))
        if self.meta_data.format_chunk_num_channels != WavFileMetaData.FORMAT_CHUNK_NUM_CHANNELS_EXPECTED:
            success = False
            errors.append("format_chunk_num_channels | actual = %s expected = %d" %
                    (self.meta_data.format_chunk_num_channels, WavFileMetaData.FORMAT_CHUNK_NUM_CHANNELS_EXPECTED))
        if self.meta_data.data_chunk_id != WavFileMetaData.DATA_CHUNK_ID_EXPECTED:
            success = False
            errors.append("data_chunk_id | actual = %d expected = %d" %
                    (self.meta_data.data_chunk_id, WavFileMetaData.DATA_CHUNK_ID_EXPECTED))
        return success, errors or None


    # Priavte helpers

    def _parse_meta_data(self, meta_data_bytes):
        """Helpers used in ctor that creates the WavFileMetaData object used by WavFile class.
        """
        meta_data = WavFileMetaData()
        meta_data.super_chunk_id = struct.unpack_from('>I',
                meta_data_bytes[WavFileMetaData.SUPER_CHUNK_ID_OFFSET:WavFileMetaData.SUPER_CHUNK_ID_OFFSET + 4])[0]
        meta_data.super_chunk_size = struct.unpack_from('<I',
                meta_data_bytes[WavFileMetaData.SUPER_CHUNK_SIZE_OFFSET:WavFileMetaData.SUPER_CHUNK_FORMAT_OFFSET + 4])[0]
        meta_data.super_chunk_format = struct.unpack_from('>I',
                meta_data_bytes[WavFileMetaData.SUPER_CHUNK_FORMAT_OFFSET:WavFileMetaData.FORMAT_CHUNK_ID_OFFSET + 4])[0]
        meta_data.format_chunk_id = struct.unpack_from('>I',
                meta_data_bytes[WavFileMetaData.FORMAT_CHUNK_ID_OFFSET:WavFileMetaData.FORMAT_CHUNK_ID_OFFSET + 4])[0]

        meta_data.format_chunk_size = struct.unpack_from('<I',
                meta_data_bytes[WavFileMetaData.FORMAT_CHUNK_SIZE_OFFSET:WavFileMetaData.FORMAT_CHUNK_SIZE_OFFSET + 4])[0]
        meta_data.format_chunk_audio_format = struct.unpack_from('<H',
                meta_data_bytes[WavFileMetaData.FORMAT_CHUNK_AUDIO_FORMAT_OFFSET:WavFileMetaData.FORMAT_CHUNK_AUDIO_FORMAT_OFFSET + 2])[0]
        meta_data.format_chunk_num_channels = struct.unpack_from('<H',
                meta_data_bytes[WavFileMetaData.FORMAT_CHUNK_NUM_CHANNELS_OFFSET:WavFileMetaData.FORMAT_CHUNK_NUM_CHANNELS_OFFSET + 2])[0]
        meta_data.format_chunk_sample_rate = struct.unpack_from('<I',
                meta_data_bytes[WavFileMetaData.FORMAT_CHUNK_SAMPLE_RATE_OFFSET:WavFileMetaData.FORMAT_CHUNK_SAMPLE_RATE_OFFSET + 4])[0]
        meta_data.format_chunk_byte_rate = struct.unpack_from('<I',
                meta_data_bytes[WavFileMetaData.FORMAT_CHUNK_BYTE_RATE_OFFSET:WavFileMetaData.FORMAT_CHUNK_BYTE_RATE_OFFSET + 4])[0]
        meta_data.format_chunk_block_align = struct.unpack_from('<H',
                meta_data_bytes[WavFileMetaData.FORMAT_CHUNK_BLOCK_ALIGN_OFFSET:WavFileMetaData.FORMAT_CHUNK_BLOCK_ALIGN_OFFSET + 2])[0]
        meta_data.format_chunk_bits_per_sample_offset = struct.unpack_from('<H',
                meta_data_bytes[WavFileMetaData.FORMAT_CHUNK_BITS_PER_SAMPLE_OFFSET:WavFileMetaData.FORMAT_CHUNK_BITS_PER_SAMPLE_OFFSET + 2])[0]
        meta_data.data_chunk_id = struct.unpack_from('>I',
                meta_data_bytes[WavFileMetaData.DATA_CHUNK_ID_OFFSET:WavFileMetaData.DATA_CHUNK_ID_OFFSET + 4])[0]
        meta_data.data_chunk_size = struct.unpack_from('<I',
                meta_data_bytes[WavFileMetaData.DATA_CHUNK_SIZE_OFFSET:WavFileMetaData.DATA_CHUNK_SIZE_OFFSET + 4])[0]
        return meta_data

