# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains an ASCII art streaming CLI application (`aa_streamer`) that displays random ASCII art from a database file. The application is built in Ruby and streams ASCII art patterns from `asciiartdb-asciiarteu.txt`.

## Commands

### Development
```bash
# Run the application
ruby aa_streamer.rb

# Make executable
chmod +x aa_streamer.rb

# Run tests (if any)
ruby test_*.rb
```

### Usage
```bash
# Stream ASCII art with default 2-second intervals
./aa_streamer.rb

# Stream with custom interval
./aa_streamer.rb --interval 5

# Show help
./aa_streamer.rb --help
```

## Architecture

### Core Components
- `aa_streamer.rb`: Main CLI application entry point
- ASCII art parser: Extracts art patterns from the database file
- Streaming engine: Handles timed display and random selection
- CLI interface: Command-line argument parsing and user interaction

### Data Format

The ASCII art database (`asciiartdb-asciiarteu.txt`) follows this format:
1. Pattern name/description
2. Dimensions in format `{width}x{height}`
3. Category (typically "ascii-one-line")
4. The actual ASCII art pattern
5. Empty lines as separators

### File Structure
- `asciiartdb-asciiarteu.txt`: ASCII art database (5.6MB, 141k+ lines)
- `aa_streamer.rb`: Main CLI application
- Database contains ASCII art from asciiart.eu

## Development Notes

- The database file is large - use efficient parsing methods
- Handle special characters in ASCII art properly
- Implement graceful interruption (Ctrl+C) handling
- Clear screen between art displays for better user experience