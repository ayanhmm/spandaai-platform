#!/usr/bin/env python3

"""
Spanda CLI: A lightweight wrapper around Docker Compose commands
"""

import subprocess
from pathlib import Path
from typing import Optional

import typer

app = typer.Typer()
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"
COMPOSE_FILE = BASE_DIR / "master-compose.yml"


def run_compose_command(*args: str):
    """Run docker compose commands with the env and master-compose file"""
    command = [
        "docker",
        "compose",
        "--env-file", str(ENV_FILE),
        "-f", str(COMPOSE_FILE),
        *args
    ]
    typer.echo(f"🔧 Running: {' '.join(command)}")
    subprocess.run(command, check=True)


@app.command()
def dry_run():
    """Validates the master Compose file and shows active profiles"""
    run_compose_command("config", "--profiles")


@app.command()
def up(profile: Optional[str] = typer.Option(None, help="Start a specific profile only")):
    """Starts the Docker Compose services"""
    args = ["--profile", profile] if profile else []
    run_compose_command("up", "-d", *args)


@app.command()
def down():
    """Stops and removes all Docker Compose services"""
    run_compose_command("down")


@app.command()
def logs(service: Optional[str] = typer.Argument(None, help="Service name to tail logs for")):
    """Tails logs of a specific service or all if none is provided"""
    args = ["logs", "-f"]
    if service:
        args.append(service)
    run_compose_command(*args)


@app.command()
def status():
    """Displays the status of all containers"""
    run_compose_command("ps")


if __name__ == "__main__":
    app()
