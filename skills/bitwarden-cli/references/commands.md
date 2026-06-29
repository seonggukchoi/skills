# `bw` subcommand reference

Options and examples extracted from `bw --help` and each `bw <cmd> --help`, collected in one place. Based on `bw` 2026.4.x. Commands are ordered by workflow (auth → data → utilities), not alphabetically.

## Table of contents

- Auth & session: `login`, `logout`, `unlock`, `lock`, `sync`, `status`, `config`
- Data operations: `list`, `get`, `create`, `edit`, `delete`, `restore`, `archive`, `move`, `confirm`
- Import/export: `import`, `export`
- Send: `send` (`list`, `template`, `get`, `create`, `edit`, `remove-password`, `delete`), `receive`
- Utilities: `generate`, `encode`, `serve`, `update`, `completion`, `sdk-version`

For global options, see the "Global options" table in SKILL.md.

---

## login

```
bw login [options] [email] [password]
```

| Option | Description |
| --- | --- |
| `--method <n>` | 2FA method. 0=Authenticator, 1=Email, 3=Yubikey, 4=U2F, 5=Duo |
| `--code <code>` | 2FA code |
| `--sso [identifier]` | SSO login (organization identifier optional) |
| `--apikey` | API key login. Uses `BW_CLIENTID`/`BW_CLIENTSECRET` |
| `--passwordenv <var>` | Read the password from an environment variable |
| `--passwordfile <path>` | Read the password from the first line of a file |
| `--check` | Only check the current login state |

```bash
bw login
bw login johndoe@example.com 'pw' --raw            # session key only to stdout
bw login johndoe@example.com 'pw' --method 0 --code 249213
bw login --sso my-org
bw login --apikey                                # uses BW_CLIENTID/SECRET
```

Adding `--raw` prints only the session key instead of a human message → export it straight into `BW_SESSION`.

## logout

```
bw logout
```
No arguments. Logs out the current user.

## unlock

```
bw unlock [options] [password]
```

| Option | Description |
| --- | --- |
| `--check` | Only check the lock state |
| `--passwordenv <var>` | Password from an environment variable |
| `--passwordfile <path>` | Password from a file |

```bash
bw unlock
bw unlock 'masterpw' --raw                       # session key only
bw unlock --passwordenv BW_MASTER --raw
```

A new session key is issued each time, and **the previous key is invalidated immediately.**

## lock

```
bw lock
```
Destroys the session key. Stays logged in.

## sync

```
bw sync [options]
```

| Option | Description |
| --- | --- |
| `-f`, `--force` | Forced full sync |
| `--last` | Print only the last sync timestamp |

## status

```
bw status
```

Example JSON output:
```json
{
  "serverUrl": "https://vault.example.com",
  "lastSync": "2025-06-16T06:33:51.419Z",
  "userEmail": "johndoe@example.com",
  "userId": "00000000-0000-0000-0000-000000000000",
  "status": "locked"
}
```

`status` ∈ {`unauthenticated`, `locked`, `unlocked`}.

## config

```
bw config <setting> [value]
bw config <setting>            # print the current value
```

| Option | Description |
| --- | --- |
| `--web-vault <url>` | Web vault URL |
| `--api <url>` | API URL |
| `--identity <url>` | Identity URL |
| `--icons <url>` | Icon service URL |
| `--notifications <url>` | Notification service URL |
| `--events <url>` | Event service URL |
| `--key-connector <url>` | Key Connector URL |

Supported `setting`: currently only `server`.

```bash
bw config server                                  # print the current server
bw config server https://vault.example.com
bw config server --api http://localhost:4000 \
                --identity http://localhost:33656
```

**Cannot be changed while logged in** — change it after `bw logout`.

---

## list

```
bw list <object>
```

`object` ∈ {`items`, `folders`, `collections`, `org-collections`, `org-members`, `organizations`}.

| Option | Description |
| --- | --- |
| `--search <q>` | Partial-match search on name/URI/notes |
| `--url <url>` | Filter login items by URL match |
| `--folderid <id>` | Filter by folder id. `null`/`notnull` allowed |
| `--collectionid <id>` | Filter by collection id |
| `--organizationid <id>` | Filter by organization id. `null`/`notnull` allowed |
| `--trash` | Trash items only |
| `--archived` | Archived items only |

Search + filter = AND. Filters with each other = OR.

```bash
bw list items
bw list items --search aws
bw list items --url https://github.com
bw list items --folderid null
bw list items --organizationid notnull
bw list items --folderid <id> --organizationid notnull
bw list items --trash
bw list folders --search dev
bw list org-members --organizationid <org-id>
```

## get

```
bw get <object> <id>
```

