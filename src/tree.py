import os
import ast

EXCLUDED_DIRS = ['__pycache__', 'build', 'dist', 'venv', '.git', '.github']

def _parse_repo(repo_path):
    repo_name = os.path.basename(os.path.abspath(repo_path))
    structure = {'_children': {}, '_exports': {'constants': [], 'functions': [], 'classes': []}, '_docstring': None}

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

            module_docstring = None
            for node in tree.body:
                if isinstance(node, ast.Expr):
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        module_docstring = node.value.value
                        break
                    elif isinstance(node.value, ast.Str):  # For Python <3.8
                        module_docstring = node.value.s
                        break

            exports = _get_exports(tree)

            current = structure
            for part in module_name_parts:
                if part not in current['_children']:
                    current['_children'][part] = {'_children': {}, '_exports': {'constants': [], 'functions': [], 'classes': []}, '_docstring': None}
                current = current['_children'][part]
            current['_exports'] = exports
            current['_docstring'] = module_docstring

    return repo_name, structure

def _get_function_docstring(node):
    docstring = None
    for body_node in node.body:
        if isinstance(body_node, ast.Expr):
            if isinstance(body_node.value, ast.Constant) and isinstance(body_node.value.value, str):
                docstring = body_node.value.value
                break
            elif isinstance(body_node.value, ast.Str):  # For Python <3.8
                docstring = body_node.value.s
                break
    return docstring

def _get_class_docstring(node):
    docstring = None
    for body_node in node.body:
        if isinstance(body_node, ast.Expr):
            if isinstance(body_node.value, ast.Constant) and isinstance(body_node.value.value, str):
                docstring = body_node.value.value
                break
            elif isinstance(body_node.value, ast.Str):
                docstring = body_node.value.s
                break
    return docstring

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
                docstring = _get_function_docstring(node)
                exports['functions'].append({'sig': sig, 'docstring': docstring})
        elif isinstance(node, ast.ClassDef):
            if (all_names and node.name in all_names) or (not all_names and not node.name.startswith('_')):
                methods = []
                for class_body_node in node.body:
                    if isinstance(class_body_node, ast.FunctionDef):
                        method_name = class_body_node.name
                        if not method_name.startswith('_'):
                            try:
                                method_sig = f"{method_name}({ast.unparse(class_body_node.args)})"
                            except AttributeError:
                                method_sig = f"{method_name}()"
                            method_docstring = _get_function_docstring(class_body_node)
                            methods.append({'sig': method_sig, 'docstring': method_docstring})
                
                try:
                    bases = [ast.unparse(base) for base in node.bases]
                except AttributeError:
                    bases = []
                
                class_docstring = _get_class_docstring(node)
                class_entry = {
                    'name': node.name,
                    'bases': bases,
                    'methods': methods,
                    'docstring': class_docstring
                }
                exports['classes'].append(class_entry)
    return exports

def _get_tree(repo_name, structure, include_docstrings=True):
    lines = [f"{repo_name}"]
    if include_docstrings and structure.get('_docstring'):
        first_line = structure['_docstring'].strip().split('\n')[0]
        lines[0] += f"  # {first_line}"
    
    def recurse(node, prefix, is_last, result, include_ds):
        constants = sorted(node['_exports']['constants'], key=lambda x: x.lower())
        functions = sorted(node['_exports']['functions'], key=lambda x: x['sig'].lower())
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
                func_info = item[1]
                line += f"method {func_info['sig']}"
                if include_ds and func_info['docstring']:
                    first_line = func_info['docstring'].strip().split('\n')[0]
                    line += f"  # {first_line}"
            elif item[0] == 'class':
                class_info = item[1]
                bases_str = f"({', '.join(class_info['bases'])})" if class_info['bases'] else ""
                line += f"class {class_info['name']}{bases_str}"
                if include_ds and class_info['docstring']:
                    first_line = class_info['docstring'].strip().split('\n')[0]
                    line += f"  # {first_line}"
            else:
                module_name, child_node = item[1]
                line += module_name
                if include_ds and child_node.get('_docstring'):
                    first_line = child_node['_docstring'].strip().split('\n')[0]
                    line += f"  # {first_line}"
            
            result.append(line)
            
            if item[0] == 'class':
                class_info = item[1]
                method_prefix = prefix + ('    ' if is_last_item else '│   ') + '    '
                for mi, method in enumerate(class_info['methods']):
                    is_last_method = mi == len(class_info['methods']) - 1
                    method_connector = '└── ' if is_last_method else '├── '
                    method_line = f"{method_prefix}{method_connector}method {method['sig']}"
                    if include_ds and method['docstring']:
                        first_line = method['docstring'].strip().split('\n')[0]
                        method_line += f"  # {first_line}"
                    result.append(method_line)
            elif item[0] == 'module':
                extension = '    ' if is_last_item else '│   '
                new_prefix = prefix + extension
                recurse(item[1][1], new_prefix, is_last_item, result, include_ds)

    recurse(structure, '', True, lines, include_docstrings)
    return lines

def python_repo_tree(repo_path, output_file, include_docstrings=False):
    repo_name, structure = _parse_repo(repo_path)
    tree = _get_tree(repo_name, structure, include_docstrings)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(tree))