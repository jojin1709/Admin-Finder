# Admin Finder

Python script for checking common admin/login paths on websites you own or have explicit permission to test.

Developed by [JOJIN JOHN](https://www.linkedin.com/in/jojin-john/).

## Requirements

- Python 3.8 or newer
- No third-party packages required

## Usage

```bash
python adm-finder.py https://example.com
```

On Windows you can also use:

```bat
run.bat https://example.com
```

You can also run it interactively:

```bash
python adm-finder.py
```

Useful options:

```bash
python adm-finder.py https://example.com --show-all
python adm-finder.py https://example.com --timeout 10 --delay 0.2
python adm-finder.py https://example.com --wordlist wordlist.txt
```

## Files

- `adm-finder.py` - the scanner script
- `wordlist.txt` - common admin/login paths used by the scanner
- `run.bat` - Windows launcher for the scanner
- `requirements.txt` - dependency note; no install packages are needed
- `LICENSE` - MIT license file
- `.gitignore` - generated/cache files Git should ignore
- `README.md` - setup and usage instructions

## License

This project is released under the MIT License. See `LICENSE` for details.

## Notes

The original project targeted Python 2. This version has been updated for Python 3 and loads `wordlist.txt` relative to the script location, so it works even when launched from another directory.

The bundled wordlist includes 1,000 unique admin/login paths, including common CMS, ecommerce, control panel, framework, and dashboard routes. Use `--delay` when scanning larger targets so requests stay gentle.

The entries inside `.gitignore` are not missing project files. They are generated folders and files that should be ignored if Python, tests, or packaging tools create them.
