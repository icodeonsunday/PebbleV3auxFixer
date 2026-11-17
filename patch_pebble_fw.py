#!/usr/bin/env python3
"""Patch Creative Pebble V3 firmware (Pebble.fw v3.8.0.0) so AUX mode can be
manually selected even when the 3.5mm jack insertion sensor is broken.
"""

import argparse
import hashlib
from pathlib import Path

EXPECTED_ORIG_SHA256 = (
    "5daebc2f3513b9648face82fd7853d991eebe52d765627aa91cff2a86391520d"
)
EXPECTED_PATCHED_SHA256 = (
    "9afd3c261fe8b392b150619c948ac8ec79f8c69d7daff21fe4c497cffad6106b"
)

# All files inside Pebble.fw's FAT32 partition are XOR-obfuscated with 0x38.
XOR_KEY = 0x38

# (file_offset, expected_plain_hex, new_plain_hex, description)
PATCHES = [
    (
        0xCDACCC,
        "1a60",
        "0065",
        "common.drv 0x0cbc (com_check_ap_valid): bteqz 0xcf2 -> nop; allow APP_FUNC_LINEIN",
    ),
    (
        0xCDE5E8,
        "02b220e841a2",
        "20e8016a0065",
        "common.drv 0x45d8 (get_linein_status): always return 1 (plugged in)",
    ),
    (
        0xCEC36E,
        "0461",
        "0410",
        "linein.ap 0x035e (linein_sys_msg_deal): btnez 0x368 -> b 0x368; ignore MSG_LINEIN_OUT (0x2103)",
    ),
    (
        0xCEC406,
        "0272026101680210025a176011b7c0a7082e10b3",
        "10f01c721a6010f00172176010f0027214600710",
        "linein.ap 0x03f6..0x0409 (_scene_linein_play): only exit on 0x801c (mode), 0x8001 (power), 0x8002 (low batt)",
    ),
    (
        0xCEC420,
        "0360",
        "0310",
        "linein.ap 0x0410 (_scene_linein_play): bteqz 0x418 -> b 0x418",
    ),
    (
        0xCEC852,
        "0328",
        "0310",
        "linein.ap 0x0842 (_scene_linein_init): bnez $s0, 0x84a -> b 0x84a; never exit with 0x801c",
    ),
]


def xor_bytes(data: bytes) -> bytes:
    return bytes(b ^ XOR_KEY for b in data)


def patch_firmware(src: Path, dst: Path) -> None:
    raw = bytearray(src.read_bytes())
    orig_sha = hashlib.sha256(raw).hexdigest()
    if orig_sha != EXPECTED_ORIG_SHA256:
        raise ValueError(
            f"Input hash mismatch for {src}:\n"
            f"  expected: {EXPECTED_ORIG_SHA256}\n"
            f"  actual:   {orig_sha}"
        )

    for offset, old_plain_hex, new_plain_hex, desc in PATCHES:
        old_raw = xor_bytes(bytes.fromhex(old_plain_hex))
        new_raw = xor_bytes(bytes.fromhex(new_plain_hex))
        if len(old_raw) != len(new_raw):
            raise ValueError(f"Length mismatch at 0x{offset:06x}")

        actual_raw = bytes(raw[offset : offset + len(old_raw)])
        if actual_raw != old_raw:
            raise ValueError(
                f"Unexpected bytes at 0x{offset:06x} ({desc}):\n"
                f"  expected: {old_raw.hex()}\n"
                f"  actual:   {actual_raw.hex()}"
            )

        raw[offset : offset + len(new_raw)] = new_raw
        print(f"Patched 0x{offset:06x}: {desc}")

    patched_sha = hashlib.sha256(raw).hexdigest()
    if patched_sha != EXPECTED_PATCHED_SHA256:
        raise ValueError(
            f"Patched hash mismatch:\n"
            f"  expected: {EXPECTED_PATCHED_SHA256}\n"
            f"  actual:   {patched_sha}"
        )

    dst.write_bytes(raw)
    print(f"\nWrote {dst} (SHA-256: {patched_sha})")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default= "Pebble.fw",
        help="Path to stock Pebble.fw (default: tmp/Tool/Pebble.fw)",
    )
    parser.add_argument(
        "output",
        nargs="?",
        type=Path,
        default= "Pebble_patched.fw",
        help="Output path (default: tmp/Tool/Pebble_patched.fw)",
    )
    args = parser.parse_args()
    patch_firmware(args.input, args.output)


if __name__ == "__main__":
    main()
