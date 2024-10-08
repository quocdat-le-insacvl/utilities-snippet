import re
import subprocess
import argparse
import shlex
import sys
import json
import os
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

def parse_fault_tolerant_xml(xml_string: str) -> List[Dict[str, Any]]:
    # Normalize line endings
    xml_string = xml_string.replace('\r\n', '\n').replace('\r', '\n')

    # Remove any XML declaration to avoid parsing issues
    xml_string = re.sub(r'<\?xml.*?\?>', '', xml_string)

    # Wrap content in a root element if not present
    if not xml_string.strip().startswith('<root>'):
        xml_string = f"<root>{xml_string}</root>"

    # Replace problematic characters
    xml_string = re.sub(r'&(?!amp;|lt;|gt;|apos;|quot;)', '&amp;', xml_string)

    result = []

    try:
        # Parse the entire XML structure
        root = ET.fromstring(xml_string)

        # Find all file elements
        file_elements = root.findall('.//file')

        for file_elem in file_elements:
            file_info = {}
            for child in file_elem:
                if child.tag == 'code':
                    file_info[child.tag] = child.text.strip() if child.text else ""
                else:
                    file_info[child.tag] = child.text.strip() if child.text else ""
            result.append(file_info)
    except ET.ParseError as e:
        print(f"Warning: Error parsing XML, attempting manual extraction: {str(e)}", file=sys.stderr)
        # If parsing fails, try to extract information manually
        file_blocks = re.findall(r'<file>.*?</file>', xml_string, re.DOTALL)
        for block in file_blocks:
            file_info = {}
            for tag in ['path', 'action', 'description', 'code']:
                match = re.search(f'<{tag}>(.*?)</{tag}>', block, re.DOTALL)
                if match:
                    file_info[tag] = match.group(1).strip()
            if file_info:
                result.append(file_info)
            else:
                print(f"Warning: Unable to extract information from block: {block[:100]}...", file=sys.stderr)

    return result

def extract_tasks(text, use_json=False):
    if use_json:
        # Try to parse as JSON
        try:
            data = json.loads(text)
            if isinstance(data, dict) and "filesContent" in data:
                return [
                    {
                        "file": file_info['file'],
                        "action": file_info['action'],
                        "description": file_info['description'],
                        "code": file_info.get('code', '')
                    }
                    for file_info in data["filesContent"]
                ]
        except json.JSONDecodeError:
            print("Warning: Failed to parse JSON, falling back to XML parsing", file=sys.stderr)
    
    # Default to XML parsing
    return parse_fault_tolerant_xml(text)

