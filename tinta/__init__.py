#!/usr/bin/env python

# Tinta — Copyright (c) 2026 github.com/brandonscript
# Licensed under the MIT License. See LICENSE.

from logging import getLogger

__version__ = "1.1.1"

__all__ = ["Tinta", "__version__"]

logger = getLogger(__name__)

try:
    from .tinta import Tinta

    assert bool(Tinta)
except ImportError as e:
    logger.warning(e)
    raise e
