#!/usr/bin/env python3
"""
Interactive CLI Bot Manager using DeepSeek V3.2 API

This script creates, manages, and deploys AI bots using only the DeepSeek API.
"""

import os
import sys
import json
import requests
from typing import List, Dict, Optional
import subprocess
import getpass
from datetime import datetime
from pathlib import Path

# Optional colored output
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLORS = True
except ImportError:
    HAS_COLORS = False
    class Fore:
        GREEN = YELLOW = CYAN = RED = MAGENTA = BLUE = WHITE = ''
    class Style:
        BRIGHT = DIM = NORMAL = RESET_ALL = ''

class BotManager:
    """Main bot manager class for creating and managing DeepSeek bots."""
    
    def __init__(self):
        self.bot_name = ""
        self.bot_purpose = ""
        self.conversation_history: List[Dict] = []
        self.api_key = None
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.model = "deepseek-chat"
        
    def print_colored(self, text: str, color: str = Fore.WHITE, style: str = Style.NORMAL) -> None:
        """Print colored text if colorama is available."""
        if HAS_COLORS:
            print(f"{style}{color}{text}{Style.RESET_ALL}")
        else:
            print(text)
    
    def get_user_input(self, prompt: str, color: str = Fore.CYAN) -> str:
        """Get user input with optional coloring."""
        self.print_colored(prompt, color, Style.BRIGHT)
        return input("> ").strip()
    
    def create_bot(self) -> None:
        """Main workflow for creating a new bot."""
        self.print_colored("\n" + "="*50, Fore.MAGENTA)
        self.print_colored("🤖 DEEPSEEK BOT MANAGER", Fore.MAGENTA, Style.BRIGHT)
        self.print_colored("="*50, Fore.MAGENTA)
        
        # Step 1: Get bot name
        while True:
            self