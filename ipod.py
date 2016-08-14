from suitcase.fields import UBInt8, UBInt16, UBInt32, UBInt56, UBInt8Sequence, \
    Magic, LengthField, SubstructureField, DispatchField, DispatchTarget, FieldProperty, Payload, CRCField
from suitcase.structure import Structure


def ipod_checksum(data, crc=0):
    return 0x100 - (sum(data) & 0xFF) - crc


class StringField(Structure):
    data = Payload()
    text = FieldProperty(data,
                         onget=lambda v: v.decode('ascii'),
                         onset=lambda v: v.encode('ascii'))
    terminator = Magic(b'\x00')


class EmptyParam(Structure):
    pass

TYPES = {
    "PLAYLIST": 0x01,
    "ARTIST": 0x02,
    "ALBUM": 0x03,
    "GENRE": 0x04,
    "SONG": 0x05,
    "COMPOSER": 0x06,
}


TYPES_INV = {v: k for k, v in TYPES.items()}


class ItemParam(Structure):
    _type = UBInt8()
    type = FieldProperty(_type,
                         onget=lambda v: TYPES_INV[v],
                         onset=lambda v: TYPES[v.upper()])
    number = UBInt32()


class ItemRangeParam(Structure):
    _type = UBInt8()
    type = FieldProperty(_type,
                         onget=lambda v: TYPES_INV[v],
                         onset=lambda v: TYPES[v.upper()])
    start = UBInt32()
    length = UBInt32()


class ItemNameResult(Structure):
    offset = UBInt32()
    name = StringField()


class TimeStatusResult(Structure):
    STATUS_STOP = 0x00
    STATUS_PLAYING = 0x01
    STATUS_PAUSED = 0x02

    length = UBInt32()
    elapsed = UBInt32()

    # STOP / PLAYING / PAUSED
    status = UBInt8()


class PictureControlHeadBlock(Structure):
    block = UBInt16()
    color = Magic(b'\x01')
    width = UBInt16()
    height = UBInt16()
    bytes_per_line = UBInt32()
    bytes = Payload()


class PictureControlBlock(Structure):
    block = UBInt16()
    bytes = Payload()


class ScreenSizeResult(Structure):
    width = UBInt16()
    _ = Magic(b'\x00')
    height = UBInt16()


class ColorScreenSizeResult(Structure):
    # Actual structure is unclear
    # Twice as large as ScreenSieResult
    data = UBInt8Sequence(10)


class CommandResultParam(Structure):
    result = UBInt8()
    command = UBInt16()


class AirMode:
    class Types:
        PLAYLIST = 0x01
        ARTIST = 0x02
        ALBUM = 0x03
        GENRE = 0x04
        SONG = 0x05
        COMPOSER = 0x06

    class Commands:
        NCU_01 = 0x0000
        FEEDBACK = 0x0001
        # A simple ping-request?
        NCU_02 = 0x0002
        # A simple ping-response?
        NCU_03 = 0x0003
        # Requests flag set by NCU_0B
        NCU_09 = 0x0009
        # Response to NCU_0B
        NCU_0A = 0x000A
        # Sets flag returned by NCU_09
        NCU_0B = 0x000B
        NCU_0C = 0x000C
        NCU_0D = 0x000D

        GET_IPOD_TYPE = 0x0012
        RES_IPOD_TYPE = 0x0013

        GET_IPOD_NAME = 0x0014
        RES_IPOD_NAME = 0x0015

        SWITCH_MAIN_PLAYLIST = 0x0016
        SWITCH_ITEM = 0x0017

        GET_TYPE_COUNT = 0x0018
        RES_TYPE_COUNT = 0x0019

        GET_ITEM_NAMES = 0x001A
        RES_ITEM_NAME = 0x001B

        GET_TIME_STATUS = 0x001C
        RES_TIME_STATUS = 0x001D

        GET_PLAYLIST_POS = 0x001E
        RES_PLAYLIST_POS = 0x001F

        GET_SONG_TITLE = 0x0020
        RES_SONG_TITLE = 0x0021

        GET_SONG_ARTIST = 0x0022
        RES_SONG_ARTIST = 0x0023

        GET_SONG_ALBUM = 0x0024
        RES_SONG_ALBUM = 0x0025

        SET_POLLING_MODE = 0x0026
        RES_TIME_ELAPSED = 0x0027

        EXEC_PLAYLIST_JUMP = 0x0028

        PLAYBACK_CONTROL = 0x0029

        GET_SHUFFLE_MODE = 0x002C
        RES_SHUFFLE_MODE = 0x002D
        SET_SHUFFLE_MODE = 0x002E

        GET_REPEAT_MODE = 0x002F
        RES_REPEAT_MODE = 0x0030
        SET_REPEAT_MODE = 0x0031

        UPLOAD_PICTURE = 0x0032
        GET_SCREEN_SIZE = 0x0033
        RES_SCREEN_SIZE = 0x0034

        GET_PLAYLIST_SIZE = 0x0035
        RES_PLAYLIST_SIZE = 0x0036

        PLAYLIST_JUMP = 0x0037

        NCU_38 = 0x0038
        # Possibly color version of screen size?
        NCU_39 = 0x0039


