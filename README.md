# Admin Finder

Python script for checking common admin/login paths on websites you own or have explicit permission to test.

Developed by [JOJIN JOHN](https://www.linkedin.com/in/jojin-john/).

## Features

- Works with Python 3
- No third-party packages required
- Includes 1,000 unique admin/login paths
- Supports custom wordlists
- Works on Windows, Linux, macOS, and Termux

## Requirements

- Python 3.8 or newer
- Git

## Clone The Repository

```bash
git clone https://github.com/jojin1709/Admin-Finder.git
cd Admin-Finder
```

## Run On Kali, Linux, macOS, Or Termux

No install step is needed. Do not run `pip install`; this tool uses only Python's standard library.

```bash
python3 adm-finder.py https://example.com
```

Interactive mode:

```bash
python3 adm-finder.py
```

## Run On Windows

Using the Windows launcher:

```bat
run.bat https://example.com
```

Using Python directly:

```bat
python adm-finder.py https://example.com
```

Interactive mode:

```bat
python adm-finder.py
```

## Quick Start

```bash
git clone https://github.com/jojin1709/Admin-Finder.git
cd Admin-Finder
python3 adm-finder.py https://example.com
```

## Examples

Show only possible admin/login pages:

```bash
python adm-finder.py https://example.com
```

Show every checked response:

```bash
python adm-finder.py https://example.com --show-all
```

Use a slower scan:

```bash
python adm-finder.py https://example.com --delay 0.2
```

Use a longer request timeout:

```bash
python adm-finder.py https://example.com --timeout 10
```

Use a custom wordlist:

```bash
python adm-finder.py https://example.com --wordlist wordlist.txt
```

Disable colors:

```bash
python adm-finder.py https://example.com --no-color
```

## Options

```text
usage: adm-finder.py [-h] [-w WORDLIST] [-t TIMEOUT] [-d DELAY] [--show-all]
                     [--no-color]
                     [url]
```

- `url` - target URL, for example `https://example.com`
- `-w, --wordlist` - path to a custom wordlist
- `-t, --timeout` - request timeout in seconds
- `-d, --delay` - delay between requests in seconds
- `--show-all` - print non-matching responses too
- `--no-color` - disable ANSI colors

## Update The Tool

If you already cloned the repository, update it with:

```bash
git pull origin main
```

## Files

- `adm-finder.py` - scanner script
- `wordlist.txt` - common admin/login paths used by the scanner
- `run.bat` - Windows launcher
- `LICENSE` - MIT license file
- `.gitignore` - generated/cache files Git should ignore
- `README.md` - setup and usage instructions

## Troubleshooting

If `python` does not work on Linux, macOS, or Termux, use:

```bash
python3 adm-finder.py https://example.com
```

If Kali shows `externally-managed-environment` after running `pip install`, you can ignore it. This project does not need `pip` or any external Python packages.

If Git is not installed, download it from:

```text
https://git-scm.com/downloads
```

If the scan is too fast for a target you own, add a delay:

```bash
python adm-finder.py https://example.com --delay 0.5
```

## License

This project is released under the MIT License. See `LICENSE` for details.

## Notes

Only scan websites you own or have explicit permission to test.

The original project targeted Python 2. This version has been updated for Python 3 and loads `wordlist.txt` relative to the script location, so it works even when launched from another directory.
