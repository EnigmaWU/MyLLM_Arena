# Solution-chiselOpenSSH deployment runbook

This runbook deploys a nested SSH path:

```text
LapC
  -> SSH to SrvB:22
  -> SrvB loopback 127.0.0.1:22022
  -> Chisel over TLS/WebSocket to DskA
  -> DskA loopback 127.0.0.1:22023
  -> DskA SSH to SrvA:22
  -> SrvA loopback 127.0.0.1:5395
  -> container sshd:5395
  -> LapC's end-to-end SSH authentication
```

## Roles and trust boundaries

| Role | Responsibility |
|---|---|
| **AdmX** | Sole key-generation and key-custody authority. Generates all solution-managed keys, records public fingerprints, retains the complete master inventory for testing/verification, and securely delivers only the minimum material required by each participant. |
| **DskA** | Internal bridge. Holds its own DskA-to-SrvA private key and public trust information. It does not hold LapC's private keys. |
| **LapC** | User SSH client. Holds only the `lapc_srvb_auth` and `lapc_container_auth` private keys. |
| **SrvB** | Public relay. Holds `lapc_srvb_auth.pub`, its TLS private key/certificate, and its Chisel server identity. It knows no SrvA address or credential. |
| **SrvA** | Accepts DskA's existing normal SSH account and forwards only to `127.0.0.1:5395`. It receives no LapC authentication key. |
| **Container** | Holds only the container host key pair and `lapc_container_auth.pub`. It authenticates LapC's inner SSH connection. |

AdmX is a role, not necessarily a machine. It may be an offline provisioning
workstation, a vault-backed administrative service, or a dedicated account on
DskA. AdmX's ability to hold every private key means AdmX can impersonate every
participant for testing. That is an intentional central-administrative
capability.

### Key delivery matrix

| Key or credential | AdmX vault | Runtime recipient |
|---|---|---|
| `lapc_srvb_auth` / `.pub` | Complete pair | Private key to LapC; public key to SrvB |
| `lapc_container_auth` / `.pub` | Complete pair | Private key to LapC; public key to container |
| DskA-to-SrvA key pair | Private/public master copy if custody is authorized | Private key on DskA; public key authorized on SrvA |
| Container host key pair | Complete pair | Private and public files in the container host-key volume |
| Chisel server identity | Complete private key and fingerprint | Private key on SrvB; fingerprint on DskA |
| SrvB TLS private key and certificate | Protected key and certificate inventory | Key/certificate on SrvB; certificate trust on DskA |
| SrvA/SrvB SSH host keys | Public fingerprints must be inventoried | Existing private keys remain managed by their server administrators unless separately delegated |

The final row is an administrative limit, not a design choice: without SrvA
`sshd` or host-root access, AdmX cannot take custody of SrvA's existing host
private key or rotate it. If “all keys” must include that host key, the SrvA
administrator must explicitly delegate that authority.

Every private key is delivered only to its intended runtime holder and retained
in AdmX's vault. DskA receives no LapC private key. SrvA receives no LapC
authentication key.

## Hard network restrictions

| From | To | Permitted transport |
|---|---|---|
| LapC | SrvB:22 | SSH |
| DskA | SrvB:443 | HTTPS and Chisel WebSocket-over-TLS only |
| DskA | SrvA:22 | Internal SSH using the existing normal account |
| SrvB | DskA | No inbound connection; traffic travels only inside DskA's outbound WSS connection |

DskA must never use SSH, SCP, SFTP, plain HTTP, or raw TCP to SrvB. Chisel's
“reverse” endpoint is multiplexed inside DskA's outbound HTTPS connection;
SrvB does not initiate a network connection to DskA.

SrvB has no SrvA address, route, credential, or inner-SSH decryption ability.
LapC has no SrvA or DskA address.

## Required environment

- SrvA already runs `sshd` on TCP `22`.
- DskA can SSH to SrvA using a normal account and an existing private key.
- The DskA normal account must already permit local TCP forwarding to
  `127.0.0.1:5395`. Step 9 tests this.
- The user does not need SrvA `sshd` administrator access unless the test in
  Step 9 fails.
- SrvA has an existing Docker image with `/usr/sbin/sshd`, `ssh-keygen`, and a
  usable non-root account.
- SrvB is Ubuntu with root access.
- SrvB has a currently valid TLS certificate for its public IPv4 address.
- The organization permits this SSH-over-WebSocket projection.
- AdmX has the approved Chisel binary when generating `chisel_server.key`.

If DskA's existing account cannot forward to the container, the deployment
stops. A SrvA administrator must approve a restricted forwarding policy; the
runbook must not be changed to bypass that policy.

## Deployment values

Replace every placeholder consistently:

| Placeholder | Meaning |
|---|---|
| `<SrvB-public-IPv4>` | SrvB public IPv4 |
| `<SrvA-internal-IP>` | SrvA address reachable from DskA |
| `<DskA-account-on-SrvA>` | Existing normal DskA account on SrvA |
| `<DskA-to-SrvA-private-key>` | Existing DskA private key for that account |
| `<LapC-source-IP>` | Routed/NAT source observed by SrvB |
| `<SrvA-container-name>` | Existing Docker container name |
| `container-user` | Existing non-root account in the container |
| `22023` | Loopback-only outer SSH bridge port on DskA |

