# Diagnosing with the herdr CLI

Rechecking premises instead of routing around, not promoting circumstance into cause, not resending
on a failed confirmation, and not parsing transcripts are in
[common/diagnosing.md](../common/diagnosing.md). Reading suggestion text and questions on screen is
in [common/reading-screens.md](../common/reading-screens.md). This file is what those look like in
herdr.

## Read state, not screen text

herdr recognizes agent status and has a snapshot made for detection, so you do not have to judge
suggestion text by eye.

```bash
herdr agent get <target>
herdr agent read <target> --source detection
```

## Symptoms and the premise to doubt

| Symptom | Premise to doubt |
|---|---|
| Agent startup ends in a timeout | Was that pane really an empty shell at a prompt |
| A prompt is rejected as stalled (`agent_prompt_stalled`) | **Is the other side really processing your text.** The submission was already accepted (the official skill's `agent prompt` notes), so **the text is already with them.** Do not resend; check with `agent get` and `agent read` whether it was processed |
| Reading returns nothing | Is it the right target pane. Is it running on an alternate screen |
| A command landed on someone else's pane | Did an omitted target grab the focused pane ([targeting.md](targeting.md)) |
| A layout command exited 0 but nothing looks different | Did it change anything: read `changed` ([splitting.md](splitting.md), "Verification commands that read backwards") |

## The source of truth for live targets

```bash
herdr agent list
herdr pane list          # this is where you check the source of truth — narrowing with --workspace falsifies the conclusion that herdr does not know
herdr workspace list
```

Not here means herdr does not know about it. Do not fill the gap with a guess; ask which one.
