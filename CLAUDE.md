
## cmux Environment

You are running in a **cmux-enhanced terminal**. This environment provides integrated tools for web browsing, terminal orchestration, and multi-pane workflows.

### Browser Automation (most useful for Claude)

| Command | Description |
|---------|-------------|
| `cmux browser open <url>` | Open a live web view alongside the terminal |
| `cmux browser <surface> snapshot` | **Read the page content** (DOM snapshot Claude can parse) |
| `cmux browser <surface> get text` | Get plain text of current page |
| `cmux browser <surface> navigate <url>` | Navigate existing browser surface to new URL |
| `cmux browser <surface> eval <script>` | Run JavaScript and return result |
| `cmux browser <surface> click <selector>` | Click an element |
| `cmux browser <surface> fill <selector> <text>` | Fill a form field |
| `cmux browser <surface> wait --selector <css>` | Wait for element to appear |
| `cmux browser <surface> get url` | Get current URL |

Browser restriction:
- AI agents must not save, download, export, or write files from the browser. Browser use is read/interact only; file creation and edits must happen through terminal/file tools.

### Workspace & Pane Management

| Command | Description |
|---------|-------------|
| `cmux identify` | Get current surface/workspace/pane refs (JSON) |
| `cmux list-workspaces` | List all workspaces |
| `cmux list-panes` | List panes in current workspace |
| `cmux list-pane-surfaces --pane <ref>` | List surfaces (tabs) in a pane |
| `cmux new-workspace [--command <cmd>]` | Create new workspace |
| `cmux new-pane [--type terminal|browser] [--url <url>]` | Create new pane |
| `cmux new-split <left|right|up|down>` | Split current pane |
| `cmux select-workspace --workspace <ref>` | Switch to workspace |
| `cmux rename-workspace <title>` | Rename current workspace |

### Terminal I/O

| Command | Description |
|---------|-------------|
| `cmux read-screen [--surface <ref>] [--scrollback]` | Read terminal output Claude can see |
| `cmux send [--surface <ref>] <text>` | Send text/commands to a terminal pane |
| `cmux send-key [--surface <ref>] <key>` | Send keypress to a pane |
| `cmux capture-pane [--scrollback]` | tmux-compatible screen capture |

### Notifications & Status

| Command | Description |
|---------|-------------|
| `cmux notify --title "<title>" --body "<body>"` | Send desktop notification |
| `cmux set-status <key> <value> [--icon <name>] [--color <#hex>]` | Set sidebar status |
| `cmux set-progress <0.0-1.0> [--label <text>]` | Show progress bar in sidebar |
| `cmux log [--level <level>] <message>` | Log to sidebar |
| `cmux clear-progress` | Clear progress bar |

### Workflow for Claude to read web pages

1. `cmux browser open <url>` → opens browser pane, returns surface ref
2. `cmux browser <surface-ref> snapshot` → Claude reads the DOM content
3. `cmux browser <surface-ref> get text` → cleaner plain text if needed
4. Use `click`, `fill`, `eval` for interactive pages (SPAs, auth, forms)

### Notes

- Get surface refs with `cmux identify` or `cmux list-pane-surfaces --pane <ref>`
- Browser snapshot gives structured DOM (links, buttons, headings with refs)
- `read-screen` lets Claude read any terminal pane output, not just the current one
- `send` lets Claude run commands in other panes (e.g. a dev server pane)

### When to use cmux vs alternatives

**Use `cmux browser` instead of WebFetch/curl when:**
- Page requires JavaScript to render (SPAs, React apps, dashboards)
- Page requires login/auth — the browser already has the session
- You need to interact: click buttons, fill forms, navigate multi-step flows
- You need to inspect specific elements by CSS selector or wait for dynamic content

**Use WebFetch/curl instead of cmux browser when:**
- Page is static (docs, plain HTML) — faster and simpler
- No browser pane is already open
- You just need raw content extraction with no interaction

**Use `cmux send` + `cmux read-screen` when:**
- You need to run commands in another terminal pane and read the output
- Monitoring a dev server, test runner, or log stream running in a split pane
- Orchestrating multi-pane workflows (e.g. start server in pane A, run tests in pane B, read results)

**Use `cmux set-progress` / `cmux set-status` when:**
- Running long tasks — show progress in the sidebar so the user can track without asking
- Surfacing task state (e.g. "deploying", "tests passing") without cluttering terminal output

