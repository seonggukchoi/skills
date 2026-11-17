"""`resize`: set the weights of a node and its siblings, in tree order."""

import json

from ..app import route, set_weights_app
from ..base import Fail
from ..doc import doc_change, doc_get
from ..ids import one_machine, qualify, split_id
from ..steps import parse_ratio
from ..tree import describe, locate, weight


def cmd_resize(a):
    r = route(a)
    machine = one_machine(a.target, on=a.on)
    _, local = split_id(a.target)
    hit = locate(doc_get(machine), local)
    if not hit:
        raise Fail(f"{a.target} is not in any tab")
    parent = hit["parent"]
    if parent is None:
        raise Fail(f"{a.target} is a tab's outermost split; give one of its children")
    ratio = parse_ratio(a.ratio)
    kids = parent["children"]
    if len(ratio) != len(kids):
        raise Fail(f"{parent['type']} {qualify(machine, parent['id'])} has {len(kids)} children "
                   f"(in order: {', '.join(describe(k) for k in kids)}); give {len(kids)} numbers")
    if r == "app":
        set_weights_app(machine, kids, ratio)
    else:
        ids = [k["id"] for k in kids]

        def mutate(doc):
            p = locate(doc, parent["id"])
            if not p or [k["id"] for k in p["node"]["children"]] != ids:
                raise Fail("that split changed while resizing; run it again")
            total = float(sum(ratio))
            for k, part in zip(p["node"]["children"], ratio):
                k["size"] = {"weight": part / total}
        doc_change(machine, mutate)
    after = locate(doc_get(machine), parent["id"])["node"]["children"]
    print(json.dumps({"via": r, "split": qualify(machine, parent["id"]), "direction": parent["type"],
                      "children": [{"id": qualify(machine, k["id"]), "what": describe(k),
                                    "weight": weight(k)} for k in after]}, indent=1))
