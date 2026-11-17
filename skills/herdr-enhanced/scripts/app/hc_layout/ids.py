"""Ids as the app shows them: `machine/id` for another machine, a bare id for this one."""

from .base import Fail


def split_id(ident):
    """`machine/id` -> (machine, id); bare id -> (None, id)."""
    if ident and "/" in ident:
        m, i = ident.split("/", 1)
        return m, i
    return None, ident


def qualify(machine, ident):
    return f"{machine}/{ident}" if machine else ident


def one_machine(*idents, on=None):
    machines = {m for m, _ in map(split_id, [i for i in idents if i])} - {None}
    if on:
        machines.add(on)
    if len(machines) > 1:
        raise Fail("a terminal belongs to its machine; these ids are on different machines: "
                   + ", ".join(sorted(machines)))
    return machines.pop() if machines else None
