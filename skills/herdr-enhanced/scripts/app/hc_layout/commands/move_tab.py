"""`move-tab`: move a tab, with its tree and sizes, to another space on the same machine."""

import json

from ..app import Placeholders, app, app_panes, bring_into, route, set_weights_app, wait_for_pane
from ..base import PLACEHOLDER, Fail
from ..doc import doc_change, doc_get
from ..ids import one_machine, qualify, split_id
from ..steps import relabel
from ..tree import describe, find_space, find_tab, terminals_under, walk, weight


def cmd_move_tab(a):
    r = route(a)
    machine = one_machine(a.tab, a.to_space)
    _, tab_local = split_id(a.tab)
    _, space_local = split_id(a.to_space)
    doc = doc_get(machine)
    src_space, src_tab = find_tab(doc, tab_local)
    if not src_tab:
        raise Fail(f"tab {a.tab} not found")
    dst_space = find_space(doc, space_local)
    if not dst_space:
        raise Fail(f"space {a.to_space} not found on {machine or 'this computer'}")
    if dst_space["id"] == src_space["id"]:
        if a.index:
            if r == "app":
                app("tab.move", id=qualify(machine, src_tab["id"]), index=a.index)
            else:
                def reorder(doc):
                    sp, tb = find_tab(doc, src_tab["id"])
                    sp["tabs"].remove(tb)
                    sp["tabs"].insert(max(0, a.index - 1), tb)
                doc_change(machine, reorder)
            print(json.dumps({"via": r, "tab": qualify(machine, src_tab["id"]), "index": a.index}))
            return
        raise Fail("already in that space")

    if r == "doc":
        def mutate(doc):
            sp, tb = find_tab(doc, src_tab["id"])
            dst = find_space(doc, dst_space["id"])
            if not tb or not dst:
                raise Fail("the tab or the space went away")
            sp["tabs"].remove(tb)
            if not sp["tabs"]:
                doc["spaces"].remove(sp)
            pos = len(dst["tabs"]) if not a.index else max(0, a.index - 1)
            dst["tabs"].insert(pos, tb)
        doc_change(machine, mutate)
        relabel(machine, doc_get(machine), {src_tab["id"]})
        print(json.dumps({"via": r, "tab": qualify(machine, src_tab["id"]),
                          "space": qualify(machine, dst_space["id"])}, indent=1))
        return

    src_root = json.loads(json.dumps(src_tab["root"]))
    shown = app_panes()
    for term in terminals_under(src_root):
        if qualify(machine, term) not in shown:
            raise Fail(f"{term} is in the tab but not shown by the app; nothing was moved")
    with Placeholders() as ph:
        made = app("tab.new", space=qualify(machine, dst_space["id"]),
                   name=src_tab.get("name") or None, argv=PLACEHOLDER, focus=False)
        ph.add(made["terminal"])
        new_tab_app = made["tab"]
        _, new_tab_local = split_id(new_tab_app)
        root_ph_pane = wait_for_pane(made["terminal"], new_tab_app)["pane"]

        def build(node, ph_terminal, ph_pane):
            if node["type"] == "block":
                content = node.get("content") or {}
                if content.get("terminal"):
                    bring_into(qualify(machine, content["terminal"]), machine, dst_space["id"],
                               new_tab_local, ph, ph_terminal, ph_pane)
                else:
                    res = app("pane.split", direction="right", pane=ph_pane,
                              mod=content.get("mod"), props=content.get("props"))
                    app("pane.swap", pane=res["pane"], target=ph_pane)
                    ph.drop(ph_terminal)
                return
            direction = "right" if node["type"] == "row" else "down"
            slots = [(ph_terminal, ph_pane)]
            for _ in node["children"][1:]:
                slots.append(ph.split(slots[-1][1], direction))
            for child, (t, p) in zip(node["children"], slots):
                build(child, t, p)

        build(src_root, made["terminal"], root_ph_pane)

    _, new_tab = find_tab(doc_get(machine), new_tab_local)
    by_key = {(n["type"], tuple(terminals_under(n))): n for n, *_ in walk(new_tab["root"])
              if terminals_under(n)}
    missed = []
    for n, parent, _, _ in walk(src_root):
        if parent is None or n is not parent["children"][0]:
            continue
        weights = [weight(k) for k in parent["children"]]
        if all(w is None for w in weights):
            continue
        weights = [1.0 if w is None else w for w in weights]
        targets = [by_key.get((k["type"], tuple(terminals_under(k)))) for k in parent["children"]]
        if any(t is None for t in targets):
            missed.append(describe(parent))
            continue
        set_weights_app(machine, targets, weights)
    if a.index:
        app("tab.move", id=new_tab_app, index=a.index)
    print(json.dumps({"via": r, "tab": new_tab_app, "space": qualify(machine, dst_space["id"]),
                      "sizes_not_matched": missed}, indent=1))
    if missed:
        raise Fail("moved, but some split sizes could not be matched; adjust them with `resize`")