LapC needs only SrvB's public IPv4 as an external address. Its final alias uses
`127.0.0.1:22022`, which is resolved by SrvB.

## Sensitive-file policy

| File/value | Secret? | Retention and rotation |
|---|---|---|
| `lapc_srvb_auth` | **Yes** | AdmX master vault plus LapC runtime copy. Rotate if exposed or for policy. |
| `lapc_container_auth` | **Yes** | AdmX master vault plus LapC runtime copy. Rotate if exposed or for policy. |
| DskA-to-SrvA private key | **Yes** | DskA runtime copy plus AdmX vault only if authorized. |
| `container_ssh_host_key` | **Yes** | Container host-key volume plus AdmX vault. Preserve across restarts. |
| `chisel_server.key` | **Yes** | SrvB plus AdmX vault. Preserve across restarts. |
| SrvB TLS private key | **Yes** | SrvB plus AdmX vault. Replace with certificate renewal. |
| `users.json` | **Yes** | Contains the tunnel password. Shape `600`; rotate on exposure. |
| Tunnel password | **Yes** | Credential manager and runtime only. Never place in repository or shell history. |
| `$AUTH` / `$env:AUTH` | **Yes** | Runtime only; unset after client exit. |
| Public keys/fingerprints/certificates | No | Record and distribute only to validators. |
| `authorized_keys` | No, access-control sensitive | Keep mode `600`; replace only as part of approved key rotation. |
| `known_hosts` | No, security-sensitive | Update only after independent fingerprint verification. |

Container SSH configuration and authorized keys are in the container's writable
layer. They survive stop/start but must be reapplied after container deletion
and recreation. The container host-key volume persists.

## Step 1: Freeze values and verify prerequisites

On DskA, verify the existing SrvA path and key without printing the key:

```bash
ssh -G "<DskA-account-on-SrvA>"@"<SrvA-internal-IP>" |
  grep -E '^(hostname|user|port|identityfile) '
nc -vz "<SrvA-internal-IP>" 22
```

Expected: port `22`, the normal account, and the existing identity file are
shown; TCP port `22` is reachable.

On SrvB:

```bash
sudo ss -ltn 'sport = :443'
sudo ss -ltn 'sport = :22'
```

Expected: `443` has no `LISTEN` row; `22` has a listener for the existing SSH
daemon.

On SrvA:

```bash
CONTAINER="<SrvA-container-name>"
CONTAINER_USER="container-user"
docker version --format '{{.Server.Version}}'
docker ps --filter "name=^/${CONTAINER}$"
docker exec "$CONTAINER" id "$CONTAINER_USER"
```

Expected: Docker is accessible, Engine is `28` or newer, the container exists,
and the target account is non-root.

Keep an administrative terminal open on SrvB while changing its SSH
configuration.

**Secret/config handling:** Do not print private keys or tunnel passwords.

## Step 2: Back up the existing container definition

On SrvA:

```bash
CONTAINER="<SrvA-container-name>"
sudo install -d -m 700 /root/chisel-openssh-deploy-backup
sudo sh -c \
  'umask 077; docker inspect "$1" > /root/chisel-openssh-deploy-backup/container.before.json' \
  sh "$CONTAINER"
sudo chmod 600 /root/chisel-openssh-deploy-backup/container.before.json
```

Record the existing image, entrypoint, command, environment sources, networks,
mounts, restart policy, and original `docker run` arguments.

Verification:

```bash
sudo test -s /root/chisel-openssh-deploy-backup/container.before.json
docker inspect --format 'image={{.Config.Image}}' "$CONTAINER"
```

Expected: the backup exists and identifies the intended image.

**Secret/config handling:** The JSON backup can contain secrets. Keep it
root-only and never paste it into chat.

## Step 3: AdmX generates the complete managed key inventory

On AdmX, create a protected working directory:

```bash
umask 077
ADMX_STAGING="$HOME/admx-key-staging"
ADMX_VAULT="$HOME/admx-key-vault"
install -d -m 700 "$ADMX_STAGING" "$ADMX_VAULT"
```

Generate LapC's two authentication pairs:

```bash
for key in lapc_srvb_auth lapc_container_auth; do
  if [ -e "$ADMX_STAGING/$key" ]; then
    echo "Refusing to overwrite existing key: $key" >&2
  else
    ssh-keygen -t ed25519 -a 100 -N "" \
      -f "$ADMX_STAGING/$key" \
      -C "$key-issued-by-admx"
  fi
done
```

Generate the container host identity:

```bash
if [ ! -e "$ADMX_STAGING/container_ssh_host_key" ]; then
  ssh-keygen -t ed25519 -N "" \
    -f "$ADMX_STAGING/container_ssh_host_key" \
    -C container-ssh-host-issued-by-admx
fi
```

Generate the Chisel server identity using the approved Chisel binary on AdmX:

```bash
chisel server --keygen "$ADMX_STAGING/chisel_server.key"
```

Record public identities:

```bash
ssh-keygen -lf "$ADMX_STAGING/lapc_srvb_auth.pub"
ssh-keygen -lf "$ADMX_STAGING/lapc_container_auth.pub"
ssh-keygen -lf "$ADMX_STAGING/container_ssh_host_key.pub"
ssh-keygen -lf "$ADMX_STAGING/chisel_server.key.pub" 2>/dev/null ||
  echo "Record the full Chisel fingerprint from server startup."
```

