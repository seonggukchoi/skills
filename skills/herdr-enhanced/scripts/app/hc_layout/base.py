"""Shared constants, the error type, and shell helpers."""

import json
import subprocess

PLACEHOLDER = ["sh", "-c", "while :; do sleep 3600; done"]
WAIT_SECONDS = 20
DOC = "herdr-app"
NODE_TYPES = {"row", "column", "block"}


class Fail(Exception):
    pass


def sh(args, check=True):
    p = subprocess.run(args, capture_output=True, text=True)
    if check and p.returncode != 0:
        raise Fail(f"{' '.join(args[:3])} failed: {(p.stderr or p.stdout).strip()}")
    return p


def sh_json(args):
    out = sh(args).stdout.strip()
    try:
        return json.loads(out) if out else None
    except json.JSONDecodeError:
        raise Fail(f"{' '.join(args[:3])}: not JSON: {out[:200]}")
