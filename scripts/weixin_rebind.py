import asyncio
import sys
from pathlib import Path

repo = Path(r"C:/Users/jax/AppData/Local/hermes/hermes-agent")
sys.path.insert(0, str(repo))

from hermes_constants import get_hermes_home
from gateway.platforms.weixin import qr_login


def _p(msg=""):
    print(msg, flush=True)


def _quote_env_value(value: str) -> str:
    value = "" if value is None else str(value)
    if not value or any(ch.isspace() for ch in value) or any(ch in value for ch in ['#', '"', "'"]):
        return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'
    return value


def save_env_value(key: str, value: str) -> None:
    env_path = Path(get_hermes_home()) / ".env"
    env_path.parent.mkdir(parents=True, exist_ok=True)
    lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
    prefix = key + "="
    new_line = f"{key}={_quote_env_value(value)}"
    replaced = False
    out = []
    for line in lines:
        if line.startswith(prefix):
            if not replaced:
                out.append(new_line)
                replaced = True
        else:
            out.append(line)
    if not replaced:
        out.append(new_line)
    env_path.write_text("\n".join(out) + "\n", encoding="utf-8")


def get_env_value(key: str) -> str:
    env_path = Path(get_hermes_home()) / ".env"
    if not env_path.exists():
        return ""
    prefix = key + "="
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith(prefix):
            value = line[len(prefix):].strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ['"', "'"]:
                value = value[1:-1]
            return value
    return ""


async def main():
    hermes_home = str(get_hermes_home())
    _p(f"Hermes home: {hermes_home}")
    _p("开始微信重新绑定。请用微信扫描终端二维码，并在手机上确认登录。")
    credentials = await qr_login(hermes_home, timeout_seconds=480)
    if not credentials:
        _p("QR login did not complete.")
        return 2

    account_id = credentials.get("account_id", "")
    token = credentials.get("token", "")
    base_url = credentials.get("base_url", "")
    user_id = credentials.get("user_id", "")

    save_env_value("WEIXIN_ACCOUNT_ID", account_id)
    save_env_value("WEIXIN_TOKEN", token)
    if base_url:
        save_env_value("WEIXIN_BASE_URL", base_url)
    save_env_value("WEIXIN_CDN_BASE_URL", get_env_value("WEIXIN_CDN_BASE_URL") or "https://novac2c.cdn.weixin.qq.com/c2c")

    save_env_value("WEIXIN_DM_POLICY", "pairing")
    save_env_value("WEIXIN_ALLOW_ALL_USERS", "false")
    save_env_value("WEIXIN_ALLOWED_USERS", "")
    save_env_value("WEIXIN_GROUP_POLICY", "disabled")
    save_env_value("WEIXIN_GROUP_ALLOWED_USERS", "")
    if user_id:
        save_env_value("WEIXIN_HOME_CHANNEL", user_id)

    _p("\nWeixin rebind saved.")
    _p(f"Account ID: {account_id}")
    if user_id:
        _p(f"Home/User ID: {user_id}")
    return 0

if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
