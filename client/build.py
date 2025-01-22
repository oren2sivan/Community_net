import os
import PyInstaller.__main__
import shutil
import base64

def create_resource_module():
    """Create a Python module containing the batch files as embedded strings"""
    
    # Read the batch files
    with open(os.path.join('config', 'dependencies-1.bat'), 'rb') as f:
        dependencies_content = base64.b64encode(f.read()).decode()
        
    with open(os.path.join('config', 'ipfs_config.bat'), 'rb') as f:
        ipfs_config_content = base64.b64encode(f.read()).decode()
    
    # Create the resource module
    resource_code = f'''
import os
import base64

def extract_config_files():
    """Extract the embedded batch files to the config directory"""
    # Create config directory if it doesn't exist
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.join(current_dir, 'config')
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    # Write dependencies batch file
    dependencies_path = os.path.join(config_dir, 'dependencies-1.bat')
    with open(dependencies_path, 'wb') as f:
        f.write(base64.b64decode('{dependencies_content}'))
    
    # Write IPFS config batch file
    ipfs_config_path = os.path.join(config_dir, 'ipfs_config.bat')
    with open(ipfs_config_path, 'wb') as f:
        f.write(base64.b64decode('{ipfs_config_content}'))
    
    return config_dir
'''
    
    # Write the resource module
    with open('embedded_resources.py', 'w') as f:
        f.write(resource_code)

def build_exe():
    # Create the resource module with embedded files
    create_resource_module()
    
    # Create build directory
    if not os.path.exists('build_files'):
        os.makedirs('build_files')
    
    # Copy all necessary files
    files_to_include = [
        'client_log_in.py',
        'client_setup.py',
        'command_executor.py',
        'gen_swarm_key.py',
        'embedded_resources.py'
    ]
    
    for file in files_to_include:
        if os.path.exists(file):
            shutil.copy2(file, 'build_files')
    
    # PyInstaller arguments
    args = [
        'build_files/client_log_in.py',  # Main script
        '--name=IPFS_Client',           # Executable name
        '--onefile',                    # Create single executable
        '--noconsole',                  # No console window
        
        # Add all Python files as modules
        '--hidden-import=client_setup',
        '--hidden-import=command_executor',
        '--hidden-import=gen_swarm_key',
        '--hidden-import=embedded_resources',
    ]
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    # Clean up
    shutil.rmtree('build_files')
    os.remove('embedded_resources.py')
    
    print("\nBuild complete! Check the 'dist' folder for your executable.")
    print("\nUser instructions:")
    print("1. Just run the executable!")
    print("2. The program will automatically create all necessary files and directories")

if __name__ == "__main__":
    build_exe()