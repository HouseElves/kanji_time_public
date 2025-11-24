# Troubleshooting

## Installation Issues

### "The virtual environment was not created successfully" (Ubuntu/Debian)

**Problem:** `python3 -m venv` fails with ensurepip error.

**Solution:**
```bash
sudo apt install python3-venv
```

Then retry the installation steps.

### Python version too old

**Problem:** `kanji_time requires Python >=3.11`

**Solution:** Check your version:
```bash
python3 --version
```

Upgrade if needed. See [python.org](https://www.python.org/downloads/) for installation.

### Missing system libraries (lxml/pillow build failures)

**Problem:** Compilation errors during pip install.

**Solution:** Install development headers:
```bash
# Ubuntu/Debian
sudo apt install python3-dev build-essential libxml2-dev libxslt1-dev libjpeg-dev zlib1g-dev

# macOS (requires Homebrew)
brew install libxml2 libxslt jpeg

# Windows
# Usually not needed - pip provides binary wheels
```

## Runtime Issues

### "kanjitime: command not found"

**Problem:** Virtual environment not activated.

**Solution:**
```bash
# Activate it first
source .kanji_time/bin/activate  # Linux/macOS
.kanji_time\Scripts\activate      # Windows
```

### Permission denied errors

**Problem:** Can't write PDF output files.

**Solution:** Check you have write permissions in the current directory, or use `--output-dir` to specify a different location.
