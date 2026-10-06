"""Just enough MP4 parsing to validate an upload.

We accept only MP4/H.264 and cap the length, so the two things worth knowing
about a file are whether it really is an MP4 and how long it runs. ffmpeg would
answer both, but it is a heavy dependency to require on every deploy for two
numbers that sit in the container header.

An MP4 is a tree of boxes, each ``[4-byte big-endian size][4-byte type]``
followed by its payload. Duration lives in the ``mvhd`` box inside ``moov``.
"""
import struct

#: Brands that indicate an ISO base-media file we are willing to accept.
ACCEPTED_BRANDS = {
    b'isom', b'iso2', b'iso4', b'iso5', b'iso6', b'mp41', b'mp42',
    b'avc1', b'M4V ', b'dash', b'qt  ',
}

MAX_BOX_DEPTH = 6


class NotAnMp4(Exception):
    pass


def _read_boxes(stream, end, depth=0):
    """Yield ``(type, payload_start, payload_end)`` for boxes under ``end``."""
    if depth > MAX_BOX_DEPTH:
        return
    while stream.tell() + 8 <= end:
        header_start = stream.tell()
        header = stream.read(8)
        if len(header) < 8:
            return
        size, box_type = struct.unpack('>I4s', header)
        if size == 1:
            # 64-bit size, stored in the eight bytes after the type.
            extended = stream.read(8)
            if len(extended) < 8:
                return
            size = struct.unpack('>Q', extended)[0]
            payload_start = header_start + 16
        elif size == 0:
            # Runs to the end of the file.
            size = end - header_start
            payload_start = header_start + 8
        else:
            payload_start = header_start + 8

        if size < 8:
            return
        box_end = min(header_start + size, end)
        yield box_type, payload_start, box_end
        stream.seek(box_end)


def _find_mvhd(stream, end, depth=0):
    for box_type, start, box_end in _read_boxes(stream, end, depth):
        if box_type == b'mvhd':
            return start, box_end
        if box_type in (b'moov', b'trak', b'mdia'):
            stream.seek(start)
            found = _find_mvhd(stream, box_end, depth + 1)
            if found:
                return found
            stream.seek(box_end)
    return None


def inspect(stream):
    """Return ``{'brand': str, 'duration': float|None}`` for an open binary stream.

    Raises ``NotAnMp4`` if the file does not start with a recognised ``ftyp``
    box. Duration comes back ``None`` when the header is present but unreadable,
    which callers should treat as "unknown", not "zero".
    """
    stream.seek(0, 2)
    size = stream.tell()
    stream.seek(0)

    header = stream.read(12)
    if len(header) < 12 or header[4:8] != b'ftyp':
        raise NotAnMp4('missing ftyp box')
    brand = header[8:12]
    if brand not in ACCEPTED_BRANDS:
        raise NotAnMp4(f'unsupported brand {brand!r}')

    stream.seek(0)
    found = _find_mvhd(stream, size)
    if not found:
        return {'brand': brand.decode('latin-1').strip(), 'duration': None}

    start, box_end = found
    stream.seek(start)
    version_flags = stream.read(4)
    if len(version_flags) < 4:
        return {'brand': brand.decode('latin-1').strip(), 'duration': None}
    version = version_flags[0]

    try:
        if version == 1:
            # creation(8) modification(8) timescale(4) duration(8)
            stream.read(16)
            timescale = struct.unpack('>I', stream.read(4))[0]
            raw_duration = struct.unpack('>Q', stream.read(8))[0]
        else:
            # creation(4) modification(4) timescale(4) duration(4)
            stream.read(8)
            timescale = struct.unpack('>I', stream.read(4))[0]
            raw_duration = struct.unpack('>I', stream.read(4))[0]
    except struct.error:
        return {'brand': brand.decode('latin-1').strip(), 'duration': None}

    duration = raw_duration / timescale if timescale else None
    # 0xFFFFFFFF is the conventional "unknown" duration.
    if raw_duration in (0, 0xFFFFFFFF, 0xFFFFFFFFFFFFFFFF):
        duration = None
    return {'brand': brand.decode('latin-1').strip(), 'duration': duration}
