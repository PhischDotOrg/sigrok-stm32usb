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

        # self.out_python = self.register(srd.OUTPUT_PYTHON)
        # self.out_binary = self.register(srd.OUTPUT_BINARY)
        # self.out_bitrate = self.register(srd.OUTPUT_META,
        #         meta=(int, 'Bitrate', 'Bitrate from Start bit to Stop bit'))

    def reset(self):
        self._initialize()

    def decode(self):
        while True:
            if self._cur == -1:
                pins = self.wait()
            else:
                pins = self.wait( [
                    { 0 : 'e' },
                    { 1 : 'e' },
                    { 2 : 'e' }
                ] )

                self._begin = self._end
                self._end = self.samplenum

            self._old = self._cur
            self._cur = 1 * pins[0] + 2 * pins[1] + 4 * pins[2]

            self._putDecodedData()

    def flush(self):
        # flush() is called when a block of data ends, including the very last block
        # of the stream.
        # If there is no change in data (_old == _cur), then don't update the begin
        # marker of the block that we're going to display.
        if (self._old != self._cur):
            self._begin = self._end
        self._end = self.endsample
        self._old = self._cur

        self._putDecodedData()

    def metadata(self, key, value):
        if key == srd.SRD_CONF_SAMPLERATE:
            self.samplerate = value

    def _initialize(self):
        self._begin = 0
        self._end = 0
        self._cur = -1
        self._old = -1

    def _putDecodedData(self):
        # self._old contains the index that is to be displayed.
        # In the first sample, the idx will be -1 so don't display.
        if (self._old != -1):
            self.put(
                self._begin,
                self._end,
                self.out_ann,
                Decoder._values[self._old]
            )