Place the existing SrvB TLS private key and certificate chain in the AdmX vault
under `srvb_tls.key` and `srvb_tls.crt`. Receive an encrypted copy of DskA's
existing SrvA private key through the approved administrative channel and store
it in the vault as `dska_to_srva_auth`. If exporting that key is forbidden by policy,
the requirement that AdmX hold all solution-managed keys cannot be satisfied;
record that exception explicitly.

Verification:

```bash
for key in lapc_srvb_auth lapc_container_auth container_ssh_host_key; do
  ssh-keygen -y -f "$ADMX_STAGING/$key" >/dev/null
done
test -s "$ADMX_STAGING/chisel_server.key"
test -s "$ADMX_VAULT/srvb_tls.key"
test -s "$ADMX_VAULT/srvb_tls.crt"
```

Expected: every command exits successfully. Do not overwrite an existing key;
rotate deliberately.

Copy the protected master material into the vault:

```bash
for file in lapc_srvb_auth lapc_container_auth container_ssh_host_key \
  chisel_server.key; do
  install -m 600 "$ADMX_STAGING/$file" "$ADMX_VAULT/$file"
done
for file in lapc_srvb_auth.pub lapc_container_auth.pub container_ssh_host_key.pub; do
  install -m 644 "$ADMX_STAGING/$file" "$ADMX_VAULT/$file"
done
```

Set AdmX-owned passphrases on the three private user/host keys:

```bash
ssh-keygen -p -f "$ADMX_VAULT/lapc_srvb_auth"
ssh-keygen -p -f "$ADMX_VAULT/lapc_container_auth"
ssh-keygen -p -f "$ADMX_VAULT/container_ssh_host_key"
```

**Secret/config handling:** AdmX keeps all master private keys in the vault.
Other hosts receive only their required subset. SrvA/SrvB host private keys
remain outside AdmX custody unless their administrators explicitly delegate
them.

## Step 4: AdmX securely delivers runtime key material

Use approved encrypted channels. Deliver these subsets:

```text
To LapC:
  lapc_srvb_auth
  lapc_srvb_auth.pub
  lapc_container_auth
  lapc_container_auth.pub

To DskA:
  existing DskA-to-SrvA private key, if rotated by AdmX
  container_ssh_host_key.pub
  SrvB TLS certificate/fingerprint
  Chisel server fingerprint

To SrvA staging:
  container_ssh_host_key
  container_ssh_host_key.pub
  lapc_container_auth.pub

To SrvB:
  lapc_srvb_auth.pub
  chisel_server.key
  SrvB TLS private key and certificate chain

To the container:
  container_ssh_host_key private/public pair
  lapc_container_auth.pub
```

DskA must receive no LapC private key. SrvA must receive no LapC private key.

On LapC, install and protect its files:

```bash
install -d -m 700 "$HOME/.ssh"
for key in lapc_srvb_auth lapc_container_auth; do
  install -m 600 "/path/to/delivered/$key" "$HOME/.ssh/$key"
  install -m 644 "/path/to/delivered/$key.pub" "$HOME/.ssh/$key.pub"
done
```

LapC may set recipient-owned passphrases:

```bash
ssh-keygen -p -f "$HOME/.ssh/lapc_srvb_auth"
ssh-keygen -p -f "$HOME/.ssh/lapc_container_auth"
```

On SrvB, create a root-only staging directory for the jump key:

```bash
sudo install -d -m 700 /root/chisel-openssh-deploy-incoming
```

If AdmX cannot directly upload to SrvB, LapC may transport the public jump key:

```bash
scp "$HOME/.ssh/lapc_srvb_auth.pub" \
  root@"<SrvB-public-IPv4>":/root/chisel-openssh-deploy-incoming/lapc_srvb_auth.pub
```

On SrvB:

```bash
ssh-keygen -lf /root/chisel-openssh-deploy-incoming/lapc_srvb_auth.pub
```

On SrvA, create a staging directory for container material. If using the normal
account:

```bash
install -d -m 700 "$HOME/chisel-openssh-deploy-incoming"
ssh-keygen -lf "$HOME/chisel-openssh-deploy-incoming/lapc_container_auth.pub"
ssh-keygen -lf "$HOME/chisel-openssh-deploy-incoming/container_ssh_host_key.pub"
```

Verification:

- Every public fingerprint matches AdmX's inventory.
- LapC private keys are mode `600`.
- DskA has no copies named `lapc_srvb_auth` or `lapc_container_auth`.
- SrvA receives no private LapC key.

**Secret/config handling:** Public keys may be transported by any approved
channel. Private keys travel only through approved encrypted channels and only
to their runtime recipient. AdmX retains the master copies.

## Step 5: Start the existing image with loopback publishing

On SrvA:

```bash
CONTAINER="<SrvA-container-name>"
CONTAINER_USER="container-user"
IMAGE="$(docker inspect --format '{{.Config.Image}}' "$CONTAINER")"
docker version --format '{{.Server.Version}}'
printf 'IMAGE=%s\n' "$IMAGE"
```