class AirCommand(Structure):
    id = DispatchField(UBInt16())
    parameters = DispatchTarget(None, dispatch_field=id, dispatch_mapping={
        AirMode.Commands.NCU_01: CommandResultParam,
        AirMode.Commands.FEEDBACK: CommandResultParam,
        AirMode.Commands.NCU_02: EmptyParam,
        AirMode.Commands.NCU_03: UBInt8Sequence(8),
        AirMode.Commands.NCU_09: EmptyParam,
        AirMode.Commands.NCU_0A: UBInt8,
        AirMode.Commands.NCU_0B: UBInt8,
        AirMode.Commands.NCU_0C: UBInt8Sequence(7),
        AirMode.Commands.NCU_0D: UBInt8Sequence(11),
        AirMode.Commands.GET_IPOD_TYPE: EmptyParam,
        AirMode.Commands.RES_IPOD_TYPE: UBInt16,
        AirMode.Commands.GET_IPOD_NAME: EmptyParam,
        AirMode.Commands.RES_IPOD_NAME: StringField,
        AirMode.Commands.SWITCH_MAIN_PLAYLIST: EmptyParam,
        AirMode.Commands.SWITCH_ITEM: ItemParam,
        AirMode.Commands.GET_TYPE_COUNT: UBInt8,
        AirMode.Commands.RES_TYPE_COUNT: UBInt32,
        AirMode.Commands.GET_ITEM_NAMES: ItemRangeParam,
        AirMode.Commands.RES_ITEM_NAME: ItemNameResult,
        AirMode.Commands.GET_TIME_STATUS: EmptyParam,
        AirMode.Commands.RES_TIME_STATUS: TimeStatusResult,
        AirMode.Commands.GET_PLAYLIST_POS: EmptyParam,
        AirMode.Commands.RES_PLAYLIST_POS: UBInt32,
        AirMode.Commands.GET_SONG_TITLE: UBInt32,
        AirMode.Commands.RES_SONG_TITLE: StringField,
        AirMode.Commands.GET_SONG_ARTIST: UBInt32,
        AirMode.Commands.RES_SONG_ARTIST: StringField,
        AirMode.Commands.GET_SONG_ALBUM: UBInt32,
        AirMode.Commands.RES_SONG_ALBUM: StringField,
        AirMode.Commands.SET_POLLING_MODE: UBInt8,
        AirMode.Commands.RES_TIME_ELAPSED: UBInt32,
        AirMode.Commands.EXEC_PLAYLIST_JUMP: UBInt32,
        AirMode.Commands.PLAYBACK_CONTROL: UBInt8,
        AirMode.Commands.GET_SHUFFLE_MODE: EmptyParam,
        AirMode.Commands.RES_SHUFFLE_MODE: UBInt8,
        AirMode.Commands.SET_SHUFFLE_MODE: UBInt8,
        AirMode.Commands.GET_REPEAT_MODE: EmptyParam,
        AirMode.Commands.RES_REPEAT_MODE: UBInt8,
        AirMode.Commands.SET_REPEAT_MODE: UBInt8,
        AirMode.Commands.UPLOAD_PICTURE: PictureControlBlock,
        AirMode.Commands.GET_SCREEN_SIZE: EmptyParam,
        AirMode.Commands.RES_SCREEN_SIZE: ScreenSizeResult,
        AirMode.Commands.GET_PLAYLIST_SIZE: EmptyParam,
        AirMode.Commands.RES_PLAYLIST_SIZE: UBInt32,
        AirMode.Commands.PLAYLIST_JUMP: UBInt32,
        AirMode.Commands.NCU_39: ColorScreenSizeResult,
    })


