# Upgrade sentence-transformers to Fix Dependency Issue

The issue is that `sentence-transformers==2.2.2` is incompatible with newer `huggingface_hub` versions.

## Solution: Uninstall and Install Newer Version

Run these commands:

```bash
cd backend
source venv/bin/activate

# Uninstall the old version
pip uninstall sentence-transformers -y

# Install the latest version (or at least 2.7.0+)
pip install sentence-transformers>=2.7.0

# Or install latest
pip install sentence-transformers --upgrade
```

## Verify the Version

Check that it installed correctly:

```bash
pip show sentence-transformers
```

You should see version 2.7.0 or higher.

## Then Update requirements.txt

The `requirements.txt` file has been updated to use `sentence-transformers>=2.7.0`, but you may need to uninstall the old pinned version first.

## Alternative: Force Reinstall

If the above doesn't work:

```bash
pip uninstall sentence-transformers -y
pip install sentence-transformers --no-cache-dir --upgrade
```

This forces a fresh install without using cached packages.

