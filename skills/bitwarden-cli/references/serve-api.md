# `bw serve` REST API

`bw serve` exposes an already-unlocked local CLI session over HTTP. There's no auth token; by default it binds only to `localhost` and blocks the `Origin` header to prevent CSRF. **Do not expose it externally.** Its purpose is to cut the cost of spawning a `bw` process on every call in automation.

## Starting it

```bash
export BW_SESSION="$(bw unlock --raw)"      # required beforehand
bw serve                                    # localhost:8087
bw serve --hostname 127.0.0.1 --port 8087
bw serve --hostname all --port 8087 --disable-origin-protection  # not recommended
```

Stop it with `Ctrl-C` or by killing the process. When `BW_SESSION` expires, restart the server.

## Response format

Every response is a uniform envelope:

```json
{
  "success": true,
  "data": { ... },
  "message": "..."
}
```

When `success: false`, look at the HTTP status code together with `message`.

## Endpoints (practical summary)

These map almost 1:1 to the CLI subcommands. In the `object` slot, put the same names you use in the CLI (`item`, `folder`, `collection`, `org-collection`, `send`, `attachment`, `organization`, `org-member`, etc.).

### Status & session

| Method | Path | Action | CLI equivalent |
| --- | --- | --- | --- |
| GET | `/status` | Server/lock status | `bw status` |
| POST | `/sync` | Sync (`?force=true` to force) | `bw sync` |
| GET | `/sync?lastSync=true` | Last sync timestamp | `bw sync --last` |
| POST | `/lock` | Lock | `bw lock` |
| POST | `/unlock` | Unlock with body `{ "password": "..." }` | `bw unlock` |
| GET | `/generate` | Pass options via query string — `length`, `uppercase`, `lowercase`, `number`, `special`, `passphrase`, `words`, `separator`, `capitalize`, `includeNumber`, `ambiguous`, `minNumber`, `minSpecial` | `bw generate` |

### Search & read

| Method | Path | Action |
| --- | --- | --- |
| GET | `/list/object/{object}` | List a collection. Query: `search`, `url`, `folderid`, `collectionid`, `organizationid`, `trash`, `archived` |
| GET | `/object/{object}/{id}` | Single object. `id` is a GUID or search term |
| GET | `/object/username/{id}` | Username only |
| GET | `/object/password/{id}` | Password only |
| GET | `/object/uri/{id}` | URI only |
| GET | `/object/totp/{id}` | 30-second OTP |
| GET | `/object/notes/{id}` | Notes |
| GET | `/object/exposed/{id}` | HIBP exposure count |
| GET | `/object/attachment/{id}?itemid=...` | Download an attachment (binary stream) |
| GET | `/object/template/{type}` | Empty template (`item`, `item.login`, `folder`, `send.text`, etc.) |
| GET | `/object/fingerprint/{id}` | User fingerprint phrase |

Collection forms (`items`, `folders`, `collections`, `org-collections`, `org-members`, `organizations`) for `{object}` match `/list/object/`, while single forms (`item`, `folder`, `password`, …) match `/object/`.

### Create, update, delete

| Method | Path | Action |
| --- | --- | --- |
| POST | `/object/{object}` | Create. Object JSON in the body (no base64 encoding — plaintext JSON) |
| POST | `/object/attachment` | Send a file via `multipart/form-data` or with `?itemid=...` |
| PUT | `/object/{object}/{id}` | Update. Object JSON in the body |
| PUT | `/object/item-collections/{id}` | Map item → collections. Body is an array of collection ids |
| DELETE | `/object/{object}/{id}` | Delete. `?permanent=true` for permanent deletion |
| POST | `/restore/item/{id}` | Restore from trash/archive |
| POST | `/archive/item/{id}` | Move to archive |
| POST | `/move/{id}/{organizationId}` | Move to organization. Body is an array of collection ids |
| POST | `/confirm/org-member/{id}?organizationId=...` | Confirm a member |

### Send

| Method | Path | Action |
| --- | --- | --- |
| GET | `/list/object/send` | List my Sends |
| GET | `/object/send/{id}` | A specific Send |
| POST | `/object/send` | New Send (text/file via multipart) |
| PUT | `/object/send/{id}` | Edit |
| DELETE | `/object/send/{id}` | Delete |
| POST | `/object/send/{id}/remove-password` | Remove the access password |

## Quick examples (curl)

```bash
# Status
curl -s http://localhost:8087/status | jq .

# Unlock (safer to do it in the CLI before starting the server)
curl -s -X POST http://localhost:8087/unlock \
  -H 'Content-Type: application/json' \
  -d '{"password":"masterpw"}' | jq .

# Force sync
curl -s -X POST 'http://localhost:8087/sync?force=true' | jq .

# Search
curl -s 'http://localhost:8087/list/object/items?search=github' | jq '.data.data[].name'

# Password only
curl -s 'http://localhost:8087/object/password/github.com' | jq -r .data.data

# TOTP
curl -s 'http://localhost:8087/object/totp/github.com' | jq -r .data.data

# New folder
curl -s -X POST http://localhost:8087/object/folder \
  -H 'Content-Type: application/json' \
  -d '{"name":"DevOps"}' | jq .

# Edit an item (GET first → modify → PUT)
ITEM_ID=...
curl -s "http://localhost:8087/object/item/$ITEM_ID" \
  | jq '.data | .login.password = "new-pw"' \
  | curl -s -X PUT "http://localhost:8087/object/item/$ITEM_ID" \
      -H 'Content-Type: application/json' -d @- | jq .

# Password generator
curl -s 'http://localhost:8087/generate?length=24&uppercase=true&lowercase=true&number=true&special=true' \
  | jq -r .data.data

# Send (text)
curl -s -X POST http://localhost:8087/object/send \
  -H 'Content-Type: application/json' \
  -d '{"name":"q4","type":0,"text":{"text":"hello","hidden":false},"deletionDate":"2026-06-01T00:00:00.000Z"}'
```

## Notes on payload shape

- The JSON that `bw create item` takes on the CLI and the server's body JSON are the same model. The difference is that the server takes **plaintext JSON without base64 encoding**.
- Some fields like `reprompt` are integers (`0`/`1`), not booleans. The wrong type yields a 422.
- Send file attachments as `multipart/form-data`. The field name is `file`.

## Security

- No token — a `localhost` trust model. Beware of exposure to other users or containers on the same machine.
- `--hostname all` effectively throws an unauthenticated password manager onto the network. If you truly need it, isolate it with an SSH tunnel / firewall.
- Use `--disable-origin-protection` only when you want to call it from a browser, and only from a trusted page.
- While the server is up, the vault is unlocked in memory. As soon as you're done, shut it down + `bw lock`.
