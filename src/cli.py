import click
from pathlib import Path

from .flattener import flatten_repo
from .tree import python_repo_tree


DEFAULT_EXCL_DIRS = ['.git', '__pycache__', 'node_modules', 'venv']
DEFAULT_EXCL_EXTS = ['.png', '.jpg', '.jpeg', '.gif', '.zip', '.pdf']


@click.group()
def cli():
    """Repository analysis toolkit for LLM context preparation"""
    pass


@click.command()
@click.argument('repo_path', type=click.Path(exists=True, file_okay=False))
@click.option('-o', '--output', default='flattened_repo.txt',
              help='Output file name')
@click.option('--exclude-dirs', multiple=True,
              help='Additional directories to exclude')
@click.option('--exclude-exts', multiple=True,
              help='Additional file extensions to exclude')
@click.option('--use-gitignore', is_flag=True,
              help='Respect .gitignore files')
def flatten(repo_path, output, exclude_dirs, exclude_exts, use_gitignore):
    """Flatten repository files into a single document"""
    excluded_dirs = list(set(DEFAULT_EXCL_DIRS + list(exclude_dirs)))
    excluded_exts = list(set(DEFAULT_EXCL_EXTS + list(exclude_exts)))
    
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    flatten_repo(
        repo_path=Path(repo_path),
        output_file=output,
        excluded_dirs=excluded_dirs,
        excluded_extensions=excluded_exts,
        use_gitignore=use_gitignore
    )
    click.echo(f"✅ Repository flattened to {output}")


@click.command()
@click.argument('repo_path', type=click.Path(exists=True, file_okay=False))
@click.option('-o', '--output', default='flattened_repo.txt',
              help='Output file name')
def python_tree(repo_path, output):
    """Generate Python project tree structure"""
    
    # check that the output file folders exist
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    python_repo_tree(repo_path=repo_path, output_file=output)

    click.echo(f"✅ Python project tree generated to {output}")


cli.add_command(flatten)
cli.add_command(python_tree)


if __name__ == '__main__':
    cli()