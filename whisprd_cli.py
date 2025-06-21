#!/usr/bin/env python3
"""
Command-line interface for the whisprd system.
"""

import sys
import signal
import argparse
import logging
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm

from whisprd.dictation_engine import DictationEngine

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

console = Console()


class WhisprdCLI:
    """Command-line interface for the whisprd system."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.engine = None
        self.console = console
        self.running = False
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle system signals."""
        console.print("\n[yellow]Shutting down...[/yellow]")
        self.stop()
        sys.exit(0)
    
    def start(self, config_path: Optional[str] = None, verbose: bool = False):
        """Start the whisprd system."""
        try:
            # Set log level
            if verbose:
                logging.getLogger().setLevel(logging.DEBUG)
            
            # Initialize engine
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Initializing whisprd engine...", total=None)
                
                self.engine = DictationEngine(config_path)
                
                # Set up callbacks
                self.engine.set_status_callback(self._on_status_change)
                self.engine.set_transcription_callback(self._on_transcription)
                
                progress.update(task, description="Starting engine...")
                self.engine.start()
                
                progress.update(task, description="Ready!")
            
            self.running = True
            self._show_welcome()
            self._interactive_loop()
            
        except Exception as e:
            console.print(f"[red]Error starting whisprd system: {e}[/red]")
            sys.exit(1)
    
    def stop(self):
        """Stop the whisprd system."""
        if self.engine and self.running:
            self.engine.stop()
            self.running = False
            console.print("[green]Whisprd system stopped.[/green]")
    
    def _show_welcome(self):
        """Show welcome message and instructions."""
        welcome_text = """
[bold blue]Real-time Whisper Dictation System[/bold blue]

[bold]Controls:[/bold]
• Press [bold]Ctrl+Alt+D[/bold] to toggle dictation on/off
• Say "computer" to activate command mode
• Say "stop dictation" to stop dictation
• Say "start dictation" to start dictation

[bold]Voice Commands:[/bold]
• "new line" - Insert newline
• "backspace" - Delete last character
• "period" - Insert period
• "comma" - Insert comma
• "question mark" - Insert question mark
• And many more...

[bold]Status:[/bold] Press Ctrl+Alt+D to start dictating
        """
        
        console.print(Panel(welcome_text, title="Welcome", border_style="blue"))
    
    def _interactive_loop(self):
        """Main interactive loop."""
        while self.running:
            try:
                # Show status
                self._show_status()
                
                # Wait for user input
                command = Prompt.ask(
                    "\n[bold]Command[/bold] (help/status/commands/quit)",
                    default="status"
                )
                
                if command.lower() in ['q', 'quit', 'exit']:
                    break
                elif command.lower() in ['h', 'help']:
                    self._show_help()
                elif command.lower() in ['s', 'status']:
                    self._show_detailed_status()
                elif command.lower() in ['c', 'commands']:
                    self._show_commands()
                elif command.lower() in ['r', 'reload']:
                    self._reload_config()
                elif command.lower() in ['t', 'toggle']:
                    self._toggle_dictation()
                else:
                    console.print(f"[yellow]Unknown command: {command}[/yellow]")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
    
    def _show_status(self):
        """Show current status."""
        if not self.engine:
            return
        
        status = self.engine.get_status()
        
        # Create status table
        table = Table(title="Whisprd Status")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Engine Running", "✅" if status['is_running'] else "❌")
        table.add_row("Dictation Active", "🎤" if status['is_dictating'] else "🔇")
        table.add_row("Hotkey", "+".join(status['hotkey']) if status['hotkey'] else "None")
        table.add_row("Audio Queue", str(status['audio_queue_size']))
        table.add_row("Transcription Queue", str(status['transcription_queue_size']))
        
        if status['stats']['start_time']:
            uptime = status['stats']['start_time']
            table.add_row("Started", uptime.strftime("%H:%M:%S"))
        
        table.add_row("Total Transcriptions", str(status['stats']['total_transcriptions']))
        table.add_row("Total Commands", str(status['stats']['total_commands']))
        table.add_row("Total Characters", str(status['stats']['total_characters']))
        table.add_row("Errors", str(status['stats']['errors']))
        
        console.print(table)
    
    def _show_detailed_status(self):
        """Show detailed status information."""
        if not self.engine:
            return
        
        status = self.engine.get_status()
        
        # Create detailed status panel
        status_text = f"""
[bold]Engine Status:[/bold]
• Running: {'✅' if status['is_running'] else '❌'}
• Dictating: {'🎤' if status['is_dictating'] else '🔇'}

[bold]Configuration:[/bold]
• Hotkey: {'+'.join(status['hotkey']) if status['hotkey'] else 'None'}
• Audio Queue Size: {status['audio_queue_size']}
• Transcription Queue Size: {status['transcription_queue_size']}

[bold]Statistics:[/bold]
• Start Time: {status['stats']['start_time'].strftime('%Y-%m-%d %H:%M:%S') if status['stats']['start_time'] else 'N/A'}
• Total Transcriptions: {status['stats']['total_transcriptions']}
• Total Commands: {status['stats']['total_commands']}
• Total Characters: {status['stats']['total_characters']}
• Errors: {status['stats']['errors']}
        """
        
        console.print(Panel(status_text, title="Detailed Status", border_style="green"))
    
    def _show_commands(self):
        """Show available voice commands."""
        if not self.engine:
            return
        
        commands = self.engine.get_commands()
        
        if not commands:
            console.print("[yellow]No commands configured.[/yellow]")
            return
        
        # Create commands table
        table = Table(title="Available Voice Commands")
        table.add_column("Command", style="cyan")
        table.add_column("Action", style="white")
        
        for command, action in commands.items():
            table.add_row(command, action)
        
        console.print(table)
    
    def _show_help(self):
        """Show help information."""
        help_text = """
[bold]Available Commands:[/bold]
• [cyan]help[/cyan] (h) - Show this help
• [cyan]status[/cyan] (s) - Show current status
• [cyan]commands[/cyan] (c) - Show voice commands
• [cyan]reload[/cyan] (r) - Reload configuration
• [cyan]toggle[/cyan] (t) - Toggle dictation
• [cyan]quit[/cyan] (q) - Exit the program

[bold]Voice Controls:[/bold]
• Press [bold]Ctrl+Alt+D[/bold] to toggle dictation
• Say "computer" to activate command mode
• Say "stop dictation" to stop dictation
• Say "start dictation" to start dictation

[bold]Configuration:[/bold]
• Edit config.yaml to customize settings
• Add custom voice commands
• Adjust audio and Whisper settings
        """
        
        console.print(Panel(help_text, title="Help", border_style="blue"))
    
    def _reload_config(self):
        """Reload configuration."""
        if not self.engine:
            return
        
        try:
            self.engine.reload_config()
            console.print("[green]Configuration reloaded successfully.[/green]")
        except Exception as e:
            console.print(f"[red]Error reloading configuration: {e}[/red]")
    
    def _toggle_dictation(self):
        """Toggle dictation on/off."""
        if not self.engine:
            return
        
        if self.engine.is_dictating:
            self.engine.stop_dictation()
            console.print("[yellow]Dictation stopped.[/yellow]")
        else:
            self.engine.start_dictation()
            console.print("[green]Dictation started.[/green]")
    
    def _on_status_change(self, status: str):
        """Handle status change callback."""
        status_icons = {
            'started': '🚀',
            'stopped': '🛑',
            'dictating': '🎤',
            'idle': '🔇'
        }
        
        icon = status_icons.get(status, '❓')
        console.print(f"{icon} Status: {status.title()}")
    
    def _on_transcription(self, original_text: str, clean_text: str, matches):
        """Handle transcription callback."""
        if original_text:
            console.print(f"[dim]🎤 {original_text}[/dim]")
        
        if clean_text and clean_text != original_text:
            console.print(f"[green]✍️  {clean_text}[/green]")
        
        if matches:
            commands = [f"{m.command}->{m.action}" for m in matches]
            console.print(f"[yellow]⚡ Commands: {', '.join(commands)}[/yellow]")


@click.command()
@click.option('--config', '-c', 'config_path', help='Path to configuration file')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--daemon', '-d', is_flag=True, help='Run in daemon mode (no interactive interface)')
def main(config_path: Optional[str], verbose: bool, daemon: bool):
    """Real-time Whisper-powered dictation system for Linux."""
    
    if daemon:
        # Daemon mode - minimal output
        logging.basicConfig(level=logging.INFO if not verbose else logging.DEBUG)
        
        try:
            engine = DictationEngine(config_path)
            engine.start()
            
            # Keep running until interrupted
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            finally:
                engine.stop()
                
        except Exception as e:
            logging.error(f"Error in daemon mode: {e}")
            sys.exit(1)
    else:
        # Interactive mode
        cli = WhisprdCLI()
        cli.start(config_path, verbose)


if __name__ == '__main__':
    main() 