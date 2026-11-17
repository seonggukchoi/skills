"""Tree edits for the doc route.

They follow what the app itself writes (measured): splitting a pane in its parent's
direction inserts beside it and halves its weight; splitting across wraps it in a new
group that takes its size; closing gives the weight back to a neighbour and unwraps a
group left with one child.
"""

from .base import Fail
from .tree import locate, new_id, weight


def detach(doc, node_id):
    """Take a block out of its tab. Returns the space/tab it left (they may be gone)."""
    hit = locate(doc, node_id)
    if not hit:
        return None
    sp, tb, node, parent, i = hit["space"], hit["tab"], hit["node"], hit["parent"], hit["index"]
    kids = parent["children"]
    kids.pop(i)
    w = weight(node)
    if w is not None and kids:
        heir = kids[i - 1] if i > 0 else kids[0]
        if weight(heir) is not None:
            heir["size"] = {"weight": weight(heir) + w}
    if parent is tb["root"]:
        if not kids:
            sp["tabs"].remove(tb)
            if not sp["tabs"]:
                doc["spaces"].remove(sp)
        return sp, tb
    if len(kids) == 1:
        grand = locate(doc, parent["id"])
        only = kids[0]
        if "size" in parent:
            only["size"] = parent["size"]
        else:
            only.pop("size", None)
        grand["parent"]["children"][grand["index"]] = only
    return sp, tb


def insert_beside(doc, anchor_id, block, direction):
    hit = locate(doc, anchor_id)
    if not hit:
        raise Fail(f"{anchor_id} is not in any tab")
    anchor, parent, i = hit["node"], hit["parent"], hit["index"]
    if parent is None:
        raise Fail("anchor is a tab's outermost split; give a pane")
    want = "row" if direction in ("right", "left") else "column"
    after = direction in ("right", "down")
    if parent["type"] == want:
        w = weight(anchor)
        if w is not None:
            anchor["size"] = {"weight": w / 2}
            block["size"] = {"weight": w / 2}
        parent["children"].insert(i + 1 if after else i, block)
    else:
        group = {"children": [anchor, block] if after else [block, anchor],
                 "id": new_id("s"), "type": want}
        if "size" in anchor:
            group["size"] = anchor.pop("size")
        parent["children"][i] = group
    return hit["space"], hit["tab"]


def append_to_tab(tab, block):
    root = tab["root"]
    kids = root["children"]
    if kids and all(weight(k) is not None for k in kids):
        last = kids[-1]
        half = weight(last) / 2
        last["size"] = {"weight": half}
        block["size"] = {"weight": half}
    kids.append(block)