`object` ∈ {`item`, `username`, `password`, `uri`, `totp`, `notes`, `exposed`, `attachment`, `folder`, `collection`, `org-collection`, `organization`, `template`, `fingerprint`, `send`}.

`id` is a GUID or a search term (when it matches uniquely).

| Option | Description |
| --- | --- |
| `--itemid <id>` | The parent item id when fetching an attachment |
| `--output <path>` | Where to save an attachment (file or directory) |
| `--organizationid <id>` | When fetching an organization object |

```bash
bw get item 99ee88d2-6046-4ea7-92c2-acac464b1412
bw get password github.com
bw get totp github.com                   # 30-second OTP
bw get notes github.com
bw get exposed yahoo.com                 # HIBP exposure count
bw get attachment b857igwl1dzrs2 --itemid <id> --output ./photo.jpg
bw get attachment photo.jpg --itemid <id> --raw > ./photo.jpg
bw get folder email
bw get template folder
bw get template item.login
bw get fingerprint me                    # my fingerprint phrase
```

`template` returns an empty object — a starting point for `create/edit`.

## create

```
bw create <object> [encodedJson]
```

`object` ∈ {`item`, `attachment`, `folder`, `org-collection`}.

| Option | Description |
| --- | --- |
| `--file <path>` | Attachment file path |
| `--itemid <id>` | Attachment parent item id |
| `--organizationid <id>` | When creating an organization object |

```bash
echo '{"name":"DevOps"}' | bw encode | bw create folder
bw create folder eyJuYW1lIjoiRGV2T3BzIn0=
bw create attachment --file ./key.pem --itemid <item-id>
```

`encodedJson` is base64-encoded JSON. Piping via stdin is recommended.

## edit

```
bw edit <object> <id> [encodedJson]
```

`object` ∈ {`item`, `item-collections`, `folder`, `org-collection`}.

| Option | Description |
| --- | --- |
| `--organizationid <id>` | When editing an organization object |

```bash
bw get folder <id> | jq '.name="Renamed"' | bw encode | bw edit folder <id>
# Map an item to collections
echo '["coll-id-1","coll-id-2"]' | bw encode \
  | bw edit item-collections <item-id>
```

## delete

```
bw delete <object> <id>
```

`object` ∈ {`item`, `attachment`, `folder`, `org-collection`}.

| Option | Description |
| --- | --- |
| `--itemid <id>` | Parent item when deleting an attachment |
| `--organizationid <id>` | Organization object |
| `-p`, `--permanent` | Permanently delete without going through trash (item only) |

```bash
bw delete item <id>
bw delete item <id> --permanent
bw delete folder <id>
bw delete attachment <att-id> --itemid <item-id>
```

## restore

```
bw restore item <id>
```
Restore from trash/archive. Object is `item` only.

## archive

```
bw archive item <id>
```
Move to archive. Object is `item` only.

## move

```
bw move <id> <organizationId> [encodedJson]
```
Personal item → organization. `encodedJson` is an array of collection ids (base64-encoded).

```bash
echo '["coll-id"]' | bw encode | bw move <item-id> <org-id>
```

`bw share` is deprecated — use `bw move` instead.

## confirm

```
bw confirm org-member <id> --organizationid <org-id>
```
Confirm an organization member's enrollment. Object is `org-member` only.

---

## import

```
bw import [format] [input]
```

| Option | Description |
| --- | --- |
| `--formats` | List of supported formats |
| `--organizationid <id>` | Import into an organization |

```bash
bw import --formats
bw import bitwardencsv ./source.csv
bw import bitwardenjson ./vault.json
bw import keepass2xml ./kp.xml
bw import --organizationid <id> bitwardencsv ./shared.csv
```

Supported formats (the common ones): `bitwardenjson`, `bitwardencsv`, `lastpasscsv`, `1password1pif`, `1password1pux`, `keepass2xml`, `keepassxcsv`, `dashlanejson`, `chromecsv`, `firefoxcsv`, `safaricsv`, `enpasscsv`, and so on. For the full list, `bw import --formats`.

## export

```
bw export [options]
```

| Option | Description |
| --- | --- |
| `--output <path>` | Output path (file or directory) |
| `--format <fmt>` | `csv` (default), `json`, `encrypted_json`, `zip` |
| `--password [pw]` | Wrapping password for `encrypted_json` |
| `--organizationid <id>` | Organization export |

```bash
bw export                                       # CSV
bw export --format json --output ./bw.json
bw export 'masterpw' --format json
bw export --format encrypted_json --password 'wrap' --output bw.enc.json
bw export --organizationid <id> --format zip
bw --raw export                                 # stdout
```

`csv`/`json` are **plaintext**; `encrypted_json` is wrapped with a separate password.

