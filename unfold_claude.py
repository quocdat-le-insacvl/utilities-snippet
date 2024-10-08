import os
import shutil
import argparse
import tempfile
import pyperclip
import tiktoken
from tqdm import tqdm
import json
import nbformat
from datetime import datetime
import subprocess

def get_all_files(path, exclude_extensions, exclude_filenames, exclude_folders):
    if os.path.isfile(path):
        return [path]
    
    file_list = []
    for root, dirs, files in os.walk(path):
        # Convert exclude_folders to a set for faster lookup
        exclude_dirs = {'favicon', '__pycache__', 'venv', '.git', 'databases', 'database', 'uploads'}.union(set(exclude_folders))
        
        # Filter out directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in exclude_dirs]
        
        # Skip processing files in excluded directories
        if any(excluded in root for excluded in exclude_dirs):
            continue
        
        for file in files:
            remove_pattern = ['__pycache__', 'venv',  '.tsbuildinfo', '.git', '.sqlite3', '.log', '.png', '-lock', '.ico']
            if any(pattern in file for pattern in remove_pattern):
                print('- ', file)
                continue
            if not file.startswith('.') and file != '.env' and file != '__init__.py':
                file_extension = os.path.splitext(file)[1]
                if file_extension not in exclude_extensions and file not in exclude_filenames:
                    file_list.append(os.path.join(root, file))
    return file_list

def rename_file(file_path, base_dir):
    relative_path = os.path.relpath(file_path, base_dir)
    return relative_path.replace(os.path.sep, '--')

def count_tokens(file_path):
    encoding = tiktoken.get_encoding("cl100k_base")
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()
    return len(encoding.encode(content))

def convert_ipynb_to_text(ipynb_path):
    with open(ipynb_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    text_content = ""
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            text_content += "```python\n"
            text_content += ''.join(cell['source'])
            text_content += "\n```\n\n"
        elif cell['cell_type'] == 'markdown':
            text_content += ''.join(cell['source'])
            text_content += "\n\n"
    
    return text_content

def create_combined_content(files_subfolder, include_repo_structure=False):
    content = "This file is a merged representation of the entire codebase, combining all repository files into a single document.\n\n"

    # Repository Structure
    if include_repo_structure:
        content += "================================================================\n"
        content += "Repository Structure\n"
        content += "================================================================\n"
        try:
            tree_output = subprocess.check_output(['tree', '-I', 'node_modules'], text=True)
            content += tree_output + "\n"
        except subprocess.CalledProcessError:
            content += "Error: Unable to run 'tree' command. Make sure it's installed on your system.\n\n"
        except FileNotFoundError:
            content += "Error: 'tree' command not found. Please install it or make sure it's in your PATH.\n\n"

    # Repository Files
    content += "================================================================\n"
    content += "Repository Files\n"
    content += "================================================================\n\n"

    for root, _, files in os.walk(files_subfolder):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, files_subfolder)
            relative_path = relative_path.replace('--', '/')

            content += "================\n"
            content += f"File: {relative_path}\n"
            content += "================\n"

            if file.endswith('.ipynb'):
                content += convert_ipynb_to_text(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content += f.read()
            content += "\n\n"

    content += "================================================================\n"

    return content

def process_path(path, dest_folder, exclude_extensions, exclude_filenames, exclude_folders, verbose):
    all_files = get_all_files(path, exclude_extensions, exclude_filenames, exclude_folders)
    total_tokens = 0
    for file_path in tqdm(all_files, desc=f"Processing {path}"):
        dest_path = os.path.join(dest_folder, file_path.replace('/', '--'))
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        if file_path.endswith('.ipynb'):
            # Convert .ipynb to text and save
            with open(dest_path + '.txt', 'w', encoding='utf-8') as f:
                f.write(convert_ipynb_to_text(file_path))
            file_tokens = count_tokens(dest_path + '.txt')
        else:
            shutil.copy2(file_path, dest_path)
            file_tokens = count_tokens(dest_path)

        total_tokens += file_tokens
        if verbose:
            print(f"Processed: {file_path} ({file_tokens} tokens)")
    return total_tokens

def get_file_sizes(folder):
    file_sizes = []
    for root, _, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            relative_path = os.path.relpath(file_path, folder)
            original_name = relative_path.replace('--', '/')
            file_sizes.append((file_size, original_name))
    return sorted(file_sizes)


def main():
    parser = argparse.ArgumentParser(description="Process files and folders for Claude.")
    parser.add_argument('paths', nargs='+', help='Files and folders to process')
    parser.add_argument('--exclude-extensions', '-ee', nargs='*', default=['.woff', '.ico'], help='File extensions to exclude (e.g., .txt .pdf)')
    parser.add_argument('--exclude-filenames', '-ef', nargs='*', default=[], help='File names to exclude')
    parser.add_argument('--exclude-folders', '-ed', nargs='*', default=['node_modules'], help='Folder names to exclude')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--no-repo', action='store_true', help='Exclude repository structure from the output')
    args = parser.parse_args()

    exclude_extensions = set(args.exclude_extensions)
    exclude_filenames = set(args.exclude_filenames)
    exclude_folders = set(args.exclude_folders)

    # Print excluded folders for debugging
    print(f"Excluded folders: {exclude_folders}")

    # Create a unique directory name using current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f'/tmp/unfold/run_{timestamp}'
    os.makedirs(output_dir, exist_ok=True)

    files_subfolder = os.path.join(output_dir, "files")
    os.makedirs(files_subfolder, exist_ok=True)

    total_tokens = 0
    for path in args.paths:
        if os.path.exists(path):
            if args.verbose:
                print(f"Processing path: {path}")
            total_tokens += process_path(path, files_subfolder, exclude_extensions, exclude_filenames, exclude_folders, args.verbose)
        else:
            print(f"Warning: {path} does not exist. Skipping.")

    combined_content = create_combined_content(files_subfolder, include_repo_structure=not args.no_repo)

    output_file = os.path.join(output_dir, 'combined_content.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(combined_content)

    pyperclip.copy(combined_content)

    print(f"\nTotal tokens in all processed files: {total_tokens}")
    cost = (total_tokens / 1_000_000) * 3.00
    print(f"Estimated cost (Claude Sonnet rate): ${cost:.2f} USD")
    print(f"Combined content has been copied to clipboard and saved to: {output_file}")

    if args.verbose:
        print("\nFiles sorted by size (in bytes):")
        for size, name in get_file_sizes(files_subfolder):
            print(f"{size} bytes: {name}")

if __name__ == "__main__":
    main()
