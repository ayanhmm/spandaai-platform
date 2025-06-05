"""CLI tool to manage Spanda Foundation Docker Compose setup."""

import subprocess
from pathlib import Path
import typer

app = typer.Typer()

@app.command()
def dry_run():
    """Perform a dry run of Docker Compose to validate configuration."""
    typer.echo("🔧 Running: docker compose --env-file .env -f master-compose.yml config")
    subprocess.run(
        ["docker", "compose", "--env-file", ".env", "-f", "master-compose.yml", "config"],
        check=True
    )

@app.command()
def validate_env():
    """Check if .env file exists and display contents."""
    env_path = Path(".env")
    if env_path.exists():
        typer.echo("✅ .env file found. Contents:")
        with open(env_path, encoding="utf-8") as f:
            typer.echo(f.read())
    else:
        typer.echo("❌ .env file is missing.")


if __name__ == "__main__":
    app()
