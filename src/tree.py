import os
import ast


EXCLUDED_DIRS = ['__pycache__', 'build', 'dist', 'venv', '.git', '.github']

def _parse_repo(repo_path):
    repo_name = os.path.basename(os.path.abspath(repo_path))
    structure = {'_children': {}, '_exports': {'constants': [], 'functions': [], 'classes': []}}

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        rel_path = os.path.relpath(root, repo_path)
        current_parts = rel_path.split(os.sep) if rel_path != '.' else []

        for file in files:
            if not file.endswith('.py'):
                continue

            file_path = os.path.join(root, file)
            module_parts = current_parts.copy()

            if file == '__init__.py':
                module_name_parts = [repo_name] + ([] if rel_path == '.' else current_parts)
            else:
                module_name_parts = [repo_name] + current_parts + [file[:-3]]

            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    tree = ast.parse(f.read(), filename=file_path)
                except:
                    continue

            exports = _get_exports(tree)

            current = structure
            for part in module_name_parts:
                if part not in current['_children']:
                    current['_children'][part] = {'_children': {}, '_exports': {'constants': [], 'functions': [], 'classes': []}}
                current = current['_children'][part]
            current['_exports'] = exports

    return repo_name, structure

def _get_exports(tree):
    all_names = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == '__all__':
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant):
                                all_names.append(elt.s)
                    break

    exports = {'constants': [], 'functions': [], 'classes': []}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id != '__all__':
                    if (all_names and target.id in all_names) or (not all_names and not target.id.startswith('_')):
                        exports['constants'].append(target.id)
        elif isinstance(node, ast.FunctionDef):
            if (all_names and node.name in all_names) or (not all_names and not node.name.startswith('_')):
                try:
                    sig = f"{node.name}({ast.unparse(node.args)})"
                except AttributeError:
                    sig = f"{node.name}()"
                exports['functions'].append(sig)
        elif isinstance(node, ast.ClassDef):
            if (all_names and node.name in all_names) or (not all_names and not node.name.startswith('_')):
                # Collect class methods
                methods = []
                for class_body_node in node.body:
                    if isinstance(class_body_node, ast.FunctionDef):
                        method_name = class_body_node.name
                        if not method_name.startswith('_'):
                            try:
                                method_sig = f"{method_name}({ast.unparse(class_body_node.args)})"
                            except AttributeError:
                                method_sig = f"{method_name}()"
                            methods.append(method_sig)
                
                # Format class signature
                try:
                    bases = [ast.unparse(base) for base in node.bases]
                except AttributeError:
                    bases = []
                
                class_entry = {
                    'name': node.name,
                    'bases': bases,
                    'methods': methods
                }
                exports['classes'].append(class_entry)
    return exports

def _get_tree(repo_name, structure):
    lines = [f"{repo_name}"]
    
    def recurse(node, prefix, is_last, result):
        constants = sorted(node['_exports']['constants'], key=lambda x: x.lower())
        functions = sorted(node['_exports']['functions'], key=lambda x: x.lower())
        classes = sorted(node['_exports']['classes'], key=lambda x: x['name'].lower())
        children = sorted(node['_children'].items(), key=lambda x: x[0].lower())
        
        all_items = []
        all_items.extend([('constant', v) for v in constants])
        all_items.extend([('function', f) for f in functions])
        all_items.extend([('class', c) for c in classes])
        all_items.extend([('module', (name, child)) for name, child in children])

        for i, item in enumerate(all_items):
            is_last_item = i == len(all_items) - 1
            connector = '└── ' if is_last_item else '├── '
            
            line = prefix + connector
            if item[0] == 'constant':
                line += f"const {item[1]}"
            elif item[0] == 'function':
                line += f"method {item[1]}"
            elif item[0] == 'class':
                class_info = item[1]
                bases_str = f"({', '.join(class_info['bases'])})" if class_info['bases'] else ""
                line += f"class {class_info['name']}{bases_str}"
            else:
                line += f"{item[1][0]}"
            
            result.append(line)
            
            if item[0] == 'class':
                # Add class methods
                class_info = item[1]
                method_prefix = prefix + ('    ' if is_last_item else '│   ') + '    '
                for mi, method in enumerate(class_info['methods']):
                    is_last_method = mi == len(class_info['methods']) - 1
                    method_connector = '└── ' if is_last_method else '├── '
                    method_line = f"{method_prefix}{method_connector}method {method}"
                    result.append(method_line)
            elif item[0] == 'module':
                extension = '    ' if is_last_item else '│   '
                new_prefix = prefix + extension
                recurse(item[1][1], new_prefix, is_last_item, result)

    recurse(structure, '', True, lines)
    return lines

def python_repo_tree(repo_path, output_file):
    repo_name, structure = _parse_repo(repo_path)
    tree = _get_tree(repo_name, structure)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(tree))