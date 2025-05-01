import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import file_path_from_module_name, module_name_from_file_path
from constants import CODE_ROOT_FOLDER

def test_file_path_from_module_name():
    """Test the conversion from module name to file path."""
    print("Testing file_path_from_module_name()\n")
    
    test_cases = [
        # Regular module
        ('zeeguu.core.model.user', f"{CODE_ROOT_FOLDER}zeeguu/core/model/user.py"),
        
        # Package (directory)
        ('zeeguu.core.model', f"{CODE_ROOT_FOLDER}zeeguu/core/model{os.path.sep}"),
        
        # Root level module
        ('main', f"{CODE_ROOT_FOLDER}main.py"),
        
        # Root level package
        ('zeeguu', f"{CODE_ROOT_FOLDER}zeeguu{os.path.sep}")
    ]
    
    passed = 0
    failed = 0
    
    for module_name, expected_path in test_cases:
        result = file_path_from_module_name(module_name)
        
        # Normalize paths for comparison
        expected_path = os.path.normpath(expected_path)
        result = os.path.normpath(result)
        
        if result == expected_path:
            passed += 1
            print(f"✓ PASS: '{module_name}' -> '{result}'")
        else:
            failed += 1
            print(f"✗ FAIL: '{module_name}'")
            print(f"  Expected: '{expected_path}'")
            print(f"  Got:      '{result}'")
    
    # Also test round-trip conversion
    print("\nTesting round-trip conversion:")
    for module_name, path in test_cases:
        # Skip packages for round-trip test as they will have / appended
        if module_name.count('.') == 0 and module_name != 'main':
            continue
            
        path_to_test = file_path_from_module_name(module_name)
        round_trip = module_name_from_file_path(path_to_test)
        
        if round_trip == module_name:
            passed += 1
            print(f"✓ PASS: '{module_name}' -> '{path_to_test}' -> '{round_trip}'")
        else:
            failed += 1
            print(f"✗ FAIL: Round-trip for '{module_name}'")
            print(f"  Expected: '{module_name}'")
            print(f"  Got:      '{round_trip}'")
    
    print(f"\nTest Results: {passed} passed, {failed} failed")
    return passed, failed

if __name__ == "__main__":
    test_file_path_from_module_name() 