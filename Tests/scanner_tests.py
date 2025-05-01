import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Model.common import file_path, module_name_from_file_path
from Model.imports_helper import import_from_line, imports_from_file


def test_file_path():
    assert 'zeeguu.core.model.user' == module_name_from_file_path(file_path('zeeguu/core/model/user.py'))

def test_imports_from_file():
    print("test_imports_from_file\n")
    """Test extracting imports from entire files."""
    
    # Test with a simple file
    imports = imports_from_file(file_path('zeeguu/api/app.py'))
    
    # Import content of zeeguu/api/app.py
    """
    from zeeguu.config.loader import load_configuration_or_abort
    from flask_cors import CORS
    from flask import Flask
    import time
    import os
    import re
    import zeeguu

    from zeeguu.logging import warning

    # apimux is quite noisy; supress it's output
    import logging
    from apimux.log import logger

    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    from zeeguu.core.model import db
    from .endpoints import api
    
    """
     
    expected_imports = [
        'zeeguu.config.loader',
        'flask_cors',
        'flask',
        'time', 
        'os',
        're',
        'zeeguu',
        'zeeguu.logging',
        'logging',
        'apimux.log',
        'sentry_sdk',
        'sentry_sdk.integrations.flask',
        'zeeguu.core.model',
        'zeeguu.api.endpoints'
    ]
    
    passed = 0
    failed = 0
    
    print("Checking for expected imports:")
    # Check each import was found
    for expected in expected_imports:
        if expected in imports:
            passed += 1
            print(f"✓ PASS: Import '{expected}' was found")
        else:
            failed += 1
            print(f"✗ FAIL: Import '{expected}' was not found")
    
    # Also check for unexpected imports
    unexpected = [imp for imp in imports if imp not in expected_imports]
    if unexpected:
        print("\nUnexpected imports found:")
        for imp in unexpected:
            print(f"  - {imp}")
    
    print(f"\nTest Results: {passed} passed, {failed} failed out of {len(expected_imports)} expected imports")
    return passed, failed

def test_imports_from_file_old():
    print("test_imports_from_file\n")
    """Test extracting imports from entire files."""
    
    # Test with a simple file
    simple_imports = imports_from_file(file_path('zeeguu/core/model/user.py'))
    assert len(simple_imports) > 0, "Should find imports in user.py"
    
    # Test different files have different imports
    bookmark_imports = imports_from_file(file_path('zeeguu/core/model/bookmark.py'))
    unique_code_imports = imports_from_file(file_path('zeeguu/core/model/unique_code.py'))
    assert unique_code_imports != bookmark_imports, "Different files should have different imports"
    
    # Test with known content including relative imports
    with open('test_imports.py', 'w') as f:
        f.write('''
import os
from datetime import datetime
from zeeguu.core import model
import zeeguu.core.model, tools.helper
import json as j
from typing import List, Optional
from . import local_module
from .subpackage import something
from .. import parent_module
from ..sibling import other
''')
    # import os -> os
    # from datetime import datetime -> datetime
    # from zeeguu.core import model -> zeeguu.core
    # import zeeguu.core.model, tools.helper -> zeeguu.core.model, tools.helper
    # import json as j -> json
    # from typing import List, Optional -> typing
    # from . import local_module -> local_module
    # from .subpackage import something -> subpackage
    # from .. import parent_module -> parent_module



    test_imports = imports_from_file('test_imports.py')
    print(f"Found imports: {test_imports}")
    
    # Since test_imports.py is at root level, the relative imports should resolve to:
    # from . import local_module -> local_module
    # from .subpackage import something -> subpackage
    # from .. import parent_module -> parent_module
    # from ..sibling import other -> sibling
    
    expected_imports = [
        'os',
        'tools.helper',
        'zeeguu.core.model',
        'datetime', 
        'zeeguu.core',
        'json',
        'typing',
        'subpackage',
        'parent_module',
        'sibling'
    ]
    
    # Check each import was found
    for expected in expected_imports:
        assert expected in test_imports, f"Missing import: {expected}"
    
    # Test relative imports in a nested location
    os.makedirs('test_package/submodule', exist_ok=True)
    with open('test_package/submodule/module.py', 'w') as f:
        f.write('''
from . import sibling
from .. import parent
from .nested import deep
''')
    
    nested_imports = imports_from_file('test_package/submodule/module.py')
    print(f"\nNested imports: {nested_imports}")
    
    # These should resolve to:
    # from . import sibling -> test_package.submodule
    # from .. import parent -> test_package
    # from .nested import deep -> test_package.submodule.nested
    
    expected_nested = [
        'test_package.submodule',
        'test_package',
        'test_package.submodule.nested'
    ]
    
    for expected in expected_nested:
        assert expected in nested_imports, f"Missing nested import: {expected}"
    
    # Clean up test files
    import shutil
    os.remove('test_imports.py')
    shutil.rmtree('test_package')