def trim_command(command, max_length=400):
    if len(command) <= max_length:
        return command
    head = command[:max_length//2 - 3]
    tail = command[-max_length//2 + 3:]
    return f"{head}...{tail}"

def parse_arguments():
    parser = argparse.ArgumentParser(description="Execute tasks using aider with custom arguments.")
    
    # Model selection group
    model_group = parser.add_mutually_exclusive_group()
    model_group.add_argument('--model', help="Specify the model to use for the main chat [env var: AIDER_MODEL]")
    model_group.add_argument('--opus', action='store_true', help="Use claude-3-opus-20240229 model for the main chat [env var: AIDER_OPUS]")
    model_group.add_argument('--sonnet', action='store_true', help="Use claude-3-5-sonnet-20240620 model for the main chat [env var: AIDER_SONNET]")
    model_group.add_argument('--4', '-4', action='store_true', help="Use gpt-4-0613 model for the main chat [env var: AIDER_4]")
    model_group.add_argument('--4o', action='store_true', help="Use gpt-4o-2024-08-06 model for the main chat [env var: AIDER_4O]")
    model_group.add_argument('--mini', action='store_true', help="Use gpt-4o-mini model for the main chat [env var: AIDER_MINI]")
    model_group.add_argument('--4-turbo', action='store_true', help="Use gpt-4-1106-preview model for the main chat [env var: AIDER_4_TURBO]")
    model_group.add_argument('--deepseek', action='store_true', help="Use deepseek/deepseek-coder model for the main chat [env var: AIDER_DEEPSEEK]")

    parser.add_argument('--input', help="Path to the input file (XML or JSON)")
    parser.add_argument('--skip', type=int, default=0, help="Number of tasks to skip")
    parser.add_argument('--only', type=int, nargs='+', help="Only execute specified task numbers")
    parser.add_argument('--use-json', action='store_true', help="Use JSON parsing instead of XML")
    parser.add_argument('--confirm', action='store_true', help="Confirm before executing each task")
    parser.add_argument('aider_args', nargs=argparse.REMAINDER, help="Arguments to pass to aider command")
    return parser.parse_args()

def get_input(input_file=None):
    if input_file:
        try:
            with open(input_file, 'r') as file:
                return file.read().strip()
        except IOError as e:
            print(f"Error reading input file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Please paste your text below. When finished, press Ctrl+D (Unix) or Ctrl+Z (Windows) followed by Enter:")
        return sys.stdin.read().strip()

def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"File deleted successfully: {file_path}")
        
        # Git operations
        try:
            # Remove the file from Git
            subprocess.run(['git', 'rm', file_path], check=True)
            print(f"File removed from Git: {file_path}")
            
            # Commit the change
            commit_message = f"Remove file: {file_path}"
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            print(f"Changes committed: {commit_message}")
        except subprocess.CalledProcessError as e:
            print(f"Error performing Git operations: {e}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except PermissionError:
        print(f"Permission denied: Unable to delete {file_path}")
    except Exception as e:
        print(f"An error occurred while deleting {file_path}: {e}")

def get_model_flag(args):
    if args.model:
        return f'--model {args.model}'
    elif args.opus:
        return '--opus'
    elif args.sonnet:
        return '--sonnet'
    elif getattr(args, '4'):
        return '--4'
    elif args.__dict__['4o']:
        return '--4o'
    elif args.mini:
        return '--mini'
    elif args.__dict__['4_turbo']:
        return '--4-turbo'
    elif args.deepseek:
        return '--deepseek'
    else:
        return '--deepseek'  # Default to deepseek if no model is specified

def format_task(task):
    formatted_task = f"Update file: {task['path']}\n\n"
    formatted_task += f"\"action\": \"{task['action']}\"\n\n"
    formatted_task += f"Description: {task['description']}\n\n"
    if task['action'].lower() != 'delete':
        formatted_task += f"New content:\n\n{task['code']}"
    return formatted_task

def main():
    args = parse_arguments()
    aider_args = ' '.join(args.aider_args)
    text = get_input(args.input)

    tasks = extract_tasks(text, args.use_json)
    if not tasks:
        print("No tasks found in the input.")
        return
    
    model_flag = get_model_flag(args)
    
    # Apply task selection based on --skip and --only arguments
    if args.only:
        selected_tasks = [tasks[i-1] for i in args.only if 1 <= i <= len(tasks)]
    else:
        selected_tasks = tasks[args.skip:]

    total_tasks = len(tasks)  # Store the total number of tasks

    for i, task in enumerate(selected_tasks, start=1):
        print("#"*20)
        print("#"*20)
        
        # Calculate the original task number
        original_task_number = args.only[i-1] if args.only else i + args.skip
        
        print(f"Executing task {original_task_number}/{total_tasks}...")
        
        file_path = task['path']
        action = task['action'].lower()
        
        print(f"[Action]: {action}")
        if action == "delete":
            delete_file(file_path)
            continue  # Skip to the next task after deletion
        
        dir_path = os.path.dirname(file_path)
        
        if action == "create" and dir_path:
            # Create directory only if action is create and dir_path is not empty
            mkdir_command = f'mkdir -p {shlex.quote(dir_path)}'
            print(f"Creating directory: {mkdir_command}")
            try:
                subprocess.run(mkdir_command, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Warning: Failed to create directory: {e}")
        
        # Touch file for create or update actions
        if action in ["create", "update"]:
            touch_command = f'touch {shlex.quote(file_path)}'
            print(f"Creating/updating file: {touch_command}")
            try:
                subprocess.run(touch_command, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Warning: Failed to create/update file: {e}")
        
        # Format the task to string before sending to the command
        formatted_task = format_task(task)
        escaped_task = shlex.quote(formatted_task)
        command = (
            f'python -m aider '
            f'--yes '
            f'{model_flag} '
            f'--no-suggest-shell-commands '
            f'{aider_args} '
            f'--message {escaped_task}'
        )
        if action.lower() != 'delete':
            command += f' {shlex.quote(file_path)}'
        
        print(f"Running command: {trim_command(command)}")
        try:
            subprocess.run(command, shell=True, check=True)
            print(f"Task {original_task_number} executed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error executing task {original_task_number}: {e}")

        if args.confirm:
            try:
                confirm = input("Do you want to continue? (y/n): ").lower().strip()
                if confirm != 'n':
                    print(f"Skipping task {original_task_number}")
                    continue
            except EOFError:
                print("Running in non-interactive mode. Continuing without confirmation.")

if __name__ == "__main__":
    main()