If the container already has the required binding and volume:

```bash
docker port "$CONTAINER" 5395/tcp
docker inspect --format \
  '{{range .Mounts}}{{if eq .Destination "/etc/ssh/container_ssh_hostkeys"}}{{println .Type .Name}}{{end}}{{end}}' \
  "$CONTAINER"
```

Expected: `127.0.0.1:5395` and the intended host-key volume. Skip recreation.

If recreation is required, preserve the original container configuration:

```bash
docker stop "$CONTAINER" 2>/dev/null || true
docker rm "$CONTAINER" 2>/dev/null || true

docker run -d \
  --name "$CONTAINER" \
  --publish 127.0.0.1:5395:5395/tcp \
  --mount type=volume,source=container_ssh_hostkeys,target=/etc/ssh/container_ssh_hostkeys \
  "$IMAGE"
```

Restore the original network, environment, application mounts, workdir,
entrypoint override, command arguments, and restart policy. Do not use Compose
or build a new image for this solution.

Verification:

```bash
docker inspect --format '{{json .HostConfig.PortBindings}}' "$CONTAINER"
docker port "$CONTAINER" 5395/tcp
docker ps --filter "name=^/${CONTAINER}$"
```

Expected: the host IP is `127.0.0.1`, not `0.0.0.0` or `::`, and the
application is running.

**Secret/config handling:** Preserve existing environment/application secrets.
The container host-key volume is protected persistent state.

## Step 6: Install the AdmX host key and configure container SSH

On SrvA, set:

```bash
CONTAINER="<SrvA-container-name>"
CONTAINER_USER="container-user"
STAGE="$HOME/chisel-openssh-deploy-incoming"
```

Create `$STAGE/sshd_config_5395`:

```text
Port 5395
ListenAddress 0.0.0.0
HostKey /etc/ssh/container_ssh_hostkeys/ssh_host_ed25519_key
PidFile /run/sshd_container_5395.pid
PubkeyAuthentication yes
AuthorizedKeysFile /etc/ssh/container_authorized_keys/%u
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
UsePAM yes
AllowUsers container-user
```

Copy all AdmX-generated container material into the container:

```bash
docker cp "$STAGE/sshd_config_5395" \
  "$CONTAINER:/etc/ssh/sshd_config_5395"
docker cp "$STAGE/container_ssh_host_key" \
  "$CONTAINER:/tmp/container_ssh_host_key"
docker cp "$STAGE/container_ssh_host_key.pub" \
  "$CONTAINER:/tmp/container_ssh_host_key.pub"
docker cp "$STAGE/lapc_container_auth.pub" \
  "$CONTAINER:/tmp/lapc_container_auth.pub"

docker exec --user 0 "$CONTAINER" sh -ec '
  set -eu
  mkdir -p /run/sshd /etc/ssh/container_ssh_hostkeys /etc/ssh/container_authorized_keys
  chmod 700 /etc/ssh/container_ssh_hostkeys
  chmod 755 /run/sshd /etc/ssh/container_authorized_keys
  install -m 600 /tmp/container_ssh_host_key \
    /etc/ssh/container_ssh_hostkeys/ssh_host_ed25519_key
  install -m 644 /tmp/container_ssh_host_key.pub \
    /etc/ssh/container_ssh_hostkeys/ssh_host_ed25519_key.pub
  authorized_keys_file=/etc/ssh/container_authorized_keys/container-user
  authorized_public_key="$(cat /tmp/lapc_container_auth.pub)"
  if [ -s "$authorized_keys_file" ]; then
    cp -p "$authorized_keys_file" "${authorized_keys_file}.before-deployment"
    chmod 600 "${authorized_keys_file}.before-deployment"
  fi
  printf "%s\n" "$authorized_public_key" > "$authorized_keys_file"
  chown root:root /etc/ssh/sshd_config_5395 \
    /etc/ssh/container_authorized_keys "$authorized_keys_file"
  chmod 644 /etc/ssh/sshd_config_5395
  chmod 600 "$authorized_keys_file"
  rm -f /tmp/container_ssh_host_key /tmp/container_ssh_host_key.pub \
    /tmp/lapc_container_auth.pub
'
```

If the image does not support PAM, preserve its known-working PAM/account
settings instead of assuming `UsePAM yes`.

Validate and start:

```bash
docker exec --user 0 "$CONTAINER" \
  /usr/sbin/sshd -t -f /etc/ssh/sshd_config_5395
```

In a dedicated terminal:

```bash
docker exec --user 0 -it "$CONTAINER" \
  /usr/sbin/sshd -D -e -f /etc/ssh/sshd_config_5395
```

From another SrvA terminal:

```bash
docker port "$CONTAINER" 5395/tcp
ssh-keyscan -T 5 -p 5395 127.0.0.1 2>/dev/null | ssh-keygen -lf -
docker exec "$CONTAINER" \
  ssh-keygen -lf /etc/ssh/container_ssh_hostkeys/ssh_host_ed25519_key.pub
docker exec "$CONTAINER" sh -c \
  'wc -l < /etc/ssh/container_authorized_keys/container-user'
```

Expected:

