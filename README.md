# Agent Security Gate

`agent-guard` is a lightweight, cross-platform security hook and policy engine for AI coding assistants. It intercepts shell commands before execution via native lifecycle hooks (`PreToolUse`, `BeforeTool`, `preToolUseHooks`) and enforces a deterministic YAML security policy.

## Prerequisites

- **macOS or Linux**
- **Python >= 3.10** with `PyYAML`

## Installation

Install via the one-line installer script:

```shell
curl -fsSL https://raw.githubusercontent.com/mietzen/agent-security-gate/main/install.sh | sh
```

Or clone the repository and run the installer locally:

```shell
git clone https://github.com/mietzen/agent-security-gate.git
cd agent-security-gate
./install.sh
```

The installer copies the `agent-guard` executable to `~/.local/bin/` and automatically configures hooks and global instruction files for all detected AI assistants.

## Usage

```text
usage: agent-guard [-h] [-v] {eval,hook,check,init,policy} ...

Agent Security Gate: Universal Safety & Policy Engine for AI Coding Agents.

positional arguments:
  {eval,hook,check,init,policy}
    eval                Process hook input from stdin (default mode)
    hook                Alias for eval
    check               Dry-run a command against security policy
    init                Initialize hooks & global instructions for AI agents
    policy              Show or inspect the active policy file

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
```

### Initializing Agent Hooks

```shell
# Configure hooks and global instructions for all supported agents
agent-guard init --all

# Or selectively configure specific agents:
agent-guard init --antigravity
agent-guard init --claude
agent-guard init --codex
agent-guard init --pi
agent-guard init --cline
agent-guard init --roo
agent-guard init --copilot
agent-guard init --opencode
agent-guard init --gemini
agent-guard init --vibe
agent-guard init --continue-dev
agent-guard init --factory
```

### Dry-running Commands

Test how `agent-guard` evaluates specific shell commands:

```shell
$ agent-guard check "mktemp -d"
Command : mktemp -d
Decision: ALLOW
Reason  : Temp directory creation allowed.

$ agent-guard check "docker run -d redis"
Command : docker run -d redis
Decision: FORCE_ASK
Reason  : Confirm Docker container lifecycle / execution operation.

$ agent-guard check "rm -rf /Users/other/data"
Command : rm -rf /Users/other/data
Decision: DENY
Reason  : Deleting files outside workspace and temp directory is forbidden: /Users/other/data
```

## Configuration

The security policy is stored in `~/.config/agent-security-gate/security_policy.yaml` (or `~/.gemini/config/security_policy.yaml`).

