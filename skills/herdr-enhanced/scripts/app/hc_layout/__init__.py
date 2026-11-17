"""hc-layout: arrange panes in Herdr without stealing focus, from any machine.

Modules, from the bottom up:
  base      Fail, shell helpers, shared constants
  ids       `machine/id` handling and the one-machine rule
  tree      reading the split tree: walk, locate, find, describe, show
  doc       the layout document over `hc connect`: read, shape check, versioned write
  edits     tree edits for the doc route, following what the app itself writes
  app       the app route: `herdr-app do`, waiting for panes, placeholders, route choice
  steps     steps both routes share: relabel, start, ratio, verify
  commands  one module per subcommand
  cli       argument parsing and the entry point
"""