- Host mapping is exactly `127.0.0.1:5395`.
- Scanned and stored host-key fingerprints match AdmX's inventory.
- Authorized-key line count is exactly `1`.
- Passwords and keyboard-interactive authentication are disabled.

**Secret/config handling:** AdmX's host-key vault copy is the recovery source.
The container receives only the delivered host key pair and
`lapc_container_auth.pub`. The old authorized-key file remains as
`container-user.before-deployment` but is not read by this SSH configuration.

## Step 7: Configure SrvB's jump account

On SrvB:

```bash
sudo install -d -m 700 /root/chisel-openssh-deploy-incoming
id srvb-jump >/dev/null 2>&1 ||
  sudo adduser --disabled-password --gecos "" srvb-jump
sudo install -d -m 700 -o srvb-jump -g srvb-jump \
  /home/srvb-jump/.ssh
authorized_public_key="$(
  sudo cat /root/chisel-openssh-deploy-incoming/lapc_srvb_auth.pub
)"
if ! sudo test -f /home/srvb-jump/.ssh/authorized_keys; then
  sudo install -m 600 -o srvb-jump -g srvb-jump \
    /dev/null /home/srvb-jump/.ssh/authorized_keys
fi
if ! sudo grep -qxF "$authorized_public_key" /home/srvb-jump/.ssh/authorized_keys; then
  printf '%s\n' "$authorized_public_key" |
    sudo tee -a /home/srvb-jump/.ssh/authorized_keys >/dev/null
fi
sudo chown srvb-jump:srvb-jump \
  /home/srvb-jump/.ssh/authorized_keys
sudo chmod 600 /home/srvb-jump/.ssh/authorized_keys
```

Create `/etc/ssh/sshd_config.d/srvb-jump.conf`:

```text
Match User srvb-jump
    PubkeyAuthentication yes
    AuthenticationMethods publickey
    PasswordAuthentication no
    KbdInteractiveAuthentication no
    AllowTcpForwarding local
    PermitOpen 127.0.0.1:22022
    PermitListen none
    AllowStreamLocalForwarding no
    AllowAgentForwarding no
    X11Forwarding no
    PermitTTY no
    MaxSessions 0
Match all
```

This does not conflict with the administrator's existing SSH access on port
`22`. One `sshd` can accept many sessions; this policy applies only to
`srvb-jump`.

Validate:

```bash
sudo chown root:root /etc/ssh/sshd_config.d/srvb-jump.conf
sudo chmod 644 /etc/ssh/sshd_config.d/srvb-jump.conf
sudo /usr/sbin/sshd -t
sudo /usr/sbin/sshd -T \
  -C user=srvb-jump,host=lapc,addr="<LapC-source-IP>" |
  grep -E '^(allowtcpforwarding|permitopen|permitlisten|maxsessions|permittty|passwordauthentication) '
```

Expected: local forwarding, `PermitOpen 127.0.0.1:22022`, no listener
forwarding, no TTY, `MaxSessions 0`, and no password authentication.

Keep the existing administrator session open, then reload:

```bash
sudo systemctl reload ssh
sudo systemctl is-active ssh
```

**Secret/config handling:** `authorized_keys` is access-control data. The
private `lapc_srvb_auth` key remains only on LapC and in AdmX's vault.

## Step 8: Install matching Chisel releases

On SrvB and DskA, verify:

```bash
command -v chisel
chisel --version
```

Current official stable version referenced here: `1.12.0`.

Install on SrvB if missing:

```bash
(
set -euo pipefail
CHISEL_VERSION="1.12.0"
CHISEL_ASSET="chisel_${CHISEL_VERSION}_linux_amd64.gz"
CHISEL_SHA256="f3f180f1d93aa72cce4e6386f98cc06569a0146fbd65eb4423cf83e6434bcfe6"
DOWNLOAD_DIR="$(mktemp -d)"
cd "$DOWNLOAD_DIR"
curl --fail --location --proto '=https' --tlsv1.2 \
  --output "$CHISEL_ASSET" \
  "https://github.com/jpillora/chisel/releases/download/v${CHISEL_VERSION}/${CHISEL_ASSET}"
printf '%s  %s\n' "$CHISEL_SHA256" "$CHISEL_ASSET" | sha256sum --check -
gzip -t "$CHISEL_ASSET"
gzip -dc "$CHISEL_ASSET" > chisel
sudo install -o root -g root -m 0755 chisel /usr/local/bin/chisel
rm -f -- chisel "$CHISEL_ASSET"
rmdir -- "$DOWNLOAD_DIR"
)
```

Install on macOS DskA:

```bash
(
set -euo pipefail
CHISEL_VERSION="1.12.0"
case "$(uname -m)" in
  arm64)
    CHISEL_ASSET="chisel_${CHISEL_VERSION}_darwin_arm64.gz"
    CHISEL_SHA256="707a4b932eea214765146504a0df246cefc415b4297af65a80dd67cf69ba85a9"
    ;;
  x86_64)
    CHISEL_ASSET="chisel_${CHISEL_VERSION}_darwin_amd64.gz"
    CHISEL_SHA256="4aeae36c867f11c8e8c3f2b913a0e063ea3c6d29e1c14a52ed2e6eef8cfc4395"
    ;;
  *) exit 2 ;;
esac
DOWNLOAD_DIR="$(mktemp -d)"
cd "$DOWNLOAD_DIR"
curl --fail --location --proto '=https' --tlsv1.2 \
  --output "$CHISEL_ASSET" \
  "https://github.com/jpillora/chisel/releases/download/v${CHISEL_VERSION}/${CHISEL_ASSET}"
printf '%s  %s\n' "$CHISEL_SHA256" "$CHISEL_ASSET" | shasum -a 256 -c -
gzip -dc "$CHISEL_ASSET" > chisel
sudo install -o root -g wheel -m 0755 chisel /usr/local/bin/chisel
rm -f -- chisel "$CHISEL_ASSET"
rmdir -- "$DOWNLOAD_DIR"
)
```

