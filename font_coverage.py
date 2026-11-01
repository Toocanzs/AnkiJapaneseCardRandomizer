"""Find the characters a font claims to support but can't actually draw.

Some fonts list characters (often rarer kanji, or 〜) in their character map
that point to *empty* glyphs. Anki's card view trusts the font, so those
characters show up blank on the card instead of falling back to another font.
unicodeRangeFor() returns a CSS unicode-range that leaves them out, so Anki
falls back for them.

This is a tiny reader for the few TrueType tables needed (cmap, head, maxp,
loca, glyf), since fontTools isn't available inside Anki. Fonts with CFF
outlines (most .otf) aren't inspected and get no range.
"""
import struct
import unicodedata

MAX_CODEPOINT = 0x10FFFF


class FontFormatError(Exception):
    pass


def _tables(data, fontOffset):
    numTables = struct.unpack_from(">H", data, fontOffset + 4)[0]
    tables = {}
    for i in range(numTables):
        tag, _checksum, offset, length = struct.unpack_from(">4sIII", data, fontOffset + 12 + 16 * i)
        tables[tag.decode("latin-1")] = (offset, length)
    return tables


def _firstFontOffset(data):
    # A collection (.ttc) starts with a 'ttcf' header; browsers use its first font
    if data[:4] == b"ttcf":
        return struct.unpack_from(">I", data, 12)[0]
    return 0


def _parseCmapFormat4(data, offset):
    segCount = struct.unpack_from(">H", data, offset + 6)[0] // 2
    endCodes = offset + 14
    startCodes = endCodes + 2 * segCount + 2
    idDeltas = startCodes + 2 * segCount
    idRangeOffsets = idDeltas + 2 * segCount
    mapping = {}
    for i in range(segCount):
        end = struct.unpack_from(">H", data, endCodes + 2 * i)[0]
        start = struct.unpack_from(">H", data, startCodes + 2 * i)[0]
        delta = struct.unpack_from(">h", data, idDeltas + 2 * i)[0]
        rangeOffsetPos = idRangeOffsets + 2 * i
        rangeOffset = struct.unpack_from(">H", data, rangeOffsetPos)[0]
        if start == 0xFFFF:
            continue
        for cp in range(start, end + 1):
            if rangeOffset == 0:
                glyph = (cp + delta) & 0xFFFF
            else:
                glyphPos = rangeOffsetPos + rangeOffset + 2 * (cp - start)
                glyph = struct.unpack_from(">H", data, glyphPos)[0]
                if glyph != 0:
                    glyph = (glyph + delta) & 0xFFFF
            if glyph != 0:
                mapping[cp] = glyph
    return mapping


def _parseCmapFormat12(data, offset):
    numGroups = struct.unpack_from(">I", data, offset + 12)[0]
    mapping = {}
    for i in range(numGroups):
        start, end, startGlyph = struct.unpack_from(">III", data, offset + 16 + 12 * i)
        for cp in range(start, min(end, MAX_CODEPOINT) + 1):
            glyph = startGlyph + cp - start
            if glyph != 0:
                mapping[cp] = glyph
    return mapping


# Preferred Unicode subtables, best first: (platformID, encodingID)
_CMAP_PREFERENCE = [(3, 10), (0, 6), (0, 4), (3, 1), (0, 3), (0, 2), (0, 1), (0, 0)]


def _parseCmap(data, cmapOffset):
    numSubtables = struct.unpack_from(">H", data, cmapOffset + 2)[0]
    subtables = {}
    for i in range(numSubtables):
        platform, encoding, offset = struct.unpack_from(">HHI", data, cmapOffset + 4 + 8 * i)
        subtables.setdefault((platform, encoding), cmapOffset + offset)
    for key in _CMAP_PREFERENCE:
        if key not in subtables:
            continue
        offset = subtables[key]
        fmt = struct.unpack_from(">H", data, offset)[0]
        if fmt == 4:
            return _parseCmapFormat4(data, offset)
        if fmt == 12:
            return _parseCmapFormat12(data, offset)
    raise FontFormatError("no supported Unicode cmap subtable")


def _glyphIsEmpty(data, glyfOffset, loca, glyph):
    if glyph + 1 >= len(loca):
        return False
    start, end = loca[glyph], loca[glyph + 1]
    if end <= start:
        return True
    numberOfContours = struct.unpack_from(">h", data, glyfOffset + start)[0]
    return numberOfContours == 0


def _isLegitimatelyBlank(cp):
    # Whitespace and invisible format/control characters have no outline on purpose
    ch = chr(cp)
    return ch.isspace() or unicodedata.category(ch) in ("Zs", "Cf", "Cc")


def blankCodepoints(data):
    """Return (cmap, sorted blank codepoints), or None if the font has no TrueType outlines."""
    fontOffset = _firstFontOffset(data)
    tables = _tables(data, fontOffset)
    if "glyf" not in tables or "loca" not in tables:
        return None  # CFF outlines (.otf); not inspected
    headOffset = tables["head"][0]
    longLoca = struct.unpack_from(">h", data, headOffset + 50)[0] == 1
    numGlyphs = struct.unpack_from(">H", data, tables["maxp"][0] + 4)[0]
    locaOffset = tables["loca"][0]
    if longLoca:
        loca = struct.unpack_from(">%dI" % (numGlyphs + 1), data, locaOffset)
    else:
        loca = [x * 2 for x in struct.unpack_from(">%dH" % (numGlyphs + 1), data, locaOffset)]
    glyfOffset = tables["glyf"][0]
    cmap = _parseCmap(data, tables["cmap"][0])
    blank = sorted(
        cp for cp, glyph in cmap.items()
        if not _isLegitimatelyBlank(cp) and _glyphIsEmpty(data, glyfOffset, loca, glyph)
    )
    return cmap, blank


def _formatRanges(ranges):
    return ",".join("U+%X" % a if a == b else "U+%X-%X" % (a, b) for a, b in ranges)


def _includedRanges(codepoints):
    ranges = []
    for cp in codepoints:
        if ranges and cp == ranges[-1][1] + 1:
            ranges[-1][1] = cp
        else:
            ranges.append([cp, cp])
    return ranges


def _excludedRanges(excluded):
    ranges = []
    start = 0
    for cp in excluded:
        if cp > start:
            ranges.append((start, cp - 1))
        start = cp + 1
    if start <= MAX_CODEPOINT:
        ranges.append((start, MAX_CODEPOINT))
    return ranges


def unicodeRangeFor(path):
    """CSS unicode-range leaving out the font's blank glyphs, or None if none are found.

    Either lists exactly what the font draws, or covers everything except the
    blank glyphs (characters missing from the font fall back anyway), whichever
    is shorter. Mostly complete fonts favour the second form, partial fonts the first.
    """
    with open(path, "rb") as f:
        data = f.read()
    result = blankCodepoints(data)
    if result is None:
        return None
    cmap, blank = result
    if not blank:
        return None
    blankSet = set(blank)
    drawable = sorted(cp for cp in cmap if cp not in blankSet)
    return min(
        _formatRanges(_includedRanges(drawable)),
        _formatRanges(_excludedRanges(blank)),
        key=len,
    )
