"""`tree` and `where`: read-only, safe on any machine."""

import json

from ..base import Fail
from ..doc import doc_get
from ..ids import one_machine, qualify, split_id
from ..tree import locate, show_tree, tabs


def cmd_tree(a):
    doc = doc_get(a.on)
    picked = []
    for sp, tb in tabs(doc):
        if not a.what:
            picked.append((sp, tb))
            continue
        for w in a.what:
            _, w = split_id(w)
            hit = locate(doc, w)
            if w in (sp["id"], sp.get("name"), tb["id"], tb.get("name")) or (hit and hit["tab"] is tb):
                picked.append((sp, tb))
                break
    if a.json:
        print(json.dumps([{"space": sp["id"], "space_name": sp.get("name"), "tab": tb["id"],
                           "tab_name": tb.get("name"), "root": tb["root"]} for sp, tb in picked],
                         ensure_ascii=False, indent=1))
        return
    if not picked:
        raise Fail("nothing matched")
    out = []
    for sp, tb in picked:
        out.append(f"space {qualify(a.on, sp['id'])} ({sp.get('name') or '-'}) "
                   f"tab {qualify(a.on, tb['id'])} ({tb.get('name') or '-'})")
        show_tree(tb["root"], a.on, out)
    print("\n".join(out))


def cmd_where(a):
    machine = one_machine(a.terminal, on=a.on)
    _, local = split_id(a.terminal)
    hit = locate(doc_get(machine), local)
    if not hit:
        raise Fail(f"{a.terminal} is not in any tab (it runs without a pane, or the id is wrong)")
    parent = hit["parent"]
    print(json.dumps({
        "machine": machine,
        "space": hit["space"]["id"], "space_name": hit["space"].get("name"),
        "tab": hit["tab"]["id"], "tab_name": hit["tab"].get("name"),
        "pane": hit["node"]["id"],
        "app_ids": {"space": qualify(machine, hit["space"]["id"]),
                    "tab": qualify(machine, hit["tab"]["id"]),
                    "pane": qualify(machine, hit["node"]["id"])},
        "parent": parent and {"id": parent["id"], "type": parent["type"], "index": hit["index"]},
    }, ensure_ascii=False, indent=1))
