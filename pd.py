import sigrokdecode as srd

from enum import IntEnum, unique

e_Undefined, e_Idle, e_SetupReceived, e_DataIn, e_StatusOut, e_DataOut, e_StatusIn, e_Error = range(8)

class Decoder(srd.Decoder):
    api_version = 3
    id = 'stm32f1-usb'
    name = 'STM32F1 USB'
    longname = 'STM32F1 USB Device State Machine'
    desc = 'Decoder for the STM32F21 USB Stack''s State Machine'
    license = 'gplv2+'
    inputs = ['logic']
    outputs = ['stm32f1']
    tags = ['PhS']
    channels = (
        {'id': 'fsm_0', 'name': 'FSM#0', 'desc': 'Bit #0 of UsbControlPipe::State_e'},
        {'id': 'fsm_1', 'name': 'FSM#1', 'desc': 'Bit #1 of UsbControlPipe::State_e'},
        {'id': 'fsm_2', 'name': 'FSM#2', 'desc': 'Bit #2 of UsbControlPipe::State_e'},
    )
    # options = (
    #     {
    #         'id' : 'phs_id',
    #         'desc' : 'phs_desc',
    #         'default' : 'phs_default',
    #         'values' : ('phs_default', 'phs_alternate')
    #     },
    # )
    annotations = (
        ( 'e_Undefined',        'e_Undefined = 0' ),
        ( 'e_Idle',             'e_Idle = 1'),
        ( 'e_SetupReceived',    'e_SetupReceived = 2'),
        ( 'e_DataIn',           'e_DataIn = 3'),
        ( 'e_StatusOut',        'e_StatusOut = 4'),
        ( 'e_DataOut',          'e_DataOut = 5'),
        ( 'e_StatusIn',         'e_StatusIn = 6'),
        ( 'e_Error',            'e_Error = 7'),
    )
    annotation_rows = (
        ('states', 'FSM State', ( e_Undefined, e_Idle, e_SetupReceived, e_DataIn, e_StatusOut, e_DataOut, e_StatusIn, e_Error )),
    )

    @unique
    class FsmStates(IntEnum):
        e_Undefined     = 0,
        e_Idle          = 1,
        e_SetupReceived = 2,
        e_DataIn        = 3,
        e_StatusOut     = 4,
        e_DataOut       = 5,
        e_StatusIn      = 6,
        e_Error         = 7

    _values = {
        FsmStates.e_Undefined       : [ FsmStates.e_Undefined ,     [ 'e_Undefined = 0', 'e_Undefined', 'UND', '0' ] ],
        FsmStates.e_Idle            : [ FsmStates.e_Idle,           [ 'e_Idle = 1', 'e_Idle', 'IDL', '1' ] ],
        FsmStates.e_SetupReceived   : [ FsmStates.e_SetupReceived,  [ 'e_SetupReceived = 2', 'e_SetupReceived', 'SRX', '2' ] ],
        FsmStates.e_StatusOut       : [ FsmStates.e_StatusOut,      [ 'e_StatusOut = 4', 'e_StatusOut', 'STO', '3' ] ],
        FsmStates.e_DataIn          : [ FsmStates.e_DataIn,         [ 'e_DataIn = 3', 'e_DataIn', 'DIN', '4' ] ],
        FsmStates.e_DataOut         : [ FsmStates.e_DataOut,        [ 'e_DataOut = 5', 'e_DataOut', 'DOT', '5' ] ],
        FsmStates.e_StatusIn        : [ FsmStates.e_StatusIn,       [ 'e_StatusIn = 6', 'e_StatusIn', 'STI', '6' ] ],
        FsmStates.e_Error           : [ FsmStates.e_Error,          [ 'e_Error = 7', 'e_Error', 'ERR', '7' ] ]
    }

    def __init__(self, **kwargs):
        self._initialize()

    def start(self):
        self.out_ann = self.register(srd.OUTPUT_ANN)
        print("PhS: start()")

        # self.out_python = self.register(srd.OUTPUT_PYTHON)
        # self.out_binary = self.register(srd.OUTPUT_BINARY)
        # self.out_bitrate = self.register(srd.OUTPUT_META,
        #         meta=(int, 'Bitrate', 'Bitrate from Start bit to Stop bit'))

    def reset(self):
        print("PhS: reset()")
        self._initialize()

    def decode(self):
        print("PhS: decode()")

        while True:
            if self._firstChunk == True:
                pins = self.wait()
                self._firstChunk = False
            else:
                pins = self.wait( [
                    { 0 : 'e' },
                    { 1 : 'e' },
                    { 2 : 'e' }
                ] )

            self._startsample = self._endsample
            self._endsample = self.samplenum

            idx = 1 * pins[0] + 2 * pins[1] + 4 * pins[2]

            print("decode(): _startsample: ", self._startsample, " _endsample: ", self._endsample, " _idx: ", self._idx, " idx: ", idx)
            print("decode(): startsample: ", self.startsample, " endsample: ", self.endsample, " _idx: ", self._idx)

            self._putDecodedData()

            self._idx = idx

    def flush(self):
        print("PhS: flush()")

        self._startsample = self._endsample
        self._endsample = self.endsample

        print("flush(): _startsample: ", self._startsample, " _endsample: ", self._endsample, " _idx: ", self._idx)
        print("flush(): startsample: ", self.startsample, " endsample: ", self.endsample, " _idx: ", self._idx)

        self._putDecodedData()

        self._firstChunk = True

    def metadata(self, key, value):
        print("PhS: metadata()")

        if key == srd.SRD_CONF_SAMPLERATE:
            self.samplerate = value

    def _initialize(self):
        self._firstChunk = True

        self._startsample = 0
        self._endsample = 0
        self._idx = -1

    def _putDecodedData(self):
        if (self._idx == -1):
            return

        self.put(
            self._startsample,
            self._endsample,
            self.out_ann,
            Decoder._values[self._idx]
        )