On Windows DskA, install the approved `1.12.0` artifact:

```powershell
$ChiselVersion = "1.12.0"
$TargetArch = if ($env:PROCESSOR_ARCHITECTURE -eq "ARM64") { "arm64" } else { "amd64" }
$ChiselArchive = "chisel_${ChiselVersion}_windows_${TargetArch}.zip"
$ExpectedSha256 = if ($TargetArch -eq "arm64") {
    "907e1538ab86522fa4b11d7e45192b5f54e74beb88745093f6b2ca5b6e4efbc8"
} else {
    "600a8ad6f03bc7f6d285fd01ab6a3f8a657204adaafa5666ade9451d18df1ebc"
}
$DownloadDirectory = Join-Path $env:TEMP "chisel-$ChiselVersion"
New-Item -ItemType Directory -Force $DownloadDirectory | Out-Null
$ArchivePath = Join-Path $DownloadDirectory $ChiselArchive
curl.exe --fail --location --proto "=https" --tlsv1.2 `
  --output $ArchivePath `
  "https://github.com/jpillora/chisel/releases/download/v${ChiselVersion}/${ChiselArchive}"
$ActualSha256 = (Get-FileHash -Algorithm SHA256 $ArchivePath).Hash.ToLower()
if ($ActualSha256 -ne $ExpectedSha256) { throw "Chisel checksum mismatch" }
$ExtractDirectory = Join-Path $DownloadDirectory "extract"
Expand-Archive -Path $ArchivePath -DestinationPath $ExtractDirectory -Force
$ChiselInstallDirectory = Join-Path $env:LOCALAPPDATA "Programs\chisel"
New-Item -ItemType Directory -Force $ChiselInstallDirectory | Out-Null
Copy-Item (Join-Path $ExtractDirectory "chisel.exe") `
  (Join-Path $ChiselInstallDirectory "chisel.exe") -Force
$env:Path = "$ChiselInstallDirectory;$env:Path"
```

Keep that PowerShell session open for the later commands, or add
`$ChiselInstallDirectory` to the approved user `PATH`.

Verification on both hosts:

```bash
chisel --version
```

Expected: the same approved version on SrvB and DskA.

**Secret/config handling:** Binaries are not secrets. Record the exact version
and archive checksum.

## Step 9: Verify DskA's existing SrvA forwarding permission

This step requires no SrvA `sshd` changes.

On DskA:

```bash
ssh -N \
  -i "<DskA-to-SrvA-private-key>" \
  -o IdentitiesOnly=yes \
  -o BatchMode=yes \
  -o ExitOnForwardFailure=yes \
  -o ServerAliveInterval=30 \
  -o ServerAliveCountMax=3 \
  -L 127.0.0.1:22023:127.0.0.1:5395 \
  "<DskA-account-on-SrvA>"@"<SrvA-internal-IP>"
```

Windows PowerShell equivalent:

```powershell
$SrvAIP = "<SrvA-internal-IP>"
$SrvAUser = "<DskA-account-on-SrvA>"
$DskAToSrvAPrivateKeyPath = Join-Path $HOME `
  ".ssh\<DskA-to-SrvA-private-key>"
ssh.exe -N `
  -i $DskAToSrvAPrivateKeyPath `
  -o IdentitiesOnly=yes `
  -o BatchMode=yes `
  -o ExitOnForwardFailure=yes `
  -o ServerAliveInterval=30 `
  -o ServerAliveCountMax=3 `
  -L "127.0.0.1:22023:127.0.0.1:5395" `
  "$SrvAUser@$SrvAIP"
```

Keep this terminal open. From another DskA terminal:

```bash
ssh-keyscan -T 5 -p 22023 127.0.0.1 2>/dev/null | ssh-keygen -lf -
```

Expected: the container host fingerprint from AdmX's inventory.

If SSH reports `administratively prohibited` or the forward cannot open, stop.
A SrvA administrator must approve local forwarding to `127.0.0.1:5395`, ideally
limited to this normal account. Do not bypass the policy.

**Secret/config handling:** DskA's SrvA private key remains on DskA and in
AdmX's vault if custody is authorized. No LapC key is installed on SrvA.

## Step 10: Start SrvB's TLS and Chisel server

On SrvB:

```bash
sudo install -d -m 700 /etc/chisel-relay
```

Place the AdmX-vault certificate chain and private key at:

```text
/etc/chisel-relay/fullchain.pem
/etc/chisel-relay/privkey.pem
```

Place AdmX's generated Chisel server key at:

```text
/etc/chisel-relay/chisel.key
```

