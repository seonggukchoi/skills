---
name: bitwarden-cli
description: Use for any task where the user works with passwords, secrets, notes, attachments, or Send on Bitwarden or a compatible server (VaultWarden, self-hosted Bitwarden) via the CLI. Triggers include requests like "bw login won't work", "how do I use BW_SESSION", "bw config server", "connect to vaultwarden", "bw export", "bw get password", "pull a TOTP from the CLI", "automate the Bitwarden CLI", "bw serve REST", "bulk-extract passwords", "API key login", "self-hosted bitwarden CLI", "password manager script", "vault migration", "share a file via Send" — and even when the user never mentions "bw", "Bitwarden", "vaultwarden", or "password vault" directly, use this skill whenever they intend to pull or modify secrets from a password manager via CLI/script. Covers command options, JSON payloads, self-signed certificate handling, environment variables, and REST API mode all in one place.
---

# Bitwarden CLI Skill

Use the `bw` CLI to securely read, modify, and automate secrets on Bitwarden or VaultWarden (a self-hosted Bitwarden-compatible server). The user's default environment is most likely macOS + zsh + self-hosted VaultWarden, so prioritize that case, but the official Bitwarden cloud (`bitwarden.com`, `bitwarden.eu`) and on-prem Bitwarden work the same way.

Read the detailed references only when needed:

- `references/commands.md` — options and examples for every subcommand
- `references/serve-api.md` — the REST API exposed by `bw serve`
- `references/vaultwarden.md` — VaultWarden-specific gotchas, self-signed certs, version-compatibility issues
- `references/json-templates.md` — `item`, `folder`, and `send` JSON templates plus `jq` automation patterns

---

## First step: check the environment

Before handling the user's request, always run a quick check of these three things. Skip anything you already know.

1. `bw --version` — whether the CLI is installed, and which version.
2. `bw status` — which server you're logged in to and whether the vault is locked or unlocked. Look at the `serverUrl`, `userEmail`, and `status` keys in the JSON response.
3. `bw config server` (with no argument) — the server URL currently in use.

What the `status` values mean:

- `unauthenticated` — login required.
- `locked` — logged in but the master key is locked. `bw unlock` is needed.
- `unlocked` — ready to use. `BW_SESSION` or `--session` may be required.

If it isn't installed, suggest `brew install bitwarden-cli` on macOS. Note, however, that **the Homebrew build is the GPL build, which omits some enterprise SSO / `device-approval` features.** If those features are needed, recommend the official native binary or `npm install -g @bitwarden/cli`.

---

## Server configuration: VaultWarden / on-prem / EU

`bw config server` **cannot be changed while logged in.** To switch to a different server, run `bw logout` first.

```bash
# Self-hosted (including VaultWarden)
bw config server https://vault.example.com

# Official EU cloud
bw config server https://bitwarden.eu

# Official US cloud (default)
bw config server https://bitwarden.com

# Check the current server
bw config server
```

In environments that run separate URLs per service (e.g., API and identity on different hosts), set them all at once.

```bash
bw config server \
  --web-vault https://vault.example.com \
  --api https://vault.example.com/api \
  --identity https://vault.example.com/identity \
  --icons https://vault.example.com/icons \
  --notifications https://vault.example.com/notifications
```

VaultWarden users need extra care. **Always check** `references/vaultwarden.md` **before logging in.** Key points up front:

- **Self-signed certificates**: export `NODE_EXTRA_CA_CERTS=/path/to/ca.crt` and use that. `NODE_TLS_REJECT_UNAUTHORIZED=0` is a security risk and not recommended.
- **Version compatibility**: a too-new `bw` sometimes requires KDF/decryption options that conflict with an older VaultWarden. If you get an error like `User Decryption Options are required` during login, downgrade the CLI by a minor version or two, or upgrade VaultWarden.
- VaultWarden is compatible with most features such as `bw serve`, `bw send`, and `bw get totp`, but some enterprise / Key Connector features don't work.

---

## Three authentication methods

### A. Master password (interactive, for humans)

```bash
bw login                                  # prompts for email / password / 2FA
bw login johndoe@example.com 'secret' --raw  # non-interactive, prints only the session key
```

`--method` is the 2FA method: `0` Authenticator, `1` Email, `3` Yubikey, `4` U2F, `5` Duo. You can pass the code inline with `--code`.

### B. API key (automation, recommended)