```yaml
# ------------------------------------------------------------------------------
# 1. HARD DENY: Strictly forbidden commands (blocked immediately)
# ------------------------------------------------------------------------------
hard_deny:
  - name: privilege_escalation
    command: "sudo|su|doas"
    reason: "Privilege escalation is forbidden."

  - name: disk_destruction
    command: "mkfs(\\.\\w+)?|dd|fdisk|parted"
    reason: "Raw disk modification or filesystem formatting is forbidden."

  - name: remote_pipe_to_shell
    command: "curl|wget"
    regex: "\\|\\s*(ba|z|k|t?c)?sh\\b"
    reason: "Piping remote download directly into shell execution is forbidden."

  - name: docker_privileged
    command: "docker"
    regex: "\\brun\\b.*--privileged"
    reason: "Running Docker with --privileged flag is forbidden."

# ------------------------------------------------------------------------------
# 2. FILE DELETION ENGINE: Path-based boundary enforcement
# ------------------------------------------------------------------------------
deletion_engine:
  temp_directories:
    - "/tmp"
    - "/private/tmp"
    - "/var/folders"
    - "$TMPDIR"
  on_temp: "allow"
  on_workspace: "force_ask"
  on_external: "deny"

# ------------------------------------------------------------------------------
# 3. CONFIRMATION REQUIRED: Prompts user before proceeding
# ------------------------------------------------------------------------------
confirm_required:
  - name: sed_in_place
    command: "sed"
    regex: "-i\\b|-i\\s*''"
    reason: "Confirm in-place file modification with sed -i."

  - name: git_destructive
    command: "git"
    regex: "\\b(reset\\s+--hard|clean\\s+-[a-zA-Z]*f|restore\\s+\\.|checkout\\s+--\\s+\\.)\\b"
    reason: "Confirm destructive git operation (discards local changes)."

  - name: git_push_commit
    command: "git"
    regex: "\\b(push|commit)\\b"
    reason: "Confirm git state modification (commit/push)."

  - name: package_management
    command: "pip|pip3|uv|poetry|npm|pnpm|yarn|brew|go"
    regex: "\\b(install|add|i|mod\\s+tidy|get)\\b"
    reason: "Confirm package/dependency modification."

  - name: docker_lifecycle
    command: "docker"
    regex: "\\b(run|stop|restart|exec|rm|rmi)\\b"
    reason: "Confirm Docker container lifecycle / execution operation."

# ------------------------------------------------------------------------------
# 4. AUTO-ALLOWED: Safe inspection, devops tools, and stream utilities
# ------------------------------------------------------------------------------
auto_allowed:
  - name: temp_dir_creation
    command: "mktemp"
    reason: "Temp directory creation allowed."

  - name: inspection_coreutils
    command: "ls|cat|head|tail|grep|rg|find|stat|file|wc|diff|echo|pwd|which|type|tr|cut|sort|uniq|paste|column|tree"
    reason: "Read-only inspection / stream tool allowed."

  - name: devops_lint_test
    command: "pytest|ruff|mypy|flake8|black|golangci-lint|staticcheck"
    reason: "DevOps build / test / lint inspection allowed."

  - name: docker_inspection
    command: "docker"
    regex: "\\b(ps|images|logs|inspect|build)\\b"
    reason: "Docker inspection / build allowed."

default_action: "allow"
```

## Supported Agent Harnesses

| Agent Harness | Hook Configuration Path | Injected Guideline File |
| :--- | :--- | :--- |
| **Google Antigravity (`agy`)** | `~/.gemini/config/hooks.json` | `~/.gemini/config/AGENTS.md` & `GEMINI.md` |
| **Claude Code** | `~/.claude/settings.json` | `~/.claude/CLAUDE.md` |
| **OpenAI Codex** | `~/.codex/hooks.json` | `~/.codex/AGENTS.md` |
| **Pi CLI / Pi Agent** | `~/.pi/hooks.json` | `~/.pi/AGENTS.md` |
| **Cline (VS Code)** | Native Execution Hook | `~/.clinerules` & `~/.config/cline/instructions.md` |
| **Roo Code (Roo-Cline)** | Native Execution Hook | `~/.roorules` & `~/.config/roo/instructions.md` |
| **Gemini CLI** | `~/.gemini/settings.json` | `~/.gemini/GEMINI.md` |
| **GitHub Copilot CLI** | `~/.config/github-copilot/hooks.json` | `~/.config/github-copilot/COPILOT.md` |
| **OpenCode** | `~/.config/opencode/hooks.json` | `~/.config/opencode/AGENTS.md` |
| **Mistral Vibe** | `~/.vibe/config.toml` | `~/.vibe/config.toml` |
| **Continue.dev** | `~/.continue/config.json` | `~/.continue/rules/security.md` |
| **Factory Droid** | `~/.factory/hooks.json` | `~/.factory/hooks.json` |

## Updating

Update to the latest version via the updater script:

```shell
curl -fsSL https://raw.githubusercontent.com/mietzen/agent-security-gate/main/scripts/updater.sh | sh
```

## Testing

Run the test suite across all agent wire protocols:

```shell
python3 tests/test_all_agents.py
```

## License

[MIT](LICENSE)
