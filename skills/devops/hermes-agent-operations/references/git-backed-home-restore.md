# Git-Backed Hermes Home Restore Notes

## Scenario

A user had another device's Hermes state backed up to a Git repository and wanted to restore it onto the current machine.

## Durable Pattern

1. Verify local Hermes and Git first with `hermes version`, `stat ~/.hermes`, and `git ls-remote <repo> HEAD`.
2. Move the current `~/.hermes` aside to `~/.hermes.backup.<timestamp>` before cloning.
3. If Hermes recreates a skeleton `~/.hermes` between the move and clone, inspect it and move it to `~/.hermes.runtime-created.<timestamp>`.
4. If `git clone` times out or disconnects after creating the destination, move that incomplete directory to `~/.hermes.partial-clone.<timestamp>` and retry with `git clone --depth 1`.
5. After clone, copy back missing local-only files such as `config.yaml`, `.env`, and `auth.json` from the original backup when present.
6. Run `chmod -R go-rwx ~/.hermes`, then verify with `hermes version`, `hermes profile list`, and `git -C ~/.hermes status --short`.

## Reporting Notes

- A stopped gateway after file restore is not a restore failure; report gateway state separately.
- Dirty Git status after copying local config back is expected when those files are intentionally untracked or runtime-generated.
