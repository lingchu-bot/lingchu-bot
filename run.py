import logging
import signal
import subprocess
import sys
from pathlib import Path

import psutil


def get_python_executable() -> str:
    """获取合适的 Python 解释器路径（优先虚拟环境）"""
    python_exe = sys.executable
    venv_python = Path(".venv") / "Scripts" / "python.exe"
    if (
        not (
            hasattr(sys, "real_prefix")
            or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)
        )
        and venv_python.exists()
    ):
        python_exe = str(venv_python)
        logging.info(f"使用虚拟环境: {python_exe}")
    else:
        logging.info("正在启动子进程")
    return python_exe


def setup_signal_handler(process: subprocess.Popen | None) -> None:
    def signal_handler(signum: int, frame: object) -> None:
        logging.debug(f"接收到终止信号(signum={signum})，正在关闭... frame={frame}")
        if process and process.poll() is None:
            try:
                proc = psutil.Process(process.pid)
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except psutil.TimeoutExpired:
                    logging.warning("进程未正常终止，强制结束...")
                    proc.kill()
            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess,
            ) as e:
                logging.warning(f"psutil 终止进程失败: {e}")
        logging.debug("主进程即将退出，sys.exit(0) 来自 signal_handler")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def terminate_process(process: subprocess.Popen | None) -> None:
    if process and process.poll() is None:
        try:
            proc = psutil.Process(process.pid)
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except psutil.TimeoutExpired:
                logging.warning("进程未正常终止，强制结束...")
                proc.kill()
        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ) as e:
            logging.warning(f"psutil 终止进程失败: {e}")


def run_bot(python_exe: str, bot_file: Path) -> int:
    process: subprocess.Popen | None = None
    try:
        logging.debug(f"run_bot: 启动子进程 {python_exe} {bot_file}")
        process = subprocess.Popen([python_exe, str(bot_file)])
        try:
            while process.poll() is None:
                try:
                    process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    continue
        except KeyboardInterrupt:
            logging.debug("run_bot: 捕获到 KeyboardInterrupt，正在终止子进程...")
            terminate_process(process)
            return 0
        logging.debug(
            "run_bot: 子进程退出，returncode=%s",
            process.returncode if process else None,
        )
    except Exception:
        logging.exception("run_bot: 捕获异常")
        return 0
    else:
        return process.returncode if process else 0


def main() -> int:
    try:
        logging.basicConfig(
            format="[%(levelname)s] %(message)s",
            level=logging.INFO,
        )
        bot_file = Path("bot.py")
        logging.debug(f"main: bot_file={bot_file.resolve()} exists={bot_file.exists()}")
        if not bot_file.exists():
            logging.error("main: 没有找到 bot.py")
            return 0
        python_exe = get_python_executable()
        logging.debug(f"main: python_exe={python_exe}")
        ret = run_bot(python_exe, bot_file)
        logging.debug(f"main: run_bot 返回 {ret}")
    except Exception:
        logging.exception("main: 捕获异常")
        return 0
    else:
        return ret


if __name__ == "__main__":
    sys.exit(main())
