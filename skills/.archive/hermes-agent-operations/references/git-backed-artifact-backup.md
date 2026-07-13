# Git-backed Hermes artifact backup troubleshooting

Use when a scheduled Hermes script mirrors selected `~/.hermes` artifacts into a GitHub repository.

## Durable patterns

- Make the source home portable: prefer `Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")).expanduser()` over host-specific absolute paths.
- Put backup worktrees under `~/.hermes/backups/...` and exclude `backups/` from mirrored content to avoid recursive copies.
- Give every Git subprocess a bounded timeout so cron reports a concrete failure instead of hanging until the scheduler kills the script.
- If `git clone` creates a partial directory without `.git`, treat it as a failed worktree and move/remove/recreate it before retrying.
- When remote `main` already has unrelated history, push automated backups to a dedicated branch such as `hermes-artifacts-backup` instead of force-pushing over `main`.
- For noninteractive cron pushes, prefer SSH remotes when SSH auth is configured; HTTPS remotes can fail with `could not read Username` unless token credentials are explicitly configured.
- If the host uses a local proxy, inject proxy environment for Git subprocesses (`HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY` and lowercase variants), ideally controlled by a script env var such as `HERMES_BACKUP_PROXY`.

## Verification sequence

1. Test GitHub reachability with the same proxy/auth style the script will use.
2. Run the backup script manually from the cron workdir.
3. Trigger the cron job once with the scheduler, then check `last_status` instead of assuming manual success proves cron success.
4. Confirm the remote backup branch exists with `git ls-remote --heads origin <branch>`.

## Common failure signatures

- `Script timed out after 120s`: usually an unbounded Git network operation inside a no-agent cron script.
- `fatal: could not read Username for 'https://github.com'`: HTTPS push lacks noninteractive credentials; switch to SSH or configure a token credential helper.
- `! [rejected] main -> main (fetch first)`: remote branch has history not present locally; use a dedicated backup branch or rebase intentionally.
