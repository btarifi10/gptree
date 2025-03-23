import os
import argparse
from pathlib import Path
from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern


def flatten_repo(repo_path, output_file, excluded_dirs, excluded_extensions, use_gitignore=False):
    """
    Flattens a repository structure into a single text file with file paths as headers.
    """
    repo_path = Path(repo_path).resolve()
    spec = None

    if use_gitignore:
        spec = PathSpec.from_lines(GitWildMatchPattern, lines=[
            line.strip() for line in open(repo_path / '.gitignore').readlines()
        ])

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(repo_path):
            current_dir = Path(root)
            
            # Filter directories
            dirs[:] = [
                d for d in dirs
                if (d not in excluded_dirs) and 
                (not use_gitignore or not spec.match_file((current_dir.relative_to(repo_path) / d).as_posix()))
            ]

            for file in files:
                file_path = current_dir / file
                relative_path = file_path.relative_to(repo_path)

                # Skip excluded extensions
                if file_path.suffix in excluded_extensions or file_path.name in excluded_extensions:
                    continue

                # Skip gitignored files
                if use_gitignore and spec.match_file(relative_path.as_posix()):
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        contents = infile.read()
                except UnicodeDecodeError:
                    continue  # Skip binary files
                except Exception as e:
                    print(f"Error reading {file_path}: {str(e)}")
                    continue

                # Write to output
                outfile.write(f"===== BEGIN FILE: {relative_path} =====\n")
                outfile.write(contents)
                outfile.write(f"\n===== END FILE: {relative_path} =====\n\n")