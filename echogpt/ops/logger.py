#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EchoGPT Logger
Centralized logging system
"""
import logging
import sys
from pathlib import Path


def get_logger(name: str = "echogpt", level: int = logging.INFO) -> logging.Logger:
    """Get configured logger"""

    logger = logging.getLogger(name)

    # 이미 핸들러가 있으면 재사용
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # 포맷터
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    # 상위 로거로 전파 방지
    logger.propagate = False

    return logger