Set permissions and verify the certificate:

```bash
sudo chmod 600 /etc/chisel-relay/privkey.pem \
  /etc/chisel-relay/chisel.key
sudo openssl x509 -in /etc/chisel-relay/fullchain.pem \
  -noout -subject -issuer -dates -ext subjectAltName
sudo test -s /etc/chisel-relay/chisel.key
```

Expected: certificate validity dates are current and SAN includes
`<SrvB-public-IPv4>`.

Create `/etc/chisel-relay/users.json`:

```json
{
  "dska-chisel:REPLACE_WITH_LONG_RANDOM_PASSWORD": [
    "^R:127\\.0\\.0\\.1:22022$"
  ]
}
```

Store the real password in the approved credential manager and deliver it to
DskA. Set and validate:

```bash
sudo chown root:root /etc/chisel-relay/users.json
sudo chmod 600 /etc/chisel-relay/users.json
sudo python3 -m json.tool /etc/chisel-relay/users.json >/dev/null
```

Start the server in a dedicated terminal:

```bash
sudo chisel server \
  --host 0.0.0.0 \
  --port 443 \
  --reverse \
  --authfile /etc/chisel-relay/users.json \
  --keyfile /etc/chisel-relay/chisel.key \
  --tls-cert /etc/chisel-relay/fullchain.pem \
  --tls-key /etc/chisel-relay/privkey.pem
```

From another SrvB terminal:

```bash
sudo ss -ltnp 'sport = :443'
```

Expected: Chisel listens on `443`. Record the full Chisel fingerprint from its
startup output; it is the public identity of AdmX's `chisel_server.key`.

The `users.json` expression restricts the SrvB listener. It does not enforce
DskA's target, so DskA must use only `127.0.0.1:22023`.

**Secret/config handling:** TLS and Chisel private keys and `users.json` are
secret. AdmX retains master copies for test and recovery.

## Step 11: Start DskA's Chisel client

First confirm the Step 9 bridge is still running:

```bash
ssh-keyscan -T 5 -p 22023 127.0.0.1 2>/dev/null | ssh-keygen -lf -
```

Expected: container host fingerprint from AdmX's inventory.

Verify HTTPS only:

```bash
curl --show-error --verbose --output /dev/null \
  "https://<SrvB-public-IPv4>:443/"
```

Do not test or configure DskA-to-SrvB SSH.

On macOS:

```bash
read -r -s -p "Tunnel password: " TUNNEL_PASSWORD
printf '\n'
export AUTH="dska-chisel:${TUNNEL_PASSWORD}"
unset TUNNEL_PASSWORD
chisel client \
  --fingerprint "<FULL_CHISEL_FINGERPRINT>" \
  "https://<SrvB-public-IPv4>:443" \
  "R:127.0.0.1:22022:127.0.0.1:22023"
unset AUTH
```

On Windows PowerShell:

```powershell
$TunnelPassword = Read-Host "Tunnel password" -AsSecureString
$env:AUTH = "dska-chisel:" +
  [System.Net.NetworkCredential]::new("", $TunnelPassword).Password
try {
    & chisel.exe client `
      --fingerprint "<FULL_CHISEL_FINGERPRINT>" `
      "https://<SrvB-public-IPv4>:443" `
      "R:127.0.0.1:22022:127.0.0.1:22023"
} finally {
    Remove-Item Env:AUTH
    $TunnelPassword.Dispose()
}
```

On SrvB:

```bash
sudo ss -ltnp 'sport = :22022'
ssh-keyscan -T 5 -p 22022 127.0.0.1 2>/dev/null | ssh-keygen -lf -
```

Expected: listener is `127.0.0.1:22022`; the returned host fingerprint is the
container host key, not SrvA's.

From a host other than SrvB:

```bash
nc -vz -w 5 "<SrvB-public-IPv4>" 22022 || echo "PASS: 22022 is not public"
```

Expected: failure/timeout.

**Secret/config handling:** `AUTH` and the tunnel password are runtime secrets.
DskA receives no LapC private key.

## Step 12: Configure LapC

Add to `~/.ssh/config`:

```sshconfig
Host SrvB-jump
    HostName <SrvB-public-IPv4>
    Port 22
    User srvb-jump
    IdentityFile ~/.ssh/lapc_srvb_auth
    IdentitiesOnly yes

Host container-via-srvb SrvA-at5395-viaSrvB
    HostName 127.0.0.1
    Port 22022
    User container-user
    IdentityFile ~/.ssh/lapc_container_auth
    IdentitiesOnly yes
    HostKeyAlias container-sshd-5395
    ProxyJump SrvB-jump
```

No alias exists for SrvA itself. LapC never authenticates to SrvA.
`container-via-srvb` is the clear primary alias. The combined `Host` line also
preserves `SrvA-at5395-viaSrvB` as a compatibility alias for environments that
still require the original command.

Verify:

```bash
chmod 600 "$HOME/.ssh/config"
ssh -G container-via-srvb |
  grep -E '^(user|hostname|port|proxyjump|hostkeyalias|identityfile) '