def test_file_path():
    print("test_file_path\n")
    """Test module name extraction from file paths."""
    test_cases = [
        # Basic module
        ('zeeguu/core/model/user.py', 'zeeguu.core.model.user'),
        
        # With __init__.py
        ('zeeguu/core/model/__init__.py', 'zeeguu.core.model'),
        
        # Nested packages
        ('zeeguu/core/model/utils/helper.py', 'zeeguu.core.model.utils.helper'),
        
        # Root level file
        ('main.py', 'main'),
        
        # With underscores and numbers
        ('zeeguu/core/model/user_2_profile.py', 'zeeguu.core.model.user_2_profile'),
    ]
    
    for file_path, expected in test_cases:
        result = module_name_from_file_path(file_path)
        assert result == expected, f"Expected {expected}, got {result} for {file_path}"

def test_resolve_relative_import():
    print("test_resolve_relative_import\n")
    """Test scanning zeeguu/api/app.py for imports"""

    expected_imports = {
        'zeeguu.config.loader',
        'flask_cors',
        'flask',
        'time',
        'os',
        're',
        'zeeguu',
        'zeeguu.logging',
        'logging',
        'apimux.log',
        'sentry_sdk',
        'sentry_sdk.integrations.flask',
        'zeeguu.core.model',
        'zeeguu.api.endpoints'
    }
    
    # Get actual imports from the file
    actual_imports = set(imports_from_file('repo_for_analysis/zeeguu/api/app.py'))
    
    print("\nExpected imports:")
    for imp in sorted(expected_imports):
        print(f"  {imp}")
        
    print("\nActual imports found:")
    for imp in sorted(actual_imports):
        print(f"  {imp}")
        
    print("\nMissing imports:")
    for imp in expected_imports - actual_imports:
        print(f"  {imp}")
        
    print("\nExtra imports found:")
    for imp in actual_imports - expected_imports:
        print(f"  {imp}")
    
    assert actual_imports == expected_imports, "Imports don't match expected set"

def test_import_from_line():
    print("Testing import_from_line()\n")
    test_cases = [
        # Basic imports
        ("import os", ["os"]),
        ("import sys", ["sys"]),
        
        # Multiple imports on one line
        ("import os, sys", ["os", "sys"]),
        ("import sys, os", ["sys", "os"]),
        
        # Imports with 'as'
        ("import numpy as np", ["numpy"]),
        ("import pandas as pd", ["pandas"]),
        
        # From imports
        ("from os import path", ["os"]),
        ("from sys import exit", ["sys"]),
        ("from . import views", ["."]),
        ("from .views import main", [".views"]),
        ("from ..models import user", ["..models"]),
        
        # From imports with multiple items
        ("from os import path, walk", ["os"]),
        
        # From imports with 'as'
        ("from numpy import array as arr", ["numpy"]),
        
        # Nested package imports
        ("from os.path import join", ["os.path"]),
        ("import xml.etree.ElementTree", ["xml.etree.ElementTree"]),
        
        # Parenthesized imports
        ("from os import (path, walk)", ["os"]),
        
        # Imports with whitespace
        ("   import os   ", ["os"]),
        ("   from   os   import   path   ", ["os"]),
        
        # Invalid or empty lines
        ("# import os", []),
        ("", []),
        ("def import_something():", []),
        ("'import os'", []),
    ]
    
    passed = 0
    failed = 0
    
    for test_input, expected in test_cases:
        result = import_from_line(test_input)
        if result == expected:
            passed += 1
            print(f"✓ PASS: '{test_input}' -> {result}")
        else:
            failed += 1
            print(f"✗ FAIL: '{test_input}'")
            print(f"  Expected: {expected}")
            print(f"  Got:      {result}")
    
    print(f"\nTest Results: {passed} passed, {failed} failed")
    return passed, failed

def test_parent_module_extraction():
    """Test the get_parent_module function with various module name formats."""
    from Model.common import get_parent_module
    import io
    import sys
    
    print("Testing parent_module_extraction()\n")
    
    test_cases = [
        ("app", ""),
        ("app.components", "app"),
        ("app.components.ui.buttons", "app"),
        ("os.path", "os"),
        ("api.v1.users", "api")
    ]
    
    passed = 0
    failed = 0
    
    for module_name, expected_parent in test_cases:
        # Redirect stdout to capture the output
        stdout_backup = sys.stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        # Call the function
        get_parent_module(module_name)
        
        # Restore stdout
        sys.stdout = stdout_backup
        output = captured_output.getvalue()
        
        # Check if the output contains the expected module and parent
        contains_module = f"module: {module_name}" in output
        contains_parent = f"parent: {expected_parent}" in output
        
        if contains_module and contains_parent:
            passed += 1
            print(f"✓ PASS: '{module_name}' -> parent: '{expected_parent}'")
        else:
            failed += 1
            print(f"✗ FAIL: '{module_name}'")
            print(f"  Expected output to contain:")
            print(f"    - 'module: {module_name}'")
            print(f"    - 'parent: {expected_parent}'")
            print(f"  Got output: {output.strip()}")
    
    print(f"\nTest Results: {passed} passed, {failed} failed")
    return passed, failed

if __name__ == "__main__":
    # test_import_from_line()
    # test_resolve_relative_import()
    test_imports_from_file()
    # test_file_path()
    # test_parent_module_extraction()