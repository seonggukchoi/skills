"""hc-layout: arrange panes in Herdr without stealing focus, from any machine.

Two routes, chosen automatically:
  app  The Herdr app is reachable here (`herdr-app status` works): every change goes
       through its public commands (`herdr-app do`, `hc label`). The layout document is
       only read, to see the split tree.
  doc  No Herdr app here (a remote machine over ssh): the change is written to that
       machine's layout document with `doc.set`, guarded by a version check, after the
       document's shape is checked. Every Herdr client (desktop, mobile) draws from
       that document, so the result shows the same everywhere.
Force one with --via app|doc.

Commands
  tree  [WHAT...] [--on M] [--json]        split trees (WHAT: space/tab/terminal id or name)
  where TERMINAL [--on M]                  the space, tab and pane holding a terminal
  open  --anchor X --direction D [--cwd DIR] [-- CMD...]
  open  --new-tab-in SPACE [--name N] [--cwd DIR] [-- CMD...]
                                           start a terminal (default: the machine's shell)
                                           beside pane X, or as a new tab
  place TERMINAL --anchor X --direction right|down|left|up [--ratio A:B]
                                           put a running terminal (background, or in another
                                           pane) beside X; --ratio is anchor:terminal
  resize TARGET --ratio A:B[:C...]         TARGET and its siblings, in tree order
                                           (TARGET: pane id, terminal, or group id from `tree`)
  move-tab TAB --to-space SPACE [--index N]
                                           move a tab, with its tree and sizes, to another
                                           space on the same machine
  adopt TERMINAL --tab-of T | --tab TAB    add a running terminal at the end of a tab

Ids: the app shows another machine's ids as `machine/id`; both forms are accepted.
A terminal belongs to its machine: nothing here moves one across machines.
"""

import argparse
import sys

from .base import Fail
from .commands.adopt import cmd_adopt
from .commands.move_tab import cmd_move_tab
from .commands.open import cmd_open
from .commands.place import cmd_place
from .commands.read import cmd_tree, cmd_where
from .commands.resize import cmd_resize


def main():
    p = argparse.ArgumentParser(prog="hc-layout", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--via", choices=["app", "doc"], help="force a route (default: app when reachable)")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("tree"); s.add_argument("what", nargs="*"); s.add_argument("--on")
    s.add_argument("--json", action="store_true"); s.set_defaults(fn=cmd_tree)
    s = sub.add_parser("where"); s.add_argument("terminal"); s.add_argument("--on")
    s.set_defaults(fn=cmd_where)
    s = sub.add_parser("open"); s.add_argument("--anchor"); s.add_argument("--new-tab-in")
    s.add_argument("--direction", choices=["right", "down", "left", "up"])
    s.add_argument("--ratio"); s.add_argument("--name"); s.add_argument("--cwd")
    s.add_argument("cmd", nargs=argparse.REMAINDER); s.set_defaults(fn=cmd_open)
    s = sub.add_parser("place"); s.add_argument("terminal"); s.add_argument("--anchor", required=True)
    s.add_argument("--direction", required=True, choices=["right", "down", "left", "up"])
    s.add_argument("--ratio"); s.set_defaults(fn=cmd_place)
    s = sub.add_parser("resize"); s.add_argument("target"); s.add_argument("--ratio", required=True)
    s.add_argument("--on"); s.set_defaults(fn=cmd_resize)
    s = sub.add_parser("move-tab"); s.add_argument("tab"); s.add_argument("--to-space", required=True)
    s.add_argument("--index", type=int); s.set_defaults(fn=cmd_move_tab)
    s = sub.add_parser("adopt"); s.add_argument("terminal"); s.add_argument("--tab")
    s.add_argument("--tab-of"); s.set_defaults(fn=cmd_adopt)
    a = p.parse_args()
    try:
        a.fn(a)
    except Fail as e:
        print(f"hc-layout: {e}", file=sys.stderr)
        sys.exit(1)
