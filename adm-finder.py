#!/usr/bin/env python3
"""
Find common admin/login paths on a website you own or have permission to test.
"""

from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


DEFAULT_WORDLIST = Path(__file__).with_name("wordlist.txt")
DEFAULT_USER_AGENT = "admin-finder/2.1"
FOUND_STATUSES = {200, 301, 302, 303, 307, 308, 401, 403}


class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"

    enabled = True

    @classmethod
    def wrap(cls, text: str, color: str) -> str:
        if not cls.enabled:
            return text
        return f"{color}{text}{cls.ENDC}"


def banner() -> None:
    lines = [
        "+------------------------------------------------------------+",
        "| ADMIN FINDER v2.1                                          |",
        "| Fast admin/login path checker for Python 3                 |",
        "| Developed by JOJIN JOHN                                   |",
        "+------------------------------------------------------------+",
    ]
    print()
    for line in lines:
        print(Colors.wrap(line, Colors.CYAN))
    print()


def normalize_base_url(raw_url: str) -> str:
    raw_url = raw_url.strip()
    if not raw_url:
        raise ValueError("URL cannot be empty.")

    if "://" not in raw_url:
        raw_url = f"http://{raw_url}"

    parsed = urlparse(raw_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Enter a valid http or https URL.")

    return f"{parsed.scheme}://{parsed.netloc}/"


def load_paths(wordlist: Path) -> list[str]:
    if not wordlist.exists():
        raise FileNotFoundError(f"Wordlist not found: {wordlist}")

    paths: list[str] = []
    seen: set[str] = set()
    with wordlist.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            item = line.strip()
            if not item or item.startswith("#"):
                continue
            item = item.lstrip("/")
            if item not in seen:
                seen.add(item)
                paths.append(item)
    return paths


def request_status(url: str, timeout: float) -> tuple[int | None, str | None]:
    request = Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.status, response.geturl()
    except HTTPError as error:
        return error.code, error.geturl()
    except (TimeoutError, URLError, OSError) as error:
        return None, str(error)


def check_path(base_url: str, path: str, timeout: float) -> tuple[str, str, int | None, str | None]:
    target = urljoin(base_url, path)
    status, detail = request_status(target, timeout)
    return path, target, status, detail


def status_label(status: int | None) -> str:
    if status is None:
        return "ERR"
    return str(status)


def print_progress(checked: int, total: int, found_count: int, path: str, status: int | None) -> None:
    percent = int((checked / total) * 100) if total else 100
    path_preview = path[:38] + ("..." if len(path) > 38 else "")
    message = (
        f"[*] Progress {checked:>4}/{total:<4} "
        f"({percent:>3}%) | found {found_count:<3} | last {status_label(status):>3} {path_preview:<41}"
    )
    print(Colors.wrap("\r" + message, Colors.BLUE), end="", flush=True)


def scan(
    base_url: str,
    paths: Iterable[str],
    timeout: float,
    delay: float,
    show_all: bool,
    workers: int,
) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []
    paths_list = list(paths)
    total = len(paths_list)
    workers = max(1, min(workers, total or 1))

    print(Colors.wrap(f"[*] Target   : {base_url}", Colors.YELLOW))
    print(Colors.wrap(f"[*] Paths    : {total}", Colors.YELLOW))
    print(Colors.wrap(f"[*] Timeout  : {timeout}s", Colors.YELLOW))
    print(Colors.wrap(f"[*] Workers  : {workers}", Colors.YELLOW))

    def handle_result(path: str, target: str, status: int | None, detail: str | None) -> None:
        if status in FOUND_STATUSES:
            found.append((status, target))
            if not show_all:
                print()
            print(Colors.wrap(f"[FOUND] {status} {target}", Colors.GREEN))
        elif show_all:
            if status is None:
                print(Colors.wrap(f"[MISS]  ERR {target} ({detail})", Colors.RED))
            else:
                print(Colors.wrap(f"[MISS]  {status} {target}", Colors.RED))

    if not paths_list:
        print(Colors.wrap("[!] Wordlist is empty.", Colors.RED))
        return found

    if delay > 0 or workers == 1:
        if delay > 0 and workers > 1:
            print(Colors.wrap("[*] Delay enabled, using one worker for gentle scanning.", Colors.YELLOW))
        for checked, path in enumerate(paths_list, start=1):
            path, target, status, detail = check_path(base_url, path, timeout)
            handle_result(path, target, status, detail)
            if not show_all:
                print_progress(checked, total, len(found), path, status)
            if delay > 0 and checked < total:
                time.sleep(delay)
    else:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(check_path, base_url, path, timeout) for path in paths_list]
            for checked, future in enumerate(as_completed(futures), start=1):
                path, target, status, detail = future.result()
                handle_result(path, target, status, detail)
                if not show_all:
                    print_progress(checked, total, len(found), path, status)

    if not show_all:
        print()

    return found


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find common admin/login paths on authorized websites.",
    )
    parser.add_argument("url", nargs="?", help="Target URL, for example https://example.com")
    parser.add_argument(
        "-w",
        "--wordlist",
        default=DEFAULT_WORDLIST,
        type=Path,
        help=f"Path to wordlist file (default: {DEFAULT_WORDLIST.name})",
    )
    parser.add_argument("-t", "--timeout", default=3.0, type=float, help="Request timeout in seconds")
    parser.add_argument("-c", "--workers", default=8, type=int, help="Number of parallel requests")
    parser.add_argument("-d", "--delay", default=0.0, type=float, help="Delay between requests in seconds")
    parser.add_argument("--show-all", action="store_true", help="Print non-matching responses too")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI colors")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    Colors.enabled = not args.no_color

    banner()
    print(
        Colors.wrap(
            "[!] Use only on websites you own or have permission to test.",
            Colors.YELLOW,
        )
    )

    raw_url = args.url or input(Colors.wrap("Enter the website URL: ", Colors.BLUE))

    try:
        base_url = normalize_base_url(raw_url)
        paths = load_paths(args.wordlist)
    except (FileNotFoundError, ValueError) as error:
        print(Colors.wrap(f"[!] {error}", Colors.RED), file=sys.stderr)
        return 1

    print(Colors.wrap(f"[*] Loaded {len(paths)} paths from {args.wordlist}", Colors.YELLOW))
    found = scan(base_url, paths, args.timeout, args.delay, args.show_all, args.workers)

    print()
    if found:
        print(Colors.wrap("[+] Scan complete. Possible admin/login pages found:", Colors.GREEN))
        for status, url in found:
            print(Colors.wrap(f"    {status} {url}", Colors.GREEN))
    else:
        print(Colors.wrap("[-] Scan complete. No matching admin/login pages found.", Colors.RED))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
