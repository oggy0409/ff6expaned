"""Core patches shared by production targets."""
from ff6x import FRAMEWORK_VERSION

META_MAGIC = b"FF6X-EE\x00"


def p001_build_metadata(rom, target, build_version):
    """Build identification block at F0:0000 (BUILD_METADATA). No game code reads it."""
    major, minor, patch = (int(x) for x in build_version.split("."))
    fw = [int(x) for x in FRAMEWORK_VERSION.split(".")]
    blob = bytearray(META_MAGIC)
    blob += bytes([1, major, minor, patch, fw[0], fw[1], fw[2], 0])     # fmt ver, build ver, fw ver
    blob += target.encode("ascii").ljust(16, b"\x00")[:16]
    blob += b"BASE:FF3US-REV1 C0FA0464".ljust(32, b"\x00")
    return rom.place("BUILD_METADATA", bytes(blob), "build_metadata", "P001_BUILD_METADATA",
                     reason="Machine-readable build identity for QA tooling.",
                     consumer="tools/verify (offline). No runtime consumer.",
                     at=0xF00000)
