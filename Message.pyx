cimport CMessage

cdef class Message:
    def __init__(self, code, raw_message=None):
        # Reserve space for the 