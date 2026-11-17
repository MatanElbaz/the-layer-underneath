#!/usr/bin/env python3
"""Fit check for models based on RAM and download size."""

# Model download sizes in GB (Ollama)
MODELS = {
    'gpt-oss-20b': 13,  # [[gpt-oss-20b]]
    'qwen3-coder-30b': 19,  # [[qwen3-coder-30b]]
}


def verdict(size_gb, ram_gb):
    """Return fit status based on RAM and model size.

    - 'fits' if ram_gb - size_gb >= 8
    - 'tight' if ram_gb >= size_gb
    - 'no' otherwise
    """
    if ram_gb - size_gb >= 8:
        return 'fits'
    if ram_gb >= size_gb:
        return 'tight'
    return 'no'


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print('Usage: python3 fit.py <ram_gb>')
        sys.exit(1)
    try:
        ram_gb = float(sys.argv[1])
    except ValueError:
        print('RAM must be a number')
        sys.exit(1)
    for name, size in MODELS.items():
        print(f"{name}: {verdict(size, ram_gb)} ({size}GB)")
