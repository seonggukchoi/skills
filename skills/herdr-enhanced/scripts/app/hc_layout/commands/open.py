"""`open`: start a terminal beside an anchor pane, or as a new tab in a space."""

import json

from ..app import app, route
from ..base import Fail
from ..doc import doc_change, doc_get
from ..ids import one_machine, qualify, split_id
from ..steps import apply_ratio, relabel, start_terminal, verify_beside
from ..tree import find_space, locate, new_id
from .place import cmd_place


def cmd_open(a):
    r = route(a)
    argv = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd
    if bool(a.anchor) == bool(a.new_tab_in):
        raise Fail("give either --anchor with --direction, or --new-tab-in")
    if a.anchor:
        if not a.direction:
            raise Fail("--anchor needs --direction")
        machine = one_machine(a.anchor)
        _, anchor_local = split_id(a.anchor)
        hit = locate(doc_get(machine), anchor_local)
        if not hit or hit["node"]["type"] != "block":
            raise Fail(f"anchor {a.anchor} is not a pane in any tab")
        if r == "app" and a.direction in ("right", "down"):
            res = app("pane.split", direction=a.direction, pane=qualify(machine, hit["node"]["id"]),
                      argv=argv or None)
            _, term_local = split_id(res["terminal"])
            ok, me, there = verify_beside(machine, term_local, hit["node"]["id"], a.direction)
            if ok and a.ratio:
                apply_ratio(r, machine, me, there, a.direction, a.ratio)
            print(json.dumps({"via": r, "terminal": res["terminal"], "pane": res["pane"],
                              "verified": ok}, indent=1))
            return
        term_local = start_terminal(machine, a.cwd, argv)
        a.terminal = qualify(machine, term_local)
        cmd_place(a)
        return
    machine = one_machine(a.new_tab_in)
    _, space_local = split_id(a.new_tab_in)
    space = find_space(doc_get(machine), space_local)
    if not space:
        raise Fail(f"space {a.new_tab_in} not found")
    if r == "app":
        res = app("tab.new", space=qualify(machine, space["id"]), name=a.name, folder=a.cwd,
                  argv=argv or None, focus=False)
        print(json.dumps({"via": r, **res}, indent=1))
        return
    tab_id = new_id("tb")
    term_local = start_terminal(machine, a.cwd, argv)

    def mutate(doc):
        sp = find_space(doc, space["id"])
        if not sp:
            raise Fail("the space went away")
        sp["tabs"].append({"id": tab_id, "name": a.name or "",
                           "root": {"children": [{"content": {"terminal": term_local},
                                                  "id": new_id("p"), "type": "block"}],
                                    "id": tab_id, "type": "row"}})
    doc_change(machine, mutate)
    relabel(machine, doc_get(machine), {tab_id})
    print(json.dumps({"via": r, "space": qualify(machine, space["id"]),
                      "tab": qualify(machine, tab_id), "terminal": qualify(machine, term_local)},
                     indent=1))