Issue `client_id`/`client_secret` from the web vault → Account Settings → Security → Keys. **Even after logging in, you still unlock with the master password** — the API key does not replace the master password.

```bash
export BW_CLIENTID='user.xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
export BW_CLIENTSECRET='xxxxxxxxxxxxxxxxxxxxxxxxxx'
bw login --apikey
# Then unlock with the master password
export BW_SESSION="$(bw unlock --raw)"
```

### C. SSO (organizations)

```bash
bw login --sso                  # default identifier
bw login --sso my-org-identifier
```

---

## Session management

`bw unlock` unlocks the vault in memory and returns a session key. Without this key you can't access the vault.

```bash
# Recommended: grab just the key with --raw into an environment variable
export BW_SESSION="$(bw unlock --raw)"

# Non-interactive
export BW_SESSION="$(bw unlock --passwordenv BW_MASTER --raw)"
bw unlock --passwordfile ~/.config/bw-master --raw
```

After this, every command uses `$BW_SESSION` automatically. You can also specify it per command with `--session <key>`.

Ending a session:

- `bw lock` — invalidates the session key. Stays logged in.
- `bw logout` — logs out completely.

Each call to `bw unlock` issues a new session key and **immediately invalidates the previous one.** Note that running it multiple times in the same shell kills the earlier environment variable.

---

## Data model

| Object | `bw list` / `bw get` name | Notes |
| --- | --- | --- |
| Logins, notes, cards, identities | `items` / `item` | All one "item" kind. Distinguished by the `type` field (1=login, 2=secure note, 3=card, 4=identity) |
| Folder | `folders` / `folder` | For personal categorization |
| Collection | `collections` / `collection` / `org-collections` / `org-collection` | For organization sharing |
| Organization | `organizations` / `organization` | |
| Organization member | `org-members` | Target of `bw confirm` |
| Attachment | `attachment` | Requires `--itemid` |
| Send | `send` | One-time sharing |

---

## Common read patterns

```bash
# Full list (--search is a must if large)
bw list items
bw list items --search github
bw list items --url https://github.com
bw list items --folderid <uuid>
bw list items --folderid null              # items with no folder
bw list items --organizationid notnull     # organization items only
bw list items --trash                      # trash
bw list items --archived                   # archive

# Single item
bw get item <id-or-search>                 # the whole thing as JSON
bw get password github.com                 # password only
bw get username github.com
bw get uri github.com
bw get totp github.com                     # TOTP code (authenticator OTP)
bw get notes github.com
bw get exposed yahoo.com                   # HIBP exposure count

# Attachments
bw get attachment cert.pem --itemid <id> --output ./cert.pem
bw get attachment cert.pem --itemid <id> --raw > ./cert.pem

# Folders / collections / organizations
bw list folders --search 'dev'
bw list org-collections --organizationid <org-id>
bw list org-members --organizationid <org-id>
```

Combining search + filter is AND; filters with each other are OR.

---

## Create, edit, delete (JSON workflow)

`create`/`edit` take **base64-encoded JSON**. The pattern:

```bash
# 1) Get a template
bw get template folder
bw get template item
bw get template item.login
bw get template item.field

# 2) Transform with jq → 3) bw encode → 4) create/edit
bw get template folder \
  | jq '.name="DevOps"' \
  | bw encode \
  | bw create folder

bw get template item \
  | jq '.name="Postgres prod"
       | .notes="rotate quarterly"
       | .login.username="admin"
       | .login.password=$pw
       | .login.uris=[{"match":null,"uri":"postgres://db.example.com"}]' \
       --arg pw "$(bw generate -ulns --length 32)" \
  | bw encode \
  | bw create item

# Edit: patch the existing object with jq
bw get item <id> \
  | jq '.login.password=$pw' --arg pw "new-secret" \
  | bw encode \
  | bw edit item <id>

# Add an attachment
bw create attachment --file ./id_ed25519 --itemid <id>

# Delete (to trash)
bw delete item <id>
# Permanent delete
bw delete item <id> --permanent
# Restore from trash/archive
bw restore item <id>
# Move to archive
bw archive item <id>
```

For the full JSON schema and more `jq` patterns, see `references/json-templates.md`.

---

## Sync

The `bw` CLI operates on a cached copy of the vault. If items added or changed on another client aren't showing up, sync first.

```bash
bw sync          # normal sync
bw sync -f       # forced full sync
bw sync --last   # last sync timestamp only
```

---

