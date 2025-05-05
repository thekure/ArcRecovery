import os
import shutil
import re
import requests

from constants import ASSETS_FOLDER

def ensure_pyvis_assets_available():
    """
    Extract required Pyvis assets and store them in the assets folder.
    This ensures we have local copies of all necessary JS and CSS files.
    """
    print(f"Preparing assets in: {os.path.abspath(ASSETS_FOLDER)}")
    os.makedirs(ASSETS_FOLDER, exist_ok=True)
    
    # Required JS libraries with their CDN URLs
    js_files = {
        "vis-network.min.js": "https://cdn.jsdelivr.net/npm/vis-network@9.1.2/dist/vis-network.min.js",
        "vis.min.js": "https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js",
        "vis.js": "https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.js",
        "utils.js": "https://cdn.jsdelivr.net/npm/vis-network@9.1.2/dist/dist/utils.js",
        "bootstrap.bundle.min.js": "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"
    }
    
    # Required CSS files with their CDN URLs
    css_files = {
        "vis-network.min.css": "https://cdn.jsdelivr.net/npm/vis-network@9.1.2/dist/dist/vis-network.min.css",
        "vis.min.css": "https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.css",
        "bootstrap.min.css": "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
    }
    
    downloaded_files = []
    
    # Try to copy from pyvis package if available
    try:
        # Try to find local pyvis resources first
        import pyvis
        pyvis_path = os.path.dirname(pyvis.__file__)
        templates_path = os.path.join(pyvis_path, 'templates')
        
        if os.path.exists(templates_path):
            print(f"Found pyvis templates at {templates_path}")
            # Try to copy local files first
            static_js_path = os.path.join(templates_path, 'static', 'js')
            static_css_path = os.path.join(templates_path, 'static', 'css')
            
            if os.path.exists(static_js_path):
                for file_name in os.listdir(static_js_path):
                    if file_name.endswith('.js'):
                        src_file = os.path.join(static_js_path, file_name)
                        dst_file = os.path.join(ASSETS_FOLDER, file_name)
                        shutil.copy2(src_file, dst_file)
                        downloaded_files.append(file_name)
                        print(f"Copied local JS file: {file_name}")
                        
            if os.path.exists(static_css_path):
                for file_name in os.listdir(static_css_path):
                    if file_name.endswith('.css'):
                        src_file = os.path.join(static_css_path, file_name)
                        dst_file = os.path.join(ASSETS_FOLDER, file_name)
                        shutil.copy2(src_file, dst_file)
                        downloaded_files.append(file_name)
                        print(f"Copied local CSS file: {file_name}")
    except Exception as e:
        print(f"Error accessing pyvis package: {str(e)}")
    
    # Now download any missing files from CDN
    # First JS files
    for js_file, js_url in js_files.items():
        if js_file not in downloaded_files:
            try:
                dst_file = os.path.join(ASSETS_FOLDER, js_file)
                if not os.path.exists(dst_file):
                    print(f"Downloading {js_file} from {js_url}")
                    download_file(js_url, dst_file)
                    downloaded_files.append(js_file)
            except Exception as e:
                print(f"Failed to download {js_file}: {str(e)}")
    
    # Then CSS files
    for css_file, css_url in css_files.items():
        if css_file not in downloaded_files:
            try:
                dst_file = os.path.join(ASSETS_FOLDER, css_file)
                if not os.path.exists(dst_file):
                    print(f"Downloading {css_file} from {css_url}")
                    download_file(css_url, dst_file)
                    downloaded_files.append(css_file)
            except Exception as e:
                print(f"Failed to download {css_file}: {str(e)}")
    
    # Create a fallback copy of vis-network.min.css if it's missing but vis.min.css exists
    if "vis-network.min.css" not in downloaded_files and "vis.min.css" in downloaded_files:
        vis_css = os.path.join(ASSETS_FOLDER, "vis.min.css")
        vis_network_css = os.path.join(ASSETS_FOLDER, "vis-network.min.css")
        if os.path.exists(vis_css) and not os.path.exists(vis_network_css):
            shutil.copy2(vis_css, vis_network_css)
            downloaded_files.append("vis-network.min.css")
            print("Created vis-network.min.css as a copy of vis.min.css")
    
    # List all files in assets folder for verification
    print("\nAssets in folder:")
    all_assets = []
    for file_name in os.listdir(ASSETS_FOLDER):
        file_path = os.path.join(ASSETS_FOLDER, file_name)
        file_size = os.path.getsize(file_path) / 1024  # Size in KB
        all_assets.append(file_name)
        print(f"  - {file_name} ({file_size:.1f} KB)")
    
    if downloaded_files:
        print(f"Successfully prepared {len(downloaded_files)} asset files")
        return True
    else:
        print("WARNING: No assets could be prepared!")
        return False

def download_file(url, destination):
    """Download a file from a URL to a destination path"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Successfully downloaded to {destination}")
        return True
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return False
    
def fix_html_asset_references(html_file):
    """
    Modify the HTML file to use local assets instead of CDN.
    
    Args:
        html_file: Path to the HTML file to modify
    """
    print(f"Fixing asset references in {html_file}")
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace CDN references with local file system references
    assets_abs_path = os.path.abspath(ASSETS_FOLDER)
    print(f"Using assets path: {assets_abs_path}")
    
    # Get a list of all available assets
    available_assets = set()
    if os.path.exists(ASSETS_FOLDER):
        available_assets = set(os.listdir(ASSETS_FOLDER))
    
    # Track replacements for debugging
    replacements = []
    skipped = []
    
    # Handle JavaScript files
    for js_pattern in [r'src=[\'"]([^\'"]+\.js)[\'"]']:
        for match in re.finditer(js_pattern, content):
            url = match.group(1)
            file_name = os.path.basename(url)
            local_path = os.path.join(assets_abs_path, file_name)
            
            # Skip if the asset doesn't exist locally
            if file_name not in available_assets:
                skipped.append(file_name)
                continue
                
            # Replace with local file URL
            new_url = f"file://{local_path}"
            content = content.replace(
                f'src="{url}"', 
                f'src="{new_url}"'
            )
            replacements.append((url, new_url))
    
    # Handle CSS files
    for css_pattern in [r'href=[\'"]([^\'"]+\.css)[\'"]']:
        for match in re.finditer(css_pattern, content):
            url = match.group(1)
            file_name = os.path.basename(url)
            local_path = os.path.join(assets_abs_path, file_name)
            
            # Skip if the asset doesn't exist locally
            if file_name not in available_assets:
                skipped.append(file_name)
                continue
                
            # Replace with local file URL
            new_url = f"file://{local_path}"
            content = content.replace(
                f'href="{url}"', 
                f'href="{new_url}"'
            )
            replacements.append((url, new_url))
    
    # Write the modified content back
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Print replacement summary
    if replacements:
        print(f"Replaced {len(replacements)} asset references:")
        for old, new in replacements[:5]:  # Show only first 5 to avoid clutter
            print(f"  - {old} → {new}")
        if len(replacements) > 5:
            print(f"  - ... and {len(replacements) - 5} more")
    
    # Only print skipped warnings if there are missing critical assets
    critical_assets = {"vis-network.min.js", "vis-network.min.css", "vis.min.js", "vis.min.css"}
    missing_critical = [asset for asset in skipped if asset in critical_assets]
    if missing_critical:
        print("WARNING: Missing critical assets that may affect visualization:")
        for asset in missing_critical:
            print(f"  - {asset}")
    
    return html_file 