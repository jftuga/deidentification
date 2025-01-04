#!/usr/bin/env python3
"""Extract project name from setup.py."""

import ast
import sys
from pathlib import Path

def get_project_name(setup_path='setup.py', default='myproject'):
    """Extract the project name from setup.py using AST parsing."""
    try:
        setup_content = Path(setup_path).read_text()
        module = ast.parse(setup_content, mode='exec')

        # Look for setup() call and find 'name' keyword argument
        for node in module.body:
            if (isinstance(node, ast.Expr) and
                isinstance(node.value, ast.Call) and
                isinstance(node.value.func, ast.Name) and
                node.value.func.id == 'setup'):

                for keyword in node.value.keywords:
                    if keyword.arg == 'name':
                        if isinstance(keyword.value, ast.Constant):
                            return keyword.value.value
                        elif isinstance(keyword.value, ast.Name):
                            # If name is a variable, try to find its definition
                            name_id = keyword.value.id
                            for prior_node in module.body:
                                if (isinstance(prior_node, ast.Assign) and
                                    len(prior_node.targets) == 1 and
                                    isinstance(prior_node.targets[0], ast.Name) and
                                    prior_node.targets[0].id == name_id and
                                    isinstance(prior_node.value, ast.Constant)):
                                    return prior_node.value.value

        return default

    except (FileNotFoundError, SyntaxError, AttributeError):
        return default

if __name__ == '__main__':
    print(get_project_name())