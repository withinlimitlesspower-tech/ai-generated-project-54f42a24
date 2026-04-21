#!/usr/bin/env python3
"""
Interactive CLI Bot Manager using DeepSeek V3.2 API
Main application file
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from typing import List, Dict, Any, Optional

# Import bot modules
try:
    from bot import DeepSeekBot
    from config import Config
except ImportError:
    print("Error: Required modules not found. Make sure bot.py and config.py exist.")
    sys.exit(1)


class BotManager:
    """Main application class for managing bots"""
    
    def __init__(self):
        self.config = Config()
        self.current_bot = None
        self.conversation_history = []
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title: str):
        """Print formatted header"""
        self.clear_screen()
        print("=" * 60)
        print(f"{title:^60}")
        print("=" * 60)
        print()
    
    def get_user_input(self, prompt: str, default: str = "") -> str:
        """Get user input with colored prompt"""
        try:
            from colorama import Fore, Style, init
            init()
            user_input = input(f"{Fore.CYAN}{prompt}{Style.RESET_ALL} ").strip()
        except ImportError:
            user_input = input(f"{prompt} ").strip()
        
        return user_input if user_input else default
    
    def create_bot(self):
        """Create a new bot with user-defined parameters"""
        self.print_header("Create New Bot")
        
        # Get bot name
        while True:
            bot_name = self.get_user_input("What would you like to name your bot?")
            if bot_name:
                break
            print("Bot name cannot be empty. Please try again.")
        
        # Get bot purpose
        while True:
            bot_purpose = self.get_user_input(
                "What should this bot do? (e.g., code assistant, friendly chat, teacher)"
            )
            if bot_purpose:
                break
            print("Bot purpose cannot be empty. Please try again.")
        
        # Confirm creation
        print(f"\nBot Name: {bot_name}")
        print(f"Bot Purpose: {bot_purpose}")
        print()
        
        confirm = self.get_user_input("Do you want to create this bot? (yes/no)").lower()
        
        if confirm == 'yes':
            try:
                # Create bot instance
                self.current_bot = DeepSeekBot(
                    name=bot_name,
                    purpose=bot_purpose,
                    config=self.config
                )
                
                print(f"\n✅ Bot '{bot_name}' created successfully!")
                
                # Ask about GitHub integration
                self.github_integration(bot_name)
                
                # Start chat session
                self.chat_session()
                
            except Exception as e:
                print(f"❌ Error creating bot: {e}")
                self.get_user_input("\nPress Enter to continue...")
        else:
            # Allow editing
            edit_choice = self.get_user_input(
                "Would you like to edit the name or purpose? (name/purpose/no)"
            ).lower()
            
            if edit_choice == 'name':
                self.create_bot()  # Restart creation process
            elif edit_choice == 'purpose':
                # Reuse name, get new purpose
                bot_purpose = self.get_user_input(
                    "Enter new purpose for the bot:"
                )
                if bot_purpose:
                    try:
                        self.current_bot = DeepSeekBot(
                            name=bot_name,
                            purpose=bot_purpose,
                            config=self.config
                        )
                        print(f"\n✅ Bot '{bot_name}' updated successfully!")
                        self.chat_session()
                    except Exception as e:
                        print(f"❌ Error updating bot: {e}")
    
    def github_integration(self, bot_name: str):
        """Handle GitHub repository creation and file pushing"""
        self.print_header("GitHub Integration")
        
        use_github = self.get_user_input(
            "Would you like to push this bot to GitHub? (yes/no)"
        ).lower()
        
        if use_github != 'yes':
            return
        
        # Get project name
        project_name = self.get_user_input(
            "Enter project name for GitHub repo:",
            default=bot_name.lower().replace(" ", "-")
        )
        
        # Check if git is installed
        try:
            subprocess.run(['git', '--version'], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Git is not installed or not in PATH.")
            print("Please install git to use GitHub integration.")
            self.get_user_input("\nPress Enter to continue...")
            return
        
        # Create necessary files
        self.create_project_files(project_name)
        
        # Initialize git repo
        try:
            # Initialize repository
            subprocess.run(['git', 'init'], check=True, capture_output=True)
            subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
            subprocess.run(
                ['git', 'commit', '-m', f'Initial commit: {bot_name} bot'],
                check=True,
                capture_output=True
            )
            
            print(f"\n✅ Local git repository initialized.")
            
            # Ask for remote URL
            remote_url = self.get_user_input(
                "Enter GitHub remote URL (or leave empty to skip):"
            )
            
            if remote_url:
                subprocess.run(['git', 'remote', 'add', 'origin', remote_url], 
                             check=True, capture_output=True)
                
                # Try to push
                try:
                    result = subprocess.run(
                        ['git', 'push', '-u', 'origin', 'main'],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        print(f"\n✅ Successfully pushed to GitHub!")
                        print(f"Repository: {remote_url}")
                    else:
                        # Try with master branch
                        result = subprocess.run(
                            ['git', 'push', '-u', 'origin', 'master'],
                            capture_output=True,
                            text=True
                        )
                        if result.returncode == 0:
                            print(f"\n✅ Successfully pushed to GitHub!")
                            print(f"Repository: {remote_url}")
                        else:
                            print(f"\n⚠️  Could not push to GitHub automatically.")
                            print("Please push manually using:")
                            print(f"  git push -u origin main")
                            
                except Exception as e:
                    print(f"❌ Error pushing to GitHub: {e}")
            
        except Exception as e:
            print(f"❌ Error setting up git: {e}")
        
        self.get_user_input("\nPress Enter to continue...")
    
    def create_project_files(self, project_name: str):
        """Create all necessary project files"""
        # Create README.md
        readme_content = f"""# {project_name} - DeepSeek Bot

This is an interactive CLI bot created using DeepSeek V3.2 API.

## Features
- Interactive chat interface
- Conversation memory
- Session management
- Easy to extend

## Setup

1. Install dependencies:
pip install -r requirements.txt

2. Set up your DeepSeek API key:
export DEEPSEEK_API_KEY='your-api-key-here'

Or create a `.env` file:
DEEPSEEK_API_KEY=your-api-key-here

3. Run the bot:
python app.py

## Usage
- Type your messages to chat with the bot
- Type 'exit' to quit
- Type 'clear' to reset conversation
- Type 'save' to save conversation to file

## Configuration
Edit `config.py` to modify bot behavior, temperature, and other settings.
"""
        
        with open('README.md', 'w') as f:
            f.write(readme_content)
        
        # Create requirements.txt
        requirements = """requests>=2.31.0
python-dotenv>=1.0.0
colorama>=0.4.6"""
        
        with open('requirements.txt', 'w') as f:
            f.write(requirements)
        
        print("✅ Project files created successfully!")
    
    def chat_session(self):
        """Start interactive chat session with the bot"""
        if not self.current_bot:
            print("❌ No bot created. Please create a bot first.")
            return
        
        self.print_header(f"Chat with {self.current_bot.name}")
        print(f"Purpose: {self.current_bot.purpose}")
        print("\nCommands:")
        print("  'exit' - Quit chat")
        print("  'clear' - Reset conversation")
        print("  'save' - Save conversation to file")
        print("  'help' - Show commands")
        print("-" * 60)
        
        # Reset conversation history for new session
        self.conversation_history = []
        
        while True:
            try:
                # Get user input
                user_input = self.get_user_input(f"You: ")
                
                # Check for commands
                if user_input.lower() == 'exit':
                    print(f"\n👋 Goodbye! Thanks for chatting with {self.current_bot.name}.")
                    break
                
                elif user_input.lower() == 'clear':
                    self.conversation_history = []
                    print("\n🔄 Conversation cleared.")
                    continue
                
                elif user_input.lower() == 'save':
                    self.save_conversation()
                    continue
                
                elif user_input.lower() == 'help':
                    print("\n📋 Available commands:")
                    print("  'exit' - Quit chat")
                    print("  'clear' - Reset conversation")
                    print("  'save' - Save conversation to file")
                    print("  'help' - Show this help")
                    continue
                
                # Add user message to history
                self.conversation_history.append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Get bot response
                print(f"\n{self.current_bot.name}: ", end="", flush=True)
                
                response = self.current_bot.chat(
                    message=user_input,
                    conversation_history=self.conversation_history[:-1]  # Exclude current message
                )
                
                # Add bot response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Print response
                try:
                    from colorama import Fore, Style
                    print(f"{Fore.GREEN}{response}{Style.RESET_ALL}")
                except ImportError:
                    print(response)
                
                print()  # Empty line for readability
                
            except KeyboardInterrupt:
                print(f"\n\n👋 Interrupted. Thanks for chatting with {self.current_bot.name}.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again or type 'exit' to quit.")
    
    def save_conversation(self):
        """Save conversation history to a file"""
        if not self.conversation_history:
            print("❌ No conversation to save.")
            return
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.json"
        
        try:
            # Prepare conversation data
            conversation_data = {
                "bot_name": self.current_bot.name if self.current_bot else "Unknown",
                "bot_purpose": self.current_bot.purpose if self.current_bot else "Unknown",
                "saved_at": datetime.now().isoformat(),
                "messages": self.conversation_history
            }
            
            # Save to file
            with open(filename, 'w') as f:
                json.dump(conversation_data, f, indent=2)
            
            print(f"✅ Conversation saved to '{filename}'")
            
        except Exception as e:
            print(f"❌ Error saving conversation: {e}")
    
    def main_menu(self):
        """Display main menu and handle user choices"""
        while True:
            self.print_header("DeepSeek Bot Manager")
            
            print("1. Create New Bot")
            print("2. Load Existing Bot")
            print("3. Configure API Settings")
            print("4. Exit")
            print()
            
            choice = self.get_user_input("Select an option (1-4):")
            
            if choice == '1':
                self.create_bot()
            elif choice == '2':
                self.load_bot()
            elif choice == '3':
                self.configure_api()
            elif choice == '4':
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1-4.")
                self.get_user_input("\nPress Enter to continue...")
    
    def load_bot(self):
        """Load an existing bot from configuration"""
        self.print_header("Load Existing Bot")
        
        # Check for existing bot files
        if not os.path.exists('bot_config.json'):
            print("❌ No existing bot configuration found.")
            print("Please create a new bot first.")
            self.get_user_input("\nPress Enter to continue...")
            return
        
        try:
            with open('bot_config.json', 'r') as f:
                bot_config = json.load(f)
            
            print(f"Found bot: {bot_config.get('name', 'Unknown')}")
            print(f"Purpose: {bot_config.get('purpose', 'Unknown')}")
            print()
            
            load_choice = self.get_user_input("Load this bot? (yes/no)").lower()
            
            if load_choice == 'yes':
                self.current_bot = DeepSeekBot