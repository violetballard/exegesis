# iPhone Remote Monitor Shortcuts

These are paste-ready recipes for a folder of iOS Shortcuts that talk to the `qual` remote monitor over VPN. They are intentionally tiny: status, kick, start, and stop. No remote commits, no packet editing, no arbitrary shell.

## Setup

Create an iPhone Shortcuts folder named `Exegesis Monitor`.

Use these two values in every shortcut:

```text
MONITOR_BASE_URL = http://<vpn-ip-or-vpn-dns-name>:8765
MONITOR_TOKEN = <remote-monitor-token>
```

Recommended VPN address examples:

```text
http://100.x.y.z:8765
http://qual-dev.tailnet-name.ts.net:8765
```

Every request except health uses this header:

```text
Authorization: Bearer MONITOR_TOKEN
```

For control shortcuts, also set:

```text
Content-Type: application/json
Accept: application/json
```

## Shortcut 1: Exegesis Status

Purpose: compact status check while away.

Shortcut actions:

1. `URL`

```text
MONITOR_BASE_URL/api/status/text
```

2. `Get Contents of URL`

```text
Method: GET
Headers:
  Authorization: Bearer MONITOR_TOKEN
  Accept: text/plain
```

3. `Quick Look` or `Show Result`

Expected result: compact plain text with daemon state, queue counts, active jobs, blocker, git cleanliness, and memory summary.

## Shortcut 2: Exegesis Full Status

Purpose: fuller sanitized snapshot if the compact status is not enough.

Shortcut actions:

1. `URL`

```text
MONITOR_BASE_URL/api/status
```

2. `Get Contents of URL`

```text
Method: GET
Headers:
  Authorization: Bearer MONITOR_TOKEN
  Accept: application/json
```

3. `Quick Look`

Expected result: sanitized JSON only. It must not expose raw logs, prompts, env vars, tokens, full command lines, or packet bodies.

## Shortcut 3: Exegesis Kick

Purpose: ask the coordinator to reconcile promptly without starting a new remote shell or doing any git mutation.

Shortcut actions:

1. `Text`

```json
{"operator":"iphone","reason":"kick from phone"}
```

2. `URL`

```text
MONITOR_BASE_URL/api/control/kick
```

3. `Get Contents of URL`

```text
Method: POST
Request Body: File
File: Text from step 1
Headers:
  Authorization: Bearer MONITOR_TOKEN
  Content-Type: application/json
  Accept: application/json
```

4. `Show Result`

## Shortcut 4: Exegesis Start

Purpose: start the daemon if it is down.

Shortcut actions:

1. `Text`

```json
{"operator":"iphone","reason":"start from phone"}
```

2. `URL`

```text
MONITOR_BASE_URL/api/control/start
```

3. `Get Contents of URL`

```text
Method: POST
Request Body: File
File: Text from step 1
Headers:
  Authorization: Bearer MONITOR_TOKEN
  Content-Type: application/json
  Accept: application/json
```

4. `Show Result`

## Shortcut 5: Exegesis Stop

Purpose: stop the daemon when the machine needs to cool down or you see runaway pressure.

Add a confirmation step before the request.

Shortcut actions:

1. `Ask for Confirmation`

```text
Stop the Exegesis daemon?
```

2. `Text`

```json
{"operator":"iphone","reason":"stop from phone"}
```

3. `URL`

```text
MONITOR_BASE_URL/api/control/stop
```

4. `Get Contents of URL`

```text
Method: POST
Request Body: File
File: Text from step 2
Headers:
  Authorization: Bearer MONITOR_TOKEN
  Content-Type: application/json
  Accept: application/json
```

5. `Show Result`

## Optional: Health Check Without Token

Purpose: verify the monitor process is reachable without exposing daemon state.

Shortcut actions:

1. `URL`

```text
MONITOR_BASE_URL/healthz
```

2. `Get Contents of URL`

```text
Method: GET
```

3. `Show Result`

## Recommended Home Screen Layout

Put these in one folder or widget stack:

```text
Exegesis Status
Exegesis Kick
Exegesis Start
Exegesis Stop
Exegesis Full Status
```

Use `Exegesis Status` most of the time. Use `Kick` only when the queue looks idle but should be moving. Use `Stop` only for resource pressure or shutdown.

## Security Notes

- Keep the token only in Shortcuts or iOS Keychain-backed storage if you later wrap this in a native helper.
- Do not paste the token into chat.
- Do not expose the monitor outside the VPN interface.
- Keep `Stop` behind a confirmation prompt.
