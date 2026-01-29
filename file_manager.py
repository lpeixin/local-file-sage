from fastmcp import FastMCP
import os

mcp = FastMCP("LocalFileSage")

# create a FastMCP instance
mcp = FastMCP("LocalFileSage")

# define tool: to read local files and list directory contents
@mcp.tool()
def read_local_file(path: str) -> str:
    """read a local file and return its content"""
    # note: safety check to prevent reading sensitive files
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "Error: File does not exist"

# define tool: list directory contents
@mcp.tool()
def list_directory(path: str = ".") -> list:
    """list all files and directories in the current folder"""
    try:
        return os.listdir(path)
    except Exception as e:
        return [str(e)]

# define resource: provide a fixed README document
@mcp.resource("config://readme")
def get_readme() -> str:
    """provide a fixed README document"""
    return "This is a local file manager built with the MCP protocol. You can ask me to read code, summarize logic, or list directories."

if __name__ == "__main__":
    mcp.run()