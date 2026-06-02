#!/usr/bin/env python3
"""
Find common admin/login paths on a website you own or have permission to test.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


DEFAULT_WORDLIST = Path(__file__).with_name("wordlist.txt")
DEFAULT_USER_AGENT = "admin-finder/2.0"
FOUND_STATUSES = {200, 301, 302, 303, 307, 308, 401, 403}


class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
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
        r"###################################################################",
        r"#    ######   ######   #### ####   #####    #######               #",
        r"#     #####   #####    #### ####   #####    #####                 #",
        r"#      ####   ####     #### ####   #####   #####                  #",
        r"#       #########      #### ####   ##########                     #",
        r"#         #####        #### ####   #########                      #",
        r"#          ###         #### ####   ##########                     #",
        r"#          ###         #### ####   #####   #####   ADMIN FINDER   #",
        r"#          ###         #### ####   #####    #####   Python 3      #",
        r"#          ###         #### ####   #####    ######   version 2.0  #",
        r"###################################################################",
    ]
    print()
    for line in lines:
        print(Colors.wrap(f"\t{line}", Colors.HEADER))
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


def scan(
    base_url: str,
    paths: Iterable[str],
    timeout: float,
    delay: float,
    show_all: bool,
) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []

    print(Colors.wrap(f"[*] Scanning {base_url}", Colors.YELLOW))
    for path in paths:
        target = urljoin(base_url, path)
        status, detail = request_status(target, timeout)

        if status in FOUND_STATUSES:
            found.append((status, target))
            print(Colors.wrap(f"[+] {status} {target}", Colors.GREEN))
        elif show_all:
            if status is None:
                print(Colors.wrap(f"[-] ERROR {target} ({detail})", Colors.RED))
            else:
                print(Colors.wrap(f"[-] {status} {target}", Colors.RED))

        if delay > 0:
            time.sleep(delay)

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
    parser.add_argument("-t", "--timeout", default=5.0, type=float, help="Request timeout in seconds")
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
            "[!] Only scan websites you own or have explicit permission to test.",
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
    found = scan(base_url, paths, args.timeout, args.delay, args.show_all)

    print()
    if found:
        print(Colors.wrap("[+] Possible admin/login pages found:", Colors.GREEN))
        for status, url in found:
            print(Colors.wrap(f"    {status} {url}", Colors.GREEN))
    else:
        print(Colors.wrap("[-] No matching admin/login pages found.", Colors.RED))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
