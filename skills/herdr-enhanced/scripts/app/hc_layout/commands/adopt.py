"""`adopt`: add a running terminal that has no pane at the end of a tab."""

import json

from ..app import route, wait_for_pane
from ..base import Fail, sh
from ..doc import doc_change, doc_get
from ..edits import append_to_tab
from ..ids import one_machine, qualify, split_id
from ..steps import ensure_running, relabel
from ..tree import find_tab, locate, new_id


def cmd_adopt(a):
    r = route(a)
    if not (a.tab or a.tab_of):
        raise Fail("give --tab TAB or --tab-of TERMINAL")
    machine = one_machine(a.terminal, a.tab or a.tab_of)
    _, term_local = split_id(a.terminal)
    doc = doc_get(machine)
    if a.tab_of:
        hit = locate(doc, split_id(a.tab_of)[1])
        if not hit:
            raise Fail(f"{a.tab_of} is not in any tab")
        space, tab = hit["space"], hit["tab"]
    else:
        space, tab = find_tab(doc, split_id(a.tab)[1])
        if not tab:
            raise Fail(f"tab {a.tab} not found")
    ensure_running(machine, term_local)
    if locate(doc, term_local):
        raise Fail(f"{a.terminal} already has a pane; use `place` to move it")
    terminal = qualify(machine, term_local)
    if r == "app":
        sh(["hc", "label", terminal, f"herdr.space={space['id']}", f"herdr.tab={tab['id']}"])
        hit = wait_for_pane(terminal, qualify(machine, tab["id"]))
        pane = hit["pane"]
    else:
        def mutate(doc):
            _, tb = find_tab(doc, tab["id"])
            if not tb:
                raise Fail("the tab went away")
            block = {"content": {"terminal": term_local}, "id": new_id("p"), "type": "block"}
            append_to_tab(tb, block)
            return block["id"]
        pane = qualify(machine, doc_change(machine, mutate))
        relabel(machine, doc_get(machine), {tab["id"]})
    print(json.dumps({"via": r, "terminal": terminal, "tab": qualify(machine, tab["id"]),
                      "pane": pane}, indent=1))
