# Hermes Git Backup Cron Timeout Pattern

Use this reference when a no-agent cron job that runs a Hermes Git backup script times out instead of producing a useful Git error.

## Diagnostic Pattern

- Read the cron output under `~/.hermes/cron/output/<job_id>/...` to confirm whether the scheduler killed the script.
- Run the script manually with an outer timeout, e.g. `timeout 30s python3 ~/.hermes/scripts/<backup>.py`, to reproduce without waiting for cron.
- Inspect the script for restored machine-specific paths such as Windows `C:/Users/...` paths on Linux hosts.
- Check whether the script creates accidental literal path trees like `~/.hermes/C:/...` after migration.
- Test Git transports independently: compare a short `git ls-remote <https-url> HEAD` with `ssh -T git@github.com` when SSH keys are expected to work.

## Durable Fixes

- Resolve Hermes home portably with `Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")).expanduser()`.
- Use `HERMES_BACKUP_REMOTE` and `HERMES_BACKUP_BRANCH` environment variables for overrideable remote/branch defaults.
- Add explicit `subprocess.run(..., timeout=<seconds>)` for Git commands so failures surface as `TimeoutExpired` rather than cron-level timeouts.
- Before cloning, if the target worktree exists but lacks `.git`, treat it as a partial clone and remove/recreate it.
- Prefer `git clone --depth 1` for generated backup worktrees.
- Avoid pushing generated snapshots directly to shared `main` unless the script also handles fetch/rebase safely. A dedicated backup branch avoids non-fast-forward conflicts without force-push.

## Pitfalls

- A cron timeout message may hide the real blocked command; add subprocess-level timeouts before drawing conclusions.
- HTTPS GitHub access can hang or be unauthenticated while SSH works on the same host; use the transport verified in live state.
- Do not save the specific failed job ID, commit hash, or one-off output as durable skill knowledge; keep the reusable migration/debugging pattern only.
