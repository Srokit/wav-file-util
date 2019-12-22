"""Wav file class is described in this module.

"""

import struct
import copy


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

    NUM_SAMPLES_DEFAULT = 2000000 # 2 Mill TODO: Make this more appropriate
    FORMAT_CHUNK_SAMPLE_RATE_DEFAULT = 8000 # 8 kHz TODO: Make better
    BYTES_PER_SAMPLE_DEFAULT = 3 # Because that was the number I saw in one wav file

    @classmethod
    def make_default_meta_data(cls):
        bytes_of_audio_data = cls.NUM_SAMPLES_DEFAULT * cls.FORMAT_CHUNK_NUM_CHANNELS_EXPECTED * cls.BYTES_PER_SAMPLE_DEFAULT
        meta_data = WavFileMetaData()
        meta_data.super_chunk_id = cls.SUPER_CHUNK_ID_EXPECTED
        # There are 8 (super_chunk_id and super_chunk_size itself) not included in super_chunk_size
        meta_data.super_chunk_size = cls.NUM_BYTES_BEFORE_DATA - 8 + bytes_of_audio_data
        meta_data.super_chunk_format = cls.SUPER_CHUNK_FORMAT_EXPECTED
        meta_data.format_chunk_id = cls.FORMAT_CHUNK_ID_EXPECTED
        meta_data.format_chunk_size = cls.FORAMT_CHUNK_SIZE_EXPECTED
        meta_data.format_chunk_audio_format = cls.FORMAT_CHUNK_AUDIO_FORMAT_EXPECTED
        meta_data.format_chunk_num_channels = cls.FORMAT_CHUNK_NUM_CHANNELS_EXPECTED
        meta_data.format_chunk_sample_rate = cls.FORMAT_CHUNK_SAMPLE_RATE_DEFAULT

        meta_data.format_chunk_byte_rate = cls.FORMAT_CHUNK_SAMPLE_RATE_DEFAULT * \
                cls.BYTES_PER_SAMPLE_DEFAULT * cls.FORMAT_CHUNK_NUM_CHANNELS_EXPECTED
        meta_data.format_chunk_block_align = cls.BYTES_PER_SAMPLE_DEFAULT \
                * cls.FORMAT_CHUNK_NUM_CHANNELS_EXPECTED
        meta_data.format_chunk_bits_per_sample = cls.BYTES_PER_SAMPLE_DEFAULT * 8
        meta_data.data_chunk_id = cls.DATA_CHUNK_ID_EXPECTED
        meta_data.data_chunk_size = bytes_of_audio_data 
        return meta_data

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

    # How many audio samples are loaded into memory at a time when streaming wav file data
    SAMPLES_PER_BLOCK = 1000

    @classmethod
    def create_new_wav_file_with_transformation(cls, src_wav_file, dest_wav_file, trans_func=None):
        """Apply trans_func to each sample and all the channels for that sample if
        trans_func is None then the new wav file will be an exact copy.
        trans_func should accept channel_index: int and sample_value: int as paramaters
        uses src_wav_file as file data input and dest_wav_file as the file to output to
        """
        write_file = open(dest_wav_file.filename, 'wb')
        # Copy the meta data object from source file
        dest_wav_file.meta_data = copy.deepcopy(src_wav_file.meta_data)
        dest_wav_file.meta_data_bytes = src_wav_file.meta_data_bytes
        # Write the meta data to disk
        write_file.write(dest_wav_file.meta_data_bytes)
        with open(src_wav_file.filename, 'rb') as wav_file_obj:
            wav_file_obj.seek(WavFileMetaData.NUM_BYTES_BEFORE_DATA_STARTS)
            bytes_per_block = src_wav_file._get_read_block_size()
            struct_format_str, padding = src_wav_file._get_per_sample_struct_format_str_and_padding()
            while True:
                data = bytearray(wav_file_obj.read(bytes_per_block))
                channel_index = 0
                bytes_per_sample = src_wav_file.meta_data.format_chunk_bits_per_sample // 8
                for sample_offset in range(0, len(data), bytes_per_sample):
                    sample_value = int(struct.unpack_from(struct_format_str, data[sample_offset:sample_offset+bytes_per_sample]+padding)[0])
                    channel_index = (channel_index + 1) % src_wav_file.meta_data.format_chunk_num_channels
                    if trans_func is not None:
                        sample_value = trans_func(channel_index, sample_value)
                    data[sample_offset:sample_offset+bytes_per_sample] = struct.pack(struct_format_str, sample_value)[:-len(padding)]
                    write_file.write(bytes(data[sample_offset:sample_offset+bytes_per_sample])) 
                if len(data) < bytes_per_block:
                    break
        write_file.close()

    def __init__(self, filename):
        self.filename = filename
        self.meta_data = None


    def read_meta_data_from_disk(self):
        with open(self.filename, 'rb') as wav_file_obj:
            # Meta data bytes is used in applying transformations as the meta data bytes are copied
            self.meta_data_bytes = wav_file_obj.read(WavFileMetaData.NUM_BYTES_BEFORE_DATA_STARTS)
        self.meta_data = self._parse_meta_data(self.meta_data_bytes)
        is_meta_data_valid, err_str = self._validate_meta_data()
        assert is_meta_data_valid, err_str

    # Private helpers

    def _validate_meta_data(self):
        """Returns bool, str combo. The string is the error(s)
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
        if self.meta_data.format_chunk_bits_per_sample % 8 != 0:
            success = False
            errors.append("format_chunk_bits_per_sample | actual: Not divisble by 8 expected: divisible by 8")
        err_str = "Wav file metadata errors:\n  " + '\n  '.join(errors) if errors else None
        return success, err_str

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
        meta_data.format_chunk_bits_per_sample = struct.unpack_from('<H',
                meta_data_bytes[WavFileMetaData.FORMAT_CHUNK_BITS_PER_SAMPLE_OFFSET:WavFileMetaData.FORMAT_CHUNK_BITS_PER_SAMPLE_OFFSET + 2])[0]
        meta_data.data_chunk_id = struct.unpack_from('>I',
                meta_data_bytes[WavFileMetaData.DATA_CHUNK_ID_OFFSET:WavFileMetaData.DATA_CHUNK_ID_OFFSET + 4])[0]
        meta_data.data_chunk_size = struct.unpack_from('<I',
                meta_data_bytes[WavFileMetaData.DATA_CHUNK_SIZE_OFFSET:WavFileMetaData.DATA_CHUNK_SIZE_OFFSET + 4])[0]
        return meta_data

    def _get_read_block_size(self):
        """Returns the number of bytes that should be processed at a time from
        the wav file which is based on some of the metadata so that we do not
        unalign with the samples.
        """
        return WavFile.SAMPLES_PER_BLOCK * self.meta_data.format_chunk_num_channels * self.meta_data.format_chunk_bits_per_sample // 8

    def _get_per_sample_struct_format_str_and_padding(self):
        """Returns the string that should be used as the first argument to
        struct.unpack_from because this will differ depending on the number of
        bits per sample as well as the padding of 0's bytes that is required for
        the pack to work.

        """
        bytes_per_sample = self.meta_data.format_chunk_bits_per_sample // 8
        if bytes_per_sample == 1:
            fmt = '<c'
            padding = bytearray(0)
        if bytes_per_sample == 2:
            fmt = '<H'
            padding = bytearray(0)
        if bytes_per_sample <= 4:
            fmt = '<I'
            padding = bytearray(4 - bytes_per_sample)
        else: # bytes_per_sample > 4
            fmt = bytearray(8 - bytes_per_sample)
            padding = bytearray(8 - bytes_per_sample)
        return fmt, padding
