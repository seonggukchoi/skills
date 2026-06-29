# JSON templates and jq automation patterns

`bw create`/`bw edit`/`bw move`/`bw send create` all take **base64-encoded JSON**. The REST bodies of `bw serve` take the same model as plaintext JSON. The starting point is always `bw get template <type>`.

## Template types

```bash
bw get template item            # generic item (shell)
bw get template item.login      # login info sub-object
bw get template item.card       # card
bw get template item.identity   # identity
bw get template item.securenote # secure note
bw get template item.field      # one custom field row
bw get template item.uri        # URI match entry
bw get template folder
bw get template org-collection
bw get template send.text
bw get template send.file
```

## item JSON schema (core fields)

```json
{
  "organizationId": null,
  "collectionIds": null,
  "folderId": null,
  "type": 1,
  "name": "Item name",
  "notes": null,
  "favorite": false,
  "fields": [],
  "login": null,
  "secureNote": null,
  "card": null,
  "identity": null,
  "reprompt": 0
}
```

- `type`: `1` login, `2` secure note, `3` card, `4` identity.
- `reprompt`: `0` or `1`. **Not a boolean** — the server rejects it if given wrong.
- Leave sub-objects that don't match the type as `null`, or omit them.

### login sub-object

```json
{
  "uris": [
    { "match": null, "uri": "https://example.com" }
  ],
  "username": "johndoe",
  "password": "secret",
  "totp": "otpauth://totp/..."
}
```

- `match`: `null` (default), `0` (domain), `1` (host), `2` (starts with), `3` (exact), `4` (regex), `5` (never).
- `totp` can take a whole otpauth URL or just the base32 secret.

### secureNote sub-object

```json
{ "type": 0 }
```

The body goes in `item.notes`.

### card sub-object

```json
{
  "cardholderName": "John Doe",
  "brand": "Visa",
  "number": "4242424242424242",
  "expMonth": "12",
  "expYear": "2030",
  "code": "123"
}
```

### identity sub-object

```json
{
  "title": "Mr",
  "firstName": "John",
  "lastName": "Doe",
  "email": "johndoe@example.com",
  "phone": "...",
  "address1": "...",
  "city": "...",
  "country": "KR"
}
```

### Custom fields (`fields` array)

```json
{ "name": "Recovery code", "value": "ABC-123", "type": 1, "linkedId": null }
```

`type`: `0` text, `1` hidden, `2` boolean, `3` linked.

## folder JSON

```json
{ "name": "Folder name" }
```

## org-collection JSON

```json
{
  "organizationId": "<org-id>",
  "name": "Collection name",
  "externalId": null,
  "groups": []
}
```

## send JSON (text)

```json
{
  "name": "My send",
  "notes": null,
  "type": 0,
  "text": { "text": "hello", "hidden": false },
  "file": null,
  "maxAccessCount": null,
  "deletionDate": "2026-06-01T00:00:00.000Z",
  "expirationDate": null,
  "password": null,
  "disabled": false,
  "hideEmail": false
}
```

- `type`: `0` text, `1` file.
- `deletionDate`/`expirationDate` are ISO 8601 UTC.

---

## jq pattern collection

### Create a new login item

```bash
PW="$(bw generate -ulns --length 32)"
bw get template item | jq \
  --arg name 'Postgres prod' \
  --arg user 'admin' \
  --arg pw  "$PW" \
  --arg uri 'postgres://db.example.com' \
  '.name=$name
   | .type=1
   | .login = (input | .username=$user | .password=$pw
                     | .uris=[{"match":null,"uri":$uri}])' \
  <(bw get template item.login) \
  | bw encode | bw create item
```

Pass `jq` a second input via `input` to compose the `item.login` template.

### Rotate just the password

```bash
ID=$(bw get item 'Postgres prod' | jq -r .id)
NEW=$(bw generate -ulns --length 32)
bw get item "$ID" \
  | jq --arg pw "$NEW" '.login.password=$pw' \
  | bw encode | bw edit item "$ID"
echo "$NEW"
```

### Bulk-create folders

```bash
for n in dev staging prod; do
  jq -n --arg n "$n" '{name:$n}' | bw encode | bw create folder
done
```

### Create a secure note

```bash
bw get template item | jq \
  --arg name 'On-call runbook' \
  --rawfile body ./runbook.md \
  '.name=$name | .type=2 | .notes=$body | .secureNote={type:0}' \
  | bw encode | bw create item
```

### Map an item to collections

```bash
echo '["coll-id-1","coll-id-2"]' | bw encode \
  | bw edit item-collections <item-id>
```

### Move a personal item to an organization

```bash
echo '["coll-id"]' | bw encode | bw move <item-id> <org-id>
```

### Create a text Send with single access + 24-hour expiry

```bash
DEL=$(date -u -v+1d +'%Y-%m-%dT%H:%M:%S.000Z')   # macOS date
bw send template send.text | jq \
  --arg t 'oneshot' \
  --arg body 'API token: ...' \
  --arg del "$DEL" \
  '.name=$t
   | .type=0
   | .text.text=$body
   | .maxAccessCount=1
   | .deletionDate=$del' \
  | bw encode | bw send create --fullObject \
  | jq -r '.accessUrl // .accessId'
```

Linux date: `date -u -d '+1 day' +'%Y-%m-%dT%H:%M:%S.000Z'`.

### Vault dump (for a pre-automation check)

```bash
bw sync -f
bw list items \
  | jq -r '.[] | [.id, .name, .login.username // ""] | @tsv'
```

### Bulk-extract passwords (search + extract)

```bash
bw list items --search 'aws' \
  | jq -r '.[] | select(.login.password) |
           "\(.name)\t\(.login.username)\t\(.login.password)"'
```

This is plaintext output, so never leave it in logs/history. Avoid `tee`/`> file`; if needed, capture it straight into a variable with `read` or similar.

### Bulk-back up attachments

```bash
mkdir -p ./bw-attachments
bw list items | jq -r '.[] | select(.attachments) |
  .id as $i | .attachments[] | "\($i)\t\(.id)\t\(.fileName)"' |
while IFS=$'\t' read -r item att name; do
  bw get attachment "$att" --itemid "$item" --output "./bw-attachments/${item}_${name}"
done
```

---

## Debugging tips

- Verify after creating: `bw get item <id> | jq`, then clean up with `bw delete item <id> --permanent` (for testing only).
- When `bw create`/`edit` fails silently, add `--response` to see `{success,message}`.
- If an integer field like `reprompt` was given as a boolean and you got a 422, check the JSON types.
- Don't forget that the `serve` API and the CLI use the same model but differ in the envelope (`{success,data,...}`).
