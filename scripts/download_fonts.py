"""
Download DejaVu fonts for PDF Unicode support
"""

import urllib.request
from pathlib import Path
import tarfile
import tempfile
import shutil

# Create fonts directory
fonts_dir = Path(__file__).parent.parent / 'fonts'
fonts_dir.mkdir(exist_ok=True)

# Download the entire font package
package_url = 'https://downloads.sourceforge.net/project/dejavu/dejavu/2.37/dejavu-fonts-ttf-2.37.tar.bz2'

print("Downloading DejaVu fonts for Unicode support...")
print(f"Downloading font package from SourceForge...")

try:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = Path(temp_dir) / 'dejavu-fonts.tar.bz2'
        urllib.request.urlretrieve(package_url, temp_file)
        print("✓ Package downloaded")
        
        print("Extracting fonts...")
        with tarfile.open(temp_file, 'r:bz2') as tar:
            # Extract only the TTF files we need
            for member in tar.getmembers():
                if member.name.endswith('DejaVuSans.ttf') or member.name.endswith('DejaVuSans-Bold.ttf'):
                    member.name = Path(member.name).name  # Get just the filename
                    tar.extract(member, fonts_dir)
                    print(f"✓ {member.name} extracted")
        
        print("\n✓ Font setup complete!")
        
except Exception as e:
    print(f"✗ Error: {e}")
    print("\nTrying alternative download method...")
    
    # Alternative: Try jsdelivr CDN
    fonts_to_download = {
        'DejaVuSans.ttf': 'https://cdn.jsdelivr.net/npm/dejavu-fonts-ttf@2.37.3/ttf/DejaVuSans.ttf',
        'DejaVuSans-Bold.ttf': 'https://cdn.jsdelivr.net/npm/dejavu-fonts-ttf@2.37.3/ttf/DejaVuSans-Bold.ttf'
    }
    
    for filename, url in fonts_to_download.items():
        filepath = fonts_dir / filename
        if not filepath.exists():
            print(f"Downloading {filename}...")
            try:
                urllib.request.urlretrieve(url, filepath)
                print(f"✓ {filename} downloaded successfully")
            except Exception as e2:
                print(f"✗ Error downloading {filename}: {e2}")