---

## send (Bitwarden Send)

### Quick creation
```
bw send <data>
```

| Option | Description |
| --- | --- |
| `-f`, `--file` | `<data>` is a file path |
| `-d`, `--deleteInDays <n>` | Expiration (days). Default 7 |
| `--password <pw>` | Access password |
| `--emails <a,b>` | Comma-separated recipient emails |
| `-a`, `--maxAccessCount <n>` | Maximum access count |
| `--hidden` | Hide a text Send by default (cannot be used with `--file`) |
| `-n`, `--name <name>` | Send name. Default is the filename or a GUID |
| `--notes <notes>` | Notes |
| `--fullObject` | Return the full Send object (default is the URL only) |

### Subcommands

| Command | Purpose |
| --- | --- |
| `bw send list` | List the Sends I created |
| `bw send template <object>` | `send.text`/`text`/`send.file`/`file` templates |
| `bw send get <id>` | Send object/content. `--text` for the text body, `--output`/`--raw` to save to a file |
| `bw send create [encodedJson]` | Precise creation via JSON. Supports `--file`/`--text`/`--hidden` |
| `bw send edit [encodedJson]` | Edit. Force the target with `--itemid`. Can't change the file of a file Send — delete and recreate |
| `bw send remove-password <id>` | Remove the access password |
| `bw send delete <id>` | Delete a Send |

```bash
bw send "secret"                                     # text
bw send -f ./report.pdf --deleteInDays 3
bw send "code" --password 'opt' --maxAccessCount 1 --hidden
bw send "code" --fullObject                          # full object

bw send template send.text \
  | jq '.text.text="hello" | .deletionDate=null' \
  | bw encode | bw send create

bw send list
bw send get <id> --text
bw send remove-password <id>
bw send delete <id>
```

## receive

```
bw receive <url>
```

| Option | Description |
| --- | --- |
| `--password <pw>` | Send password |
| `--passwordenv <var>` | From an environment variable |
| `--passwordfile <path>` | From a file |
| `--obj` | Return only the Send object (JSON); don't fetch the content |
| `--output <path>` | Where to save a file Send |

```bash
bw receive 'https://vault.example.com/#/send/abc/key'
bw receive '...' --password 'opt'
bw receive '...' --passwordenv SEND_PW --output ./out.pdf
```

---

## generate

```
bw generate [options]
```

| Option | Description |
| --- | --- |
| `-u`, `-l`, `-n`, `-s` | Include uppercase/lowercase/digits/special |
| `-p`, `--passphrase` | Passphrase mode |
| `--length <n>` | Password length (min 5) |
| `--words <n>` | Number of passphrase words (min 3) |
| `--minNumber <n>` | Minimum number of digits |
| `--minSpecial <n>` | Minimum number of special characters |
| `--separator <sep>` | Word separator (`space`/`empty`/character) |
| `-c`, `--capitalize` | Capitalize the first letter of passphrase words |
| `--includeNumber` | Include a number in the passphrase |
| `--ambiguous` | Avoid confusable characters (`O0lI`, etc.) |

Default: `-uln --length 14`.

```bash
bw generate
bw generate -ulns --length 32 --minNumber 4 --minSpecial 4
bw generate -p --words 5 --separator -
bw generate -p --words 6 --separator space --capitalize --includeNumber
```

## encode

```
bw encode
```
stdin → base64. For preparing a payload to pipe into `create`/`edit`/`move`/`send create`.

```bash
echo '{"name":"X"}' | bw encode
```

## serve

```
bw serve [options]
```

| Option | Description |
| --- | --- |
| `--hostname <host>` | Bind host. Default `localhost`. `all` for all interfaces |
| `--port <port>` | Port. Default 8087 |
| `--disable-origin-protection` | Turn off the `Origin` header check (CSRF risk) |

For detailed REST endpoints, see `serve-api.md`.

## update

```
bw update [--raw]
```
Print the download URL for the latest version. With `--raw`, the URL only.

## completion

```
bw completion --shell zsh
```
zsh only. bash/fish are not supported.

```bash
# ~/.zshrc
eval "$(bw completion --shell zsh); compdef _bw bw;"
```

## sdk-version

```
bw sdk-version
```
Print the internal SDK build identifier. For debugging and issue reports.

---

## Exit codes and error output

- Normal success = `0`. Failure = non-0.
- `--cleanexit` always exits 0 "as long as no error is thrown" — for when you want `bw status` and the like to return 0 even when the result is empty.
- Adding `--response` makes stdout a uniform JSON envelope of the form `{"success": bool, "data": ..., "message": ...}`. Handy for automation parsing.
- If you need debug logs, `BITWARDENCLI_DEBUG=true bw ...`.
