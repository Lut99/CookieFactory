"""
    CFNPv2_CODES.py
        by tHE iNCREDIBLE mACHINE

    This file is a library for the subprotocols and their respective operators.
"""


class SUBPROTOCOL:
    def __init__(self):
        # Collect all typles and put them in pairs
        opcodes = []
        for op in self.opcodes:
            setattr(self, op, (self.code, self.opcodes[op]))
            opcodes.append(self.opcodes[op])
        self.opcodes = opcodes


# SUBPROCOTOL CODES
class __FOURTH_HANDSHAKE__(SUBPROTOCOL):
    code = 0
    opcodes = {
        "REQUEST": 0,
        "ACCEPT": 1
    }


class __TERMINAL__(SUBPROTOCOL):
    code = 1
    opcodes = {
        "ANNOUNCEMENT": 0,
        "ANNOUNCEMENT_MESSAGE": 1,
        "COMMAND_REQUEST": 2,
        "COMMAND_RESPONSE": 3,
        "SYNC_REQUEST": 4,
        "SYNC_RESPONSE": 5
    }


# Instantiate objects of each of 'em
FOURTH_HANDSHAKE = __FOURTH_HANDSHAKE__()
TERMINAL = __TERMINAL__()

TYPES = {
    FOURTH_HANDSHAKE.code: FOURTH_HANDSHAKE,
    TERMINAL.code: TERMINAL
}