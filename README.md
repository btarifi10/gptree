# 🚀 Flat Repo

**Transform code repositories into LLM-friendly context with style!**  
📦 Flatten directories • 🌳 Generate structure trees • 🧠 AI-ready formatting

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-green.svg)](https://www.python.org/)

## 📥 Installation

```
git clone git+https://github.com/btarifi/gptree.git
cd gptree
pip install .
```

## ✨ Features

- **📄 File Flattening** - Combine entire repos into a single document
- **🧭 Smart Exclusion** - Default ignores for `.git`, `node_modules`, binaries
- **🌳 Structure Visualization** - Generate beautiful directory trees
- **🤖 Gitignore Integration** - Respect existing project rules
- **🔧 Customizable Filters** - Add extra exclusions on the fly
- **💻 CLI Interface** - Developer-friendly command line experience

## 🛠 Usage

### 🔄 Flatten a Repository

```
gptree flatten ./your-project \
    --output ai_context.txt \
    --exclude-dirs tests __pycache__ \
    --exclude-exts .log .tmp \
    --use-gitignore
```

### 🌿 Generate Project Tree

```
gptree python-tree ./your-project -o tree.txt
```

## 🎯 Example Outputs

### Flattened File Format

```
===== BEGIN FILE: src/main.py =====
def hello():
    print("World!")
===== END FILE: src/main.py =====

===== BEGIN FILE: README.md =====
# Awesome Project
...
===== END FILE: README.md =====
```

### Python Tree Visualization

This is the python tree of this repo:

```
gptree
└── gptree
    ├── gptree
    │   ├── cli
    │   │   ├── const DEFAULT_EXCL_DIRS
    │   │   ├── const DEFAULT_EXCL_EXTS
    │   │   ├── method cli
    │   │   ├── method flatten(repo_path, output, exclude_dirs, exclude_exts, use_gitignore)
    │   │   └── method python_tree(repo_path, output)
    │   ├── flattener
    │   │   └── method flatten_repo(repo_path, output_file, excluded_dirs, excluded_extensions) use_gitignore=False
    │   └── tree
    │       ├── const EXCLUDED_DIRS
    │       └── method python_repo_tree(repo_path, output_file)
    └── setup
```

## ⚙️ Configuration

### Default Exclusions
| Type          | Patterns                          |
|---------------|-----------------------------------|
| **Directories** | `.git`, `__pycache__`, `node_modules`, `venv` |
| **Extensions**  | `.png`, `.jpg`, `.zip`, `.pdf`    |

💡 Add to defaults using `--exclude-dirs` and `--exclude-exts` options!

## 🤝 Contributing

We 💖 contributions! Here's how to help:
1. Fork the repository
2. Create a feature branch (`git checkout -b cool-feature`)
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📜 License

MIT Licensed - See [LICENSE](LICENSE) for details.

---
