"""The app route: public `herdr-app` and `hc` commands only, and the choice of route."""

import json
import subprocess
import time

from .base import PLACEHOLDER, WAIT_SECONDS, Fail, sh, sh_json
from .ids import qualify


def app(command, **kw):
    args = {k: v for k, v in kw.items() if v is not None}
    return sh_json(["herdr-app", "do", command, json.dumps(args)])


def app_available():
    try:
        p = subprocess.run(["herdr-app", "status"], capture_output=True, text=True, timeout=10)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    return p.returncode == 0 and p.stdout.strip().startswith("{")


def route(a):
    if a.via == "app" and not app_available():
        raise Fail("--via app: `herdr-app status` cannot reach a Herdr app here")
    if a.via:
        return a.via
    return "app" if app_available() else "doc"


def app_panes():
    out = {}
    for sp in sh_json(["herdr-app", "ls"])["spaces"]:
        for tb in sp["tabs"]:
            for t in tb["terminals"]:
                out[t["terminal"]] = {"pane": t["pane"], "tab": tb["id"], "space": sp["id"]}
    return out


def wait_for_pane(terminal, tab=None):
    deadline = time.time() + WAIT_SECONDS
    while time.time() < deadline:
        hit = app_panes().get(terminal)
        if hit and (tab is None or hit["tab"] == tab):
            return hit
        time.sleep(0.3)
    raise Fail(f"{terminal} did not appear in tab {tab} within {WAIT_SECONDS}s")


def wait_gone(terminal):
    deadline = time.time() + WAIT_SECONDS
    while time.time() < deadline:
        if terminal not in app_panes():
            return
        time.sleep(0.3)
    raise Fail(f"{terminal} still has a pane after parking")


def split_placeholder(anchor_pane, direction):
    r = app("pane.split", direction=direction, pane=anchor_pane, argv=PLACEHOLDER)
    return r["terminal"], r["pane"]


def drop_placeholder(ph_terminal, ph_pane):
    app("pane.close", pane=ph_pane)
    deadline = time.time() + WAIT_SECONDS
    while time.time() < deadline:
        p = sh(["hc", "get", ph_terminal, "--json"], check=False)
        if p.returncode != 0:
            return
        if json.loads(p.stdout).get("state") == "finished":
            sh(["hc", "rm", ph_terminal], check=False)
            return
        time.sleep(0.3)


def bring_into(terminal, machine, space_local, tab_local, ph_terminal, ph_pane):
    """App route: put `terminal` where the placeholder is, then drop the placeholder."""
    if app_panes().get(terminal):
        app("terminal.park", terminal=terminal)
        wait_gone(terminal)
    sh(["hc", "label", terminal, f"herdr.space={space_local}", f"herdr.tab={tab_local}"])
    landed = wait_for_pane(terminal, qualify(machine, tab_local))
    app("pane.swap", pane=landed["pane"], target=ph_pane)
    drop_placeholder(ph_terminal, ph_pane)
    return landed["pane"]


def set_weights_app(machine, nodes, ratio):
    total = float(sum(ratio))
    for node, part in zip(nodes, ratio):
        app("layout.resize", id=qualify(machine, node["id"]), weight=part / total)