## Organizations: move and confirm

```bash
# Move a personal item → organization (pass the collection array along)
echo '["<collection-id>"]' | bw encode \
  | bw move <item-id> <org-id>

# Confirm a new member (admin)
bw confirm org-member <member-id> --organizationid <org-id>
```

`bw share` is deprecated. Use `bw move`.

---

## Generate (passwords / passphrases)

```bash
bw generate                                # default: -uln --length 14
bw generate -ulns --length 24              # upper/lower/digits/special + 24 chars
bw generate -ulns --length 32 --minNumber 4 --minSpecial 4 --ambiguous
bw generate -p --words 5 --separator -     # 5-word passphrase
bw generate -p --words 6 --separator space --capitalize --includeNumber
```

Flags:
- `-u/-l/-n/-s` character sets, `-p` passphrase mode
- `--length` (min 5), `--words` (min 3), `--separator`, `--minNumber`, `--minSpecial`
- `-c/--capitalize`, `--includeNumber`, `--ambiguous` (exclude confusable characters)

---

## Send (one-time sharing)

```bash
# Quick text Send
bw send "secret message"
echo "secret message" | bw send

# File Send
bw send -f ./report.pdf

# Options
bw send "..." \
  --deleteInDays 3 \
  --maxAccessCount 5 \
  --password 'opt' \
  --emails 'a@x.com,b@x.com' \
  --name 'Q2 report' \
  --notes 'NDA only' \
  --hidden \
  --fullObject              # return the full object (default is the access URL only)

# Manage Sends
bw send list
bw send get <id>
bw send get <id> --text                   # text Send body
bw send template send.text
bw send remove-password <id>
bw send delete <id>

# Receive
bw receive https://vault.example.com/#/send/<token>/<key>
bw receive <url> --passwordenv SEND_PW --output ./out.pdf
```

---

## Import / Export

```bash
# Show supported formats
bw import --formats

# Import
bw import bitwardenjson ./vault.json
bw import lastpasscsv ./lp.csv
bw import --organizationid <org-id> bitwardencsv ./shared.csv

# Export
bw export                                                # CSV (default)
bw export --format json --output ./bw.json
bw export --format encrypted_json --password 'wrap-pw' --output ./bw.enc.json
bw export --organizationid <org-id> --format zip --output ./org.zip
bw --raw export                                          # to stdout
```

Export output is plaintext, so encrypt, transfer, and delete it immediately. `encrypted_json` is wrapped with a separate password rather than the account key.

---

## `bw serve` — local REST API

For long-running automation scripts or calls from other processes, stand up a local HTTP gateway instead of spawning a `bw` process every time.

```bash
bw serve                              # localhost:8087
bw serve --hostname 127.0.0.1 --port 8087
bw serve --hostname all --port 8087   # bind externally (usually not recommended)
```

By default, requests carrying an `Origin` header are blocked as CSRF protection. You can lift this with `--disable-origin-protection`, but that's not recommended for security reasons.

**Key concept**: this server is not a cloud auth gateway — it *exposes an already-unlocked local CLI session over HTTP.* It operates directly on the vault unlocked in memory. `bw unlock` is required before starting it, and shut it down when you're done.

The endpoint table and payload examples are collected in `references/serve-api.md`.

---

## Environment variables (the common ones)

| Variable | Purpose |
| --- | --- |
| `BW_SESSION` | The session key returned after unlock. Export it in your shell to use automatically on every command. |
| `BW_CLIENTID` / `BW_CLIENTSECRET` | API key login. Read by `bw login --apikey`. |
| `BITWARDENCLI_APPDATA_DIR` | The config/cache/data directory. Use it to separate multiple accounts. Default on macOS is `~/Library/Application Support/Bitwarden CLI`. |
| `BITWARDENCLI_DEBUG` | When `true`, prints debug logs. For troubleshooting. |
| `NODE_EXTRA_CA_CERTS` | Path to a self-signed CA certificate. Often required for self-signed VaultWarden. |
| `NODE_TLS_REJECT_UNAUTHORIZED` | When `0`, skips TLS verification. **Do not use outside temporary debugging.** |

---

## Multiple accounts / context separation

To use a work vault and a personal vault at the same time, separate the data directories with `BITWARDENCLI_APPDATA_DIR`. Example shell functions for a second vault:

