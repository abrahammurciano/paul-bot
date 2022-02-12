# Development Overview

Requirements: Python, MySQL

### Setup:

- Create postgres database
- Copy .env.example to .env and fill in with your own keys and postgres database url
- Install python version from .python-version
- Create a python venv
  - `python -m venv venv`

### Run server
- Activate venv
  - `source bin/activate`
- Install Requirements
  - `pip install -r reqiurements.txt`
- Run process
  - `python main.py`

### Required Permissions of Discord API Key

- application.commands
- bot
  - Send Messages
  - Read Message History
  - Add Reactions
  - Use Slash Commands