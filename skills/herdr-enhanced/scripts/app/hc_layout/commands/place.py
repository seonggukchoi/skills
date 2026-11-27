"""`place`: put a running terminal beside an anchor pane, then read the tree back."""

import json

from ..app import Placeholders, app, bring_into, route
from ..base import Fail
from ..doc import doc_change, doc_get
from ..edits import detach, insert_beside
from ..ids import one_machine, qualify, split_id
from ..steps import apply_ratio, ensure_running, relabel, verify_beside
from ..tree import locate, new_id, terminal_of


def cmd_place(a):
    r = route(a)
    machine = one_machine(a.terminal, a.anchor)
    _, term_local = split_id(a.terminal)
    _, anchor_local = split_id(a.anchor)
    doc = doc_get(machine)
    anchor = locate(doc, anchor_local)
    if not anchor or anchor["node"]["type"] != "block":
        raise Fail(f"anchor {a.anchor} is not a pane in any tab")
    anchor_id = anchor["node"]["id"]
    if terminal_of(anchor["node"]) == term_local:
        raise Fail("the terminal and the anchor are the same pane")
    ensure_running(machine, term_local)

    if r == "app":
        terminal = qualify(machine, term_local)
        anchor_pane = qualify(machine, anchor_id)
        base = "right" if a.direction in ("right", "left") else "down"
        with Placeholders() as ph:
            ph_terminal, ph_pane = ph.split(anchor_pane, base)
            if a.direction in ("left", "up"):
                app("pane.swap", pane=anchor_pane, target=ph_pane)
            bring_into(terminal, machine, anchor["space"]["id"], anchor["tab"]["id"], ph,
                       ph_terminal, ph_pane)
    else:
        def mutate(doc):
            old = locate(doc, term_local)
            block = old["node"] if old else {"content": {"terminal": term_local},
                                             "id": new_id("p"), "type": "block"}
            if old:
                detach(doc, old["node"]["id"])
                block.pop("size", None)
            sp, tb = insert_beside(doc, anchor_id, block, a.direction)
            return tb["id"]
        tab_id = doc_change(machine, mutate)
        relabel(machine, doc_get(machine), {tab_id})

    ok, me, there = verify_beside(machine, term_local, anchor_id, a.direction)
    if ok and a.ratio:
        apply_ratio(r, machine, me, there, a.direction, a.ratio)
    print(json.dumps({"via": r, "terminal": qualify(machine, term_local),
                      "pane": me and qualify(machine, me["node"]["id"]),
                      "beside": qualify(machine, anchor_id), "direction": a.direction,
                      "verified": ok}, indent=1))
    if not ok:
        raise Fail("placed, but the tree does not show it where asked; check with `tree`")
