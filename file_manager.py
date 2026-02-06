from fastmcp import FastMCP
import os
import json
from pathlib import Path

mcp = FastMCP("LocalFileSage")

# Define tool: to read local files
@mcp.tool()
def read_local_file(path: str) -> str:
    """Read a local file and return its content"""
    try:
        # Safety check to prevent reading sensitive files
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path) and os.path.isfile(abs_path):
            # Prevent reading files outside the current directory for security
            base_path = os.path.abspath('.')
            if os.path.commonpath([abs_path]) != os.path.commonpath([abs_path, base_path]):
                return "Error: Cannot read files outside the working directory"
            
            with open(abs_path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            return "Error: File does not exist or is not a file"
    except UnicodeDecodeError:
        return "Error: Unable to decode file as text"
    except PermissionError:
        return "Error: Permission denied to read the file"
    except Exception as e:
        return f"Error: {str(e)}"

# Define tool: Write content to a local file
@mcp.tool()
def write_local_file(path: str, content: str) -> str:
    """Write content to a local file"""
    try:
        abs_path = os.path.abspath(path)
        # Safety check to prevent writing outside the current directory
        base_path = os.path.abspath('.')
        if os.path.commonpath([abs_path]) != os.path.commonpath([abs_path, base_path]):
            return "Error: Cannot write files outside the working directory"
        
        # Create directory if it doesn't exist
        directory = os.path.dirname(abs_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to file: {path}"
    except PermissionError:
        return "Error: Permission denied to write the file"
    except Exception as e:
        return f"Error: {str(e)}"

# Define tool: List directory contents
@mcp.tool()
def list_directory(path: str = ".") -> dict:
    """List all files and directories in the specified folder with details"""
    try:
        abs_path = os.path.abspath(path)
        # Safety check to prevent accessing directories outside the current directory
        base_path = os.path.abspath('.')
        if os.path.commonpath([abs_path]) != os.path.commonpath([abs_path, base_path]):
            return {"error": "Cannot access directories outside the working directory"}
        
        items = []
        for item in os.listdir(abs_path):
            item_path = os.path.join(abs_path, item)
            stat = os.stat(item_path)
            items.append({
                "name": item,
                "type": "directory" if os.path.isdir(item_path) else "file",
                "size": stat.st_size,
                "modified": stat.st_mtime
            })
        
        return {
            "path": abs_path,
            "items": sorted(items, key=lambda x: (x["type"], x["name"])),
            "total_items": len(items)
        }
    except FileNotFoundError:
        return {"error": "Directory does not exist"}
    except PermissionError:
        return {"error": "Permission denied to access the directory"}
    except Exception as e:
        return {"error": str(e)}

# Define tool: Get file information
@mcp.tool()
def get_file_info(path: str) -> dict:
    """Get information about a specific file or directory"""
    try:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            stat = os.stat(abs_path)
            return {
                "path": abs_path,
                "name": os.path.basename(abs_path),
                "type": "directory" if os.path.isdir(abs_path) else "file",
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "permissions": oct(stat.st_mode)[-3:]
            }
        else:
            return {"error": "Path does not exist"}
    except Exception as e:
        return {"error": str(e)}

# Define tool: Create directory
@mcp.tool()
def create_directory(path: str) -> str:
    """Create a new directory"""
    try:
        abs_path = os.path.abspath(path)
        # Safety check to prevent creating directories outside the current directory
        base_path = os.path.abspath('.')
        if os.path.commonpath([abs_path]) != os.path.commonpath([abs_path, base_path]):
            return "Error: Cannot create directories outside the working directory"
        
        os.makedirs(abs_path, exist_ok=True)
        return f"Successfully created directory: {path}"
    except PermissionError:
        return "Error: Permission denied to create the directory"
    except Exception as e:
        return f"Error: {str(e)}"

# Define tool: Delete file
@mcp.tool()
def delete_file(path: str) -> str:
    """Delete a file"""
    try:
        abs_path = os.path.abspath(path)
        # Safety check to prevent deleting files outside the current directory
        base_path = os.path.abspath('.')
        if os.path.commonpath([abs_path]) != os.path.commonpath([abs_path, base_path]):
            return "Error: Cannot delete files outside the working directory"
        
        if os.path.isfile(abs_path):
            os.remove(abs_path)
            return f"Successfully deleted file: {path}"
        else:
            return "Error: Path is not a file or does not exist"
    except PermissionError:
        return "Error: Permission denied to delete the file"
    except Exception as e:
        return f"Error: {str(e)}"

# Define resource: Provide dynamic README document
@mcp.resource("docs://readme")
def get_readme() -> str:
    """Provide a dynamic README document"""
    readme_path = os.path.join(os.getcwd(), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Local File Manager MCP\n\nThis service allows you to interact with local files through the MCP protocol. Available tools:\n- read_local_file: Read file contents\n- write_local_file: Write content to a file\n- list_directory: List directory contents\n- get_file_info: Get info about a file/directory\n- create_directory: Create a new directory\n- delete_file: Delete a file"

# Define resource: Provide current working directory
@mcp.resource("config://working_directory")
def get_working_directory() -> str:
    """Provide the current working directory"""
    return os.getcwd()

# Define resource: Provide system information
@mcp.resource("config://system_info")
def get_system_info() -> dict:
    """Provide system information"""
    return {
        "platform": os.name,
        "cwd": os.getcwd(),
        "available_tools": [
            "read_local_file",
            "write_local_file", 
            "list_directory",
            "get_file_info",
            "create_directory",
            "delete_file"
        ]
    }

if __name__ == "__main__":
    print("Starting LocalFileSage MCP Server...")
    print(f"Working directory: {os.getcwd()}")
    mcp.run()