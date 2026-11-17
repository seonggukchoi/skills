"""Steps both routes share."""

import json

from .app import app
from .base import Fail, sh, sh_json
from .doc import doc_change, doc_get
from .ids import qualify, split_id
from .tree import locate, tabs, terminals_under, weight


def relabel(machine, doc, tab_ids):
    """The doc route does not make the app relabel; keep herdr.space/herdr.tab true."""
    for sp, tb in tabs(doc):
        if tb["id"] not in tab_ids:
            continue
        for t in terminals_under(tb["root"]):
            sh(["hc", "label", qualify(machine, t), f"herdr.space={sp['id']}",
                f"herdr.tab={tb['id']}"], check=False)


def ensure_running(machine, terminal_local):
    p = sh(["hc", "get", qualify(machine, terminal_local), "--json"], check=False)
    if p.returncode != 0:
        raise Fail(f"no terminal {qualify(machine, terminal_local)}")
    t = json.loads(p.stdout)
    if t.get("state") != "live":
        raise Fail(f"{qualify(machine, terminal_local)} is {t.get('state')}, not running")
    if not t.get("keep"):
        sh(["hc", "keep", qualify(machine, terminal_local)])


def start_terminal(machine, cwd, argv, labels=()):
    args = ["hc", "run", "--bg", "--json", "--keep", "--no-parent"]
    if machine:
        args += ["--on", machine]
    if cwd:
        args += ["--cwd", cwd]
    for k, v in labels:
        args += ["--label", f"{k}={v}"]
    args += ["--"] + argv if argv else []
    r = sh_json(args)
    _, local = split_id(r["address"])
    return local


def parse_ratio(text):
    try:
        parts = [float(x) for x in text.replace("/", ":").split(":")]
    except ValueError:
        raise Fail(f"bad ratio {text!r}; use numbers like 7:3 or 1:1:2")
    if len(parts) < 2 or any(p <= 0 for p in parts):
        raise Fail("a ratio needs two or more positive numbers")
    return parts


def verify_beside(machine, term_local, anchor_id, direction):
    doc = doc_get(machine)
    me, there = locate(doc, term_local), locate(doc, anchor_id)
    want = "row" if direction in ("right", "left") else "column"
    ok = bool(me and there and me["parent"] is not None and me["parent"] is there["parent"]
              and me["parent"]["type"] == want
              and me["index"] - there["index"] == (1 if direction in ("right", "down") else -1))
    return ok, me, there


def apply_ratio(r, machine, me, there, direction, ratio_text):
    ratio = parse_ratio(ratio_text)
    if len(ratio) != 2:
        raise Fail("--ratio here takes A:B (anchor:terminal)")
    first, second = (there, me) if direction in ("right", "down") else (me, there)
    parts = ratio if direction in ("right", "down") else ratio[::-1]
    # Split the share the two hold together, so other siblings keep theirs
    # (a missing weight counts as 1).
    share = sum(1.0 if weight(n["node"]) is None else weight(n["node"]) for n in (first, second))
    parts = [p * share / sum(parts) for p in parts]
    if r == "app":
        for node, part in zip((first["node"], second["node"]), parts):
            app("layout.resize", id=qualify(machine, node["id"]), weight=part)
    else:
        ids = (first["node"]["id"], second["node"]["id"])

        def mutate(doc):
            for node_id, part in zip(ids, parts):
                locate(doc, node_id)["node"]["size"] = {"weight": part}
        doc_change(machine, mutate)
