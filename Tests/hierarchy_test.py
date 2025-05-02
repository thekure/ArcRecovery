import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Model.graph_builder import get_module_hierarchy

def test_module_hierarchy():
    """Test the hierarchical organization of modules."""
    print("Testing ModuleHierarchy...\n")
    
    # Get the hierarchy
    hierarchy = get_module_hierarchy()
    
    # Test root level view
    root_view = hierarchy.get_level_view('')
    print(f"Root level packages: {sorted(root_view['packages'])}")
    print(f"Root level modules: {[m.name for m in root_view['modules']]}")
    
    # Test dependencies at root level
    root_deps = hierarchy.get_aggregated_dependencies('')
    print("\nRoot level dependencies:")
    for (source, target), weight in sorted(root_deps.items(), key=lambda x: x[1], reverse=True):
        print(f"  {source} -> {target}: {weight}")
    
    # Test a specific package level
    if 'zeeguu' in root_view['packages']:
        print("\nZeeguu package level:")
        zeeguu_view = hierarchy.get_level_view('zeeguu')
        print(f"  Packages: {sorted(zeeguu_view['packages'])}")
        print(f"  Modules: {[m.name for m in zeeguu_view['modules']]}")
        
        # Test dependencies at zeeguu level
        zeeguu_deps = hierarchy.get_aggregated_dependencies('zeeguu')
        print("\n  Dependencies:")
        for (source, target), weight in sorted(zeeguu_deps.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    {source} -> {target}: {weight}")
    
    # Test nested level
    if 'zeeguu' in root_view['packages'] and 'core' in hierarchy.get_level_view('zeeguu')['packages']:
        print("\nZeeguu.core package level:")
        zeeguu_core_view = hierarchy.get_level_view('zeeguu.core')
        print(f"  Packages: {sorted(zeeguu_core_view['packages'])}")
        
        # Debug: Print first 5 module names to see what's included
        modules_list = [m.name for m in zeeguu_core_view['modules']]
        print(f"  Module count: {len(zeeguu_core_view['modules'])}")
        print(f"  First 5 modules: {sorted(modules_list)[:5]}")
        
        # Test dependencies at zeeguu.core level
        zeeguu_core_deps = hierarchy.get_aggregated_dependencies('zeeguu.core')
        print("\n  Dependencies (top 5):")
        for (source, target), weight in sorted(zeeguu_core_deps.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    {source} -> {target}: {weight}")
    
    # Test module info
    print("\nDetailed module info for a sample module:")
    # Find a module to display
    sample_module = None
    for module in root_view['modules']:
        if len(module.dependencies) > 0:
            sample_module = module.name
            break
    
    if sample_module:
        module_info = hierarchy.get_module_info(sample_module)
        print(f"  Module: {module_info['name']}")
        print(f"  Is package: {module_info['is_package']}")
        print(f"  Depth: {module_info['depth']}")
        print(f"  Dependencies: {module_info['dependency_count']}")
        print(f"  First few dependencies: {module_info['dependencies'][:3]}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_module_hierarchy() 
    