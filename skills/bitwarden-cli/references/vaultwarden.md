# VaultWarden ↔ Bitwarden CLI operational notes

VaultWarden is a Bitwarden-compatible self-hosted server (a Rust implementation). Most CLI features work as-is, but there are a few known pitfalls.

## 1. Server configuration order

```bash
bw logout                                       # log out first if logged in to another server
bw config server https://vault.example.com
bw login                                        # or --apikey
```

`bw config server` **cannot be changed while logged in.** Attempting to change it is either silently ignored or fails with an error.

For a reverse-proxy setup that puts a path (e.g., `/bw`) after `vault.example.com`, you must specify per-service URLs rather than a single URL.

```bash
bw config server \
  --web-vault https://example.com/bw \
  --api https://example.com/bw/api \
  --identity https://example.com/bw/identity \
  --icons https://example.com/bw/icons \
  --notifications https://example.com/bw/notifications
```

## 2. Self-signed certificates

Symptom: `request to https://vault.example.com/identity/accounts/prelogin failed, reason: self-signed certificate`.

Recommended fixes (in order):

1. **Apply a proper certificate (e.g., Let's Encrypt)** — the cleanest. It's also the first recommendation in VaultWarden's official guide.
2. **Trust a private CA certificate** — use `NODE_EXTRA_CA_CERTS`.

   ```bash
   export NODE_EXTRA_CA_CERTS="$HOME/.config/bw/vaultwarden-ca.crt"
   bw config server https://vault.example.com
   bw login
   ```

   To make it permanent, add it to `.zshrc`/`.bashrc` or to a systemd unit's `Environment=`.

3. **For temporary debugging only**, `NODE_TLS_REJECT_UNAUTHORIZED=0`. **Forbidden in production** — it turns off all TLS verification.

Even if you add your private CA to the system keychain, `bw` is a Node.js runtime and doesn't use the system CA bundle, so `NODE_EXTRA_CA_CERTS` is required.

## 3. Version compatibility

Because the CLI and VaultWarden evolve at different rates, temporary incompatibilities crop up often when KDF, device approval, or new encryption options are introduced. Known cases:

- **CLI 2025.12.0 + VaultWarden 1.35.2** — `User Decryption Options are required for client initialization` error on `bw login --apikey`. Fixed by downgrading the CLI to `2025.11.0` or updating VaultWarden to the latest.
- **CLI 2024.6.1** — `Invalid master password` false error on `bw unlock`. `2024.6.0` is fine.
- The same pattern repeats whenever a new KDF (Argon2id, etc.) or device approval flow is added.

What to do:

1. First check the latest VaultWarden version (see the `dani-garcia/vaultwarden` release notes). Compatibility patches tend to land quickly.
2. If that still doesn't work, downgrade the CLI by a minor version or two.
   - Homebrew: `brew install bitwarden-cli@<ver>` or download the binary directly.
   - npm: `npm install -g @bitwarden/cli@<ver>`.
3. Pin production automation to a verified version until the issue is resolved.

## 4. Supported / limited features

| Feature | Works on VaultWarden? | Notes |
| --- | --- | --- |
| `login` / `unlock` / `lock` / `logout` | ✅ | Master / API key / SSO all |
| `list`, `get`, `create`, `edit`, `delete`, `restore`, `archive` | ✅ | Full functionality |
| `bw get totp` | ✅ | Only items with a registered TOTP secret |
| `bw send`, `bw receive` | ✅ | VaultWarden 0.21+ |
| `bw export`, `bw import` | ✅ | |
| `bw serve` | ✅ | A local gateway, so independent of the server |
| Organizations, collections, member confirm | ✅ | Core features |
| Key Connector (`--key-connector`) | ❌ | Bitwarden Enterprise only |
| Enterprise SSO + JIT provisioning | Partial | Depends on configuration |
| `device-approval` | ❌ (mostly) | Only on Bitwarden Enterprise + an official CLI build. The Homebrew GPL build lacks the command entirely |

## 5. Homebrew build caveat

`brew install bitwarden-cli` is the GPL build, which omits some enterprise features (notably `device-approval`). It's enough for the personal + VaultWarden scenario, but if you hit a missing command in an organization management flow, switch to the official native binary or `npm install -g @bitwarden/cli`.

## 6. Hands-on verification checklist

When connecting to a new VaultWarden for the first time:

1. Confirm the server is HTTPS and its certificate is trusted (`curl -I https://vault.example.com/alive`).
2. After `bw config server <url>`, recheck with `bw config server` — confirm the URL you entered went in verbatim.
3. Confirm `bw login` → `bw unlock --raw` both succeed in one go.
4. After `bw sync -f`, compare counts with `bw list items | jq length`.
5. For automation, issue an API key and verify re-login with `--apikey`.
6. After `bw lock`, run `bw unlock` again — confirm session rotation is OK.

## 7. Frequently asked scenarios

### "I switched VaultWarden but the CLI keeps connecting to the old server"
`bw status` → check `serverUrl`. If it differs, `bw logout` → `bw config server <new>` → log in again.

### "On WSL/a Linux container the certificate isn't picked up"
Copy the CA file into the container, then `NODE_EXTRA_CA_CERTS=/etc/ssl/vw-ca.crt`. `update-ca-certificates` has no effect on Node.js.

### "API key login works but unlock doesn't"
The API key doesn't replace the master password. You have to provide the master separately with `bw unlock --passwordenv BW_MASTER`.

### "Items disappear when I sync"
Likely sent to trash on another client. Check `bw list items --trash` → restore if needed with `bw restore item <id>`.