```

Expected: container user, final `127.0.0.1:22022`, jump `SrvB-jump`,
`lapc_container_auth` identity, and the container host-key alias.

Before accepting host keys, verify SrvB's SSH host fingerprint and the
container's host fingerprint through trusted channels. DskA separately verifies
SrvA's host key in the Step 9 outer SSH session.

Never use `StrictHostKeyChecking=no` or curl without TLS verification.

**Secret/config handling:** LapC keeps only its two private keys. It has no
SrvA key and no DskA address.

## Step 13: Verify end to end

Start in this order:

1. Container `sshd`.
2. DskA's `ssh -N` bridge to SrvA.
3. SrvB's Chisel server.
4. DskA's Chisel client.
5. LapC's SSH client.

From LapC:

```bash
ssh container-via-srvb
```

Inside:

```bash
whoami
hostname
printf 'SSH_CONNECTION=%s\n' "$SSH_CONNECTION"
```

Expected: `container-user`, the intended container hostname, and a normal shell.

On SrvA:

```bash
CONTAINER="<SrvA-container-name>"
docker exec "$CONTAINER" hostname
```

Expected: hostname matches LapC's session.

Final boundary checks:

```bash
# SrvA
docker port "$CONTAINER" 5395/tcp

# SrvB
sudo ss -ltnp 'sport = :22022'

# Other host
nc -vz -w 5 "<SrvB-public-IPv4>" 5395 || echo "PASS: 5395 not public"
nc -vz -w 5 "<SrvB-public-IPv4>" 22022 || echo "PASS: 22022 not public"
```

Expected: only host loopback mappings/listeners and no public `5395`/`22022`.

If the SSH connection fails, use `ssh -vvv container-via-srvb` and diagnose:

1. LapC to SrvB and `127.0.0.1:22022`.
2. DskA outer SSH to SrvA and local `22023`.
3. DskA Chisel client to SrvB over HTTPS.
4. Container host-key verification.
5. Container public-key authentication.

AdmX tests with its vault copies through approved test endpoints. AdmX must not
copy LapC private keys onto DskA merely to test.

**Secret/config handling:** Keep verbose diagnostics private.

## Step 14: Revoke or restore LapC access

Enable:

```bash
STAGE="$HOME/chisel-openssh-deploy-incoming"
docker cp "$STAGE/lapc_container_auth.pub" \
  "$CONTAINER:/tmp/lapc_container_auth.pub"
docker exec --user 0 "$CONTAINER" sh -ec '
  set -eu
  authorized_keys_file=/etc/ssh/container_authorized_keys/container-user
  authorized_public_key="$(cat /tmp/lapc_container_auth.pub)"
  touch "$authorized_keys_file"
  if ! grep -qxF "$authorized_public_key" "$authorized_keys_file"; then
    printf "%s\n" "$authorized_public_key" >> "$authorized_keys_file"
  fi
  chown root:root "$authorized_keys_file"
  chmod 600 "$authorized_keys_file"
  rm -f /tmp/lapc_container_auth.pub
'
```

Temporarily revoke:

```bash
STAGE="$HOME/chisel-openssh-deploy-incoming"
docker cp "$STAGE/lapc_container_auth.pub" \
  "$CONTAINER:/tmp/lapc_container_auth.pub"
docker exec --user 0 "$CONTAINER" sh -ec '
  set -eu
  authorized_keys_file=/etc/ssh/container_authorized_keys/container-user
  updated_authorized_keys="${authorized_keys_file}.new"
  authorized_public_key="$(cat /tmp/lapc_container_auth.pub)"
  test -f "$authorized_keys_file"
  : > "$updated_authorized_keys"
  grep -vxF "$authorized_public_key" "$authorized_keys_file" \
    > "$updated_authorized_keys" || true
  chown root:root "$updated_authorized_keys"
  chmod 600 "$updated_authorized_keys"
  mv "$updated_authorized_keys" "$authorized_keys_file"
  rm -f /tmp/lapc_container_auth.pub
'
```

New LapC connections fail after removal; existing sessions remain active. This
revokes only final container access, not LapC's SrvB jump authorization.

**Secret/config handling:** AdmX's vault retains the recovery copy. The
container receives only the public key.

## Restart and redeployment

Restart order:

1. Container `sshd`.
2. DskA's `ssh -N` bridge.
3. SrvB's Chisel server.
4. DskA's Chisel client.
5. LapC's SSH connection.

An ordinary restart regenerates nothing.

For rotation or replacement:

- New LapC: AdmX generates both LapC pairs, retains the master copies, and
  delivers private keys only to LapC.
- New container: preserve the host-key volume; if intentionally rotating,
  AdmX generates the new host key and updates all trusted fingerprints.
- New SrvB certificate: update key/certificate in AdmX's vault and SrvB, then
  re-run DskA's HTTPS preflight.
- New Chisel identity: update the AdmX vault, SrvB key file, and DskA fingerprint
  together.
- Changed `lapc_srvb_auth`: update AdmX, LapC, and SrvB jump authorization.
- Changed `lapc_container_auth`: update AdmX, LapC, and the sole container
  authorized key.
- SrvA host-key change: update DskA's known-host entry; LapC does not track
  SrvA's host key.
- DskA key change: requires the SrvA administrator to authorize its new public
  key unless an existing authorized key remains in use.

If the DskA normal account loses forwarding permission, stop until the SrvA
administrator restores the restricted policy.