```bash
# ~/.zshrc
bw-work() {
  BITWARDENCLI_APPDATA_DIR="$HOME/.config/bw-work" bw "$@"
}
bw-personal() {
  BITWARDENCLI_APPDATA_DIR="$HOME/.config/bw-personal" bw "$@"
}
```

Each function goes through `login → unlock` separately, and you must manage the session keys separately too.

---

## Common automation patterns

### 1. Unlock helper

```bash
# ~/.zshrc
bw-unlock() {
  if [[ -z "${BW_SESSION:-}" || "$(bw status | jq -r .status)" == "locked" ]]; then
    export BW_SESSION="$(bw unlock --raw)"
  fi
}
```

### 2. Inject secrets in CI/CD (API key + master password)

```bash
export BW_CLIENTID="$BW_CLIENTID"
export BW_CLIENTSECRET="$BW_CLIENTSECRET"
bw config server "$BW_SERVER" >/dev/null
bw login --apikey --quiet
export BW_SESSION="$(BW_MASTER='...' bw unlock --passwordenv BW_MASTER --raw)"
DB_PW="$(bw get password 'prod/postgres')"
trap 'bw lock --quiet' EXIT
```

### 3. One-way JSON pipe

```bash
bw list items --search 'aws' \
  | jq -r '.[] | select(.login) | "\(.name)\t\(.login.username)"'
```

### 4. Backup

```bash
bw sync -f
bw export --format encrypted_json --password "$BACKUP_PASS" \
  --output "$HOME/backups/bw-$(date +%F).enc.json"
```

---

## Global options (common to all commands)

| Flag | Effect |
| --- | --- |
| `--pretty` | Indent JSON |
| `--raw` | Output only the raw value instead of a human message (for scripts) |
| `--response` | Wrap the response in a consistent JSON envelope (`success`, `data`, `message`) |
| `--cleanexit` | Always exit 0 when there's no error |
| `--quiet` | Suppress stdout |
| `--nointeraction` | Disable prompts. Required for automation. |
| `--session <key>` | Pass the session key as an argument instead of via the environment variable |

---

## Troubleshooting quick table

| Symptom | Likely cause / fix |
| --- | --- |
| `You are not logged in.` | `bw login` or `--apikey`. If you just switched servers, `bw logout` → reconfigure `bw config server`. |
| `Vault is locked.` | `export BW_SESSION="$(bw unlock --raw)"`. |
| `Session key is invalid.` | Run `bw unlock` again for a new key. The old key is invalidated automatically. |
| `self-signed certificate` | Add the CA to `NODE_EXTRA_CA_CERTS`. Or use a proper certificate (Let's Encrypt). |
| `User Decryption Options are required` | The CLI version is too new relative to VaultWarden. Update VaultWarden or downgrade the CLI (one minor back). |
| `bw config server` ignored | Tried to change it without logging out. `bw logout` and retry. |
| `device-approval` command missing | Homebrew GPL build. Use the official binary / npm install. |
| Data not showing up | `bw sync -f`. If it was just added on another client, it may be a server propagation delay. |
| `bw serve` refuses external calls | Default `localhost` binding + `Origin` blocking. Use `--hostname`, and `--disable-origin-protection` if needed. |

---

## Ending a session

**Leave the session unlocked by default.** Locking after every task makes the user re-enter the master password on the next one, and because `bw unlock` invalidates the previous key, any `BW_SESSION` they already exported stops working too. Run the commands below only when the user asks to lock or sign out, or when the vault was unlocked on a machine that isn't theirs.

```bash
bw lock          # lock the session only (stay signed in)
bw logout        # full logout
```

Automation scripts are the exception: keep `trap 'bw lock --quiet' EXIT` there so a session doesn't linger even on abnormal exit. A CI runner is a throwaway environment, so nobody pays the cost of unlocking again.

---

## Workflow summary (checklist)

1. Check the environment with `bw --version`, `bw status`, `bw config server`.
2. If needed, `bw logout` → `bw config server <url>` to set the server (for VaultWarden, along with `NODE_EXTRA_CA_CERTS`).
3. `bw login` or `bw login --apikey`.
4. `export BW_SESSION="$(bw unlock --raw)"`.
5. Do the actual work (`list`/`get`/`create`/`edit`/`delete`/`send`/`export`/`serve` …).
6. Leave the session as it is. Lock with `bw lock` or sign out with `bw logout` only when the user asks for it.

Refer to the relevant file under `references/` for detailed options, JSON schemas, and the REST API as you go.
