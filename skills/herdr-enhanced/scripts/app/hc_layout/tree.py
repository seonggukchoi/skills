"""Reading a layout document's split tree. Nothing here changes it."""

import uuid

from .ids import qualify


def walk(node, parent=None, index=0, depth=0):
    yield node, parent, index, depth
    for i, child in enumerate(node.get("children") or []):
        yield from walk(child, node, i, depth + 1)


def terminal_of(node):
    return (node.get("content") or {}).get("terminal") if node.get("type") == "block" else None


def terminals_under(node):
    return [terminal_of(n) for n, *_ in walk(node) if terminal_of(n)]


def weight(node):
    return (node.get("size") or {}).get("weight")


def tabs(doc):
    for sp in doc["spaces"]:
        for tb in sp["tabs"]:
            yield sp, tb


def locate(doc, ident):
    """A node (pane, group, tab root) or a terminal -> dict, or None."""
    for sp, tb in tabs(doc):
        for node, parent, index, _ in walk(tb["root"]):
            if node.get("id") == ident or terminal_of(node) == ident:
                return {"space": sp, "tab": tb, "node": node, "parent": parent, "index": index}
    return None


def find_tab(doc, ident):
    for sp, tb in tabs(doc):
        if ident in (tb["id"], tb.get("name")):
            return sp, tb
    hit = locate(doc, ident)
    return (hit["space"], hit["tab"]) if hit else (None, None)


def find_space(doc, ident):
    for sp in doc["spaces"]:
        if ident in (sp["id"], sp.get("name")):
            return sp
    hit = locate(doc, ident)
    return hit["space"] if hit else None


def new_id(prefix):
    return prefix + uuid.uuid4().hex


def describe(node):
    t = terminal_of(node)
    if t:
        return t
    if node["type"] == "block":
        return f"mod:{(node.get('content') or {}).get('mod')}"
    return f"{node['type']}[{', '.join(terminals_under(node))}]"


def show_tree(node, machine, out, depth=1):
    pad = "  " * depth
    w = weight(node)
    ws = f" weight={w:g}" if isinstance(w, (int, float)) else ""
    if node["type"] == "block":
        content = node.get("content") or {}
        label = content.get("terminal") or f"mod:{content.get('mod')}"
        out.append(f"{pad}pane {qualify(machine, node['id'])} [{label}]{ws}")
    else:
        word = {"row": "row (side by side)", "column": "column (stacked)"}[node["type"]]
        out.append(f"{pad}{word} {qualify(machine, node['id'])}{ws}")
        for child in node["children"]:
            show_tree(child, machine, out, depth + 1)
