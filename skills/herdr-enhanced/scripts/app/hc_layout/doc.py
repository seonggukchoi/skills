"""The machine's layout document, read and written over `hc connect`.

Reading is safe anywhere. Writing (`doc_change`) is the doc route only: it checks the
document's shape first and carries the version it read, retrying when another client
wrote first.
"""

import json
import subprocess
import time

from .base import DOC, NODE_TYPES, Fail
from .tree import walk


def rpc(method, params):
    req = (json.dumps({"jsonrpc": "2.0", "id": 1, "method": "hello", "params": {}}) + "\n"
           + json.dumps({"jsonrpc": "2.0", "id": 2, "method": method, "params": params}) + "\n")
    p = subprocess.Popen(["hc", "connect"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True)
    try:
        p.stdin.write(req)
        p.stdin.flush()
        for line in p.stdout:
            msg = json.loads(line)
            if msg.get("id") == 2:
                return msg
        raise Fail(f"{method}: no answer from hc connect")
    finally:
        p.kill()


def doc_read(machine=None):
    params = {"name": DOC}
    if machine:
        params["on"] = machine
    msg = rpc("doc.get", params)
    if "error" in msg:
        raise Fail(f"doc.get{' on ' + machine if machine else ''}: {msg['error'].get('message')}")
    value = msg["result"].get("value")
    check_shape(value)
    return value, msg["result"]["version"]


def doc_get(machine=None):
    return doc_read(machine)[0]


def check_shape(value):
    """Refuse to touch a document that is not shaped the way this script was measured on."""
    def bad(why):
        raise Fail("the layout document has a shape this script does not know (" + why + "); "
                   "this Herdr version may store layouts differently, so nothing was changed")
    if not isinstance(value, dict) or not isinstance(value.get("spaces"), list):
        bad("no spaces list")
    for sp in value["spaces"]:
        if not isinstance(sp, dict) or not isinstance(sp.get("id"), str) \
                or not isinstance(sp.get("tabs"), list):
            bad("a space without id or tabs")
        for tb in sp["tabs"]:
            if not isinstance(tb, dict) or not isinstance(tb.get("id"), str) \
                    or not isinstance(tb.get("root"), dict):
                bad("a tab without id or root")
            for node, *_ in walk(tb["root"]):
                if node.get("type") not in NODE_TYPES or not isinstance(node.get("id"), str):
                    bad(f"a node of type {node.get('type')!r}")
                if node["type"] == "block" and not isinstance(node.get("content"), dict):
                    bad("a block without content")
                if node["type"] != "block" and not isinstance(node.get("children"), list):
                    bad("a split without children")
                size = node.get("size")
                if size is not None and not (isinstance(size, dict) and set(size) <= {"weight", "px"}):
                    bad("an unknown size")


def doc_change(machine, mutate):
    """Read, change, write with the version read; retry when another client wrote first."""
    for _ in range(6):
        value, version = doc_read(machine)
        result = mutate(value)
        check_shape(value)
        params = {"name": DOC, "value": value, "version": version}
        if machine:
            params["on"] = machine
        msg = rpc("doc.set", params)
        if "error" not in msg:
            return result
        if (msg["error"].get("data") or {}).get("kind") != "conflict":
            raise Fail(f"doc.set: {msg['error'].get('message')}")
        time.sleep(0.2)
    raise Fail("doc.set: the layout kept changing under us; nothing was changed")