class SwitchMode:
    class Commands:
        SET_VOICE_RECORDER = 0x0101
        SET_IPOD_REMOTE = 0X0102
        SET_ADVANCED_REMOTE = 0x0104

        GET_MODE = 0x0003
        RES_MODE_VOICE_RECORDER = 0x0401
        RES_MODE_IPOD_REMOTE = 0x0402
        RES_MODE_ADVANCED_REMOTE = 0x0404

        SET_ADVANCED_REMOTE_ALT = 0x0005
        SET_IPOD_REMOTE_ALT = 0x0006


class SwitchModeCommand(Structure):
    id = UBInt16()


class VoiceRecorderMode:
    class Commands:
        RECORDING_STARTED = 0x0100
        RECORDING_STOPPED = 0x0101


class VoiceRecorderCommand:
    id = UBInt16()


class SimpleRemoteMode:
    class Commands:
        BUTTON_RELEASED = b'\x00\x00'
        PLAY_PAUSE = b'\x00\x01'
        VOLUME_UP = b'\x00\x02'
        VOLUME_DOWN = b'\x00\x04'
        NEXT_SONG = b'\x00\x08'
        PREV_SONG = b'\x00\x10'
        NEXT_ALBUM = b'\x00\x20'
        PREV_ALBUM = b'\x00\x40'
        STOP = b'\x00\x80'

    class Params:
        PLAY = b'\x00\x00\x01'
        PAUSE = b'\x00\x00\x02'
        MUTE = b'\x00\x00\x04'
        NEXT_PLAYLIST = b'\x00\x00\x20'
        PREV_PLAYLIST = b'\x00\x00\x40'
        SHUFFLE = b'\x00\x00\x80'

        REPEAT = b'\x00\x00\x00\x01'
        IPOD_OFF = b'\x00\x00\x00\x04'
        IPOD_ON = b'\x00\x00\x00\x08'
        MENU_BUTTON = b'\x00\x00\x00\x40'
        OK_SELECT_BUTTON = b'\x00\x00\x00\x80'


class SimpleRemoteCommand:
    id = Payload()


class RequestModeStatusCommand:
    id = Magic(b'\x00\x03')


class IpodPacket(Structure):
    header = Magic(b'\xFF\x55')
    length = LengthField(UBInt8(), get_length=lambda l: l.getval() - 1, set_length=lambda f, v: f.setval(v + 1))
    mode = DispatchField(UBInt8())
    command = DispatchTarget(length_provider=length, dispatch_field=mode, dispatch_mapping={
        0x00: SwitchModeCommand,
        0x01: VoiceRecorderCommand,
        0X02: SimpleRemoteCommand,
        0x03: RequestModeStatusCommand,
        0x04: AirCommand,
    })
    checksum = CRCField(UBInt8(), algo=ipod_checksum, start=2, end=-1)


if __name__ == "__main__":
    # Switch to AiR mode command
    switch_air_bytes = b'\xFF\x55\x03\x00\x01\x04\xF8'
    switch_air_packet = IpodPacket.from_data(switch_air_bytes)

    assert(switch_air_packet.command.id == SwitchMode.Commands.SET_ADVANCED_REMOTE)
    assert(switch_air_packet.pack() == switch_air_bytes)

    song_name_data = b'\xFF\x55\x0A\x04\x00\x21A SONG\x00'
    song_name_data += bytes([(0x100 - (sum(song_name_data[2:]))) & 0xFF])
    song_name_packet = IpodPacket.from_data(song_name_data)

    assert(song_name_packet.command.parameters.text == "A SONG")

    packet4 = IpodPacket()
    packet4.command = AirCommand()
    packet4.command.id = AirMode.Commands.RES_SONG_ARTIST
    packet4.command.parameters = StringField()
    packet4.command.parameters.text = "An Artist"
    assert(packet4.pack() == b'\xffU\r\x04\x00%An Artist\x00\x84')
