# When something fails or looks wrong

These traps sit between an observation and a conclusion. No error points at them; the conclusion
simply comes out wrong and confident.

The symptom tables for each CLI:
[tui/diagnosing.md](../tui/diagnosing.md) (TUI symptoms and the premise to doubt, verification
commands that read backwards, the source of truth for live targets) ·
[app/delegating.md](../app/delegating.md) (hc refusals: `blocked`, `finished`).

## Something failing for no reason is a signal to recheck premises, not to route around

In the incident where suggestion text was taken for an approval
([reading-screens.md](reading-screens.md)), the moment Enter did not take twice was the moment to
doubt the judgment. Instead, a different route was taken and the incident completed itself.

**When a route fails for no reason, it does not mean find another way — it means a premise is
wrong.** Before looking for another path, find what you assumed wrongly.

## Do not promote circumstance into cause

**The better something fits a trap you know, the harder you should look for a counterexample.**
There is a case where exit times one second apart were read as "evidence one command killed several."
In fact a person had simply shut them down back to back.

In the same family: a symptom report can be accurate while **its attribution of cause is wrong.** The
value of a report is in the symptom observed, not the cause proposed. The receiving side re-verifies
the cause.

## Do not turn a failed confirmation straight into a resend

A timeout or a stalled wait does not prove the text was never delivered (the official `herdr` skill
says the same). Resend on that basis and you produce a duplicate submission. For the same reason, do
not stack repeated wait commands just because no response came. What to wait for is covered in
[protocol-waiting.md](protocol-waiting.md).

## Do not parse transcripts to find a target

Do not identify sessions through `~/.claude/projects/**/*.jsonl`. Those files **mix in secrets and
personal data, so pulling them into context is itself risky**, and the result is guesswork besides.

The source of truth for live targets is the multiplexer's own listing (`herdr agent list` and
`herdr pane list` in the TUI, `hc ls` in hc mode), queried without narrowing its scope. Not there
means it does not know about it. Do not fill the gap with a guess; ask which one.
