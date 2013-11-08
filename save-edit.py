#!/usr/bin/env python

import struct


def sublist_index(haystack, needle, start=0):
    n = len(needle)
    if n == 0:
        return start
    for i in xrange(start, len(haystack) - n):
        ok = True
        for j in xrange(0, n):
            if haystack[i + j] != needle[j]:
                ok = False
                break
        if ok:
            return i
    return len(haystack)


class SaveFile:

    def __init__(self, fname):
        print "opening", fname
        with open(fname, "rb") as fd:
            data = fd.read()
            self.header = data[:0x8c]
            data = list(struct.unpack("%dB" % len(data), data)[0x8c:])
            self.data = self.encrypt(data)

    def encrypt(self, data):
        data = list(data)
        seed = 82
        for i in xrange(0, len(data)):
            data[i] = data[i] ^ seed
            seed = (seed + 84) & 0xff
        return data

    def search(self, value):
        value = struct.unpack("4B", struct.pack("<I", value))
        i = -1
        while i < len(self.data):
            i = sublist_index(self.data, value, i + 1)
            if i < len(self.data):
                print "FOUND AT ", i, " 0x", hex(i)

    def setName(self, name):
        if len(name) >= 0x18:
            raise Exception("name is too long")
        name = name + "\0" * (0x18 - len(name))
        self.header = name + self.header[0x18:]

    def setMoney(self, value):
        i = sublist_index(self.data, [ord(c) for c in "Money"])
        if i >= len(self.data):
            raise Exception("could not find money block")
        i -= 148
        if sublist_index(self.data, [0x40, 0x42, 0x0f, 0x00], i) != i:
            raise Exception("money block appears to be longer than 148 bytes")
        i += 4
        print "found at ", i, "current value: ", struct.unpack("<I", struct.pack("4B", *self.data[i: i + 4]))[0]
        self.data[i + 0] = (value >> 0) & 0xff
        self.data[i + 1] = (value >> 8) & 0xff
        self.data[i + 2] = (value >> 16) & 0xff
        self.data[i + 3] = (value >> 24) & 0xff

    def save(self, name):
        with open(name, "wb") as f:
            f.write(self.header)
            data = self.encrypt(self.data)
            f.write(struct.pack("<%dB" % len(data), *data))

print """
#Sample usage:
s1 = SaveFile("00000000.SAV")
s1.setMoney(1200)
s1.setName("money lol")
s1.save("00000002.SAV");
"""
