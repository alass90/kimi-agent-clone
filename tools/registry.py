"""
Tool Registry — Complete 29-tool schema definitions.
Faithful reproduction of Kimi's ok-computer.json tool schemas.

Each tool has:
  - name: unique identifier
  - description: what the tool does (used in LLM system prompt)
  - parameters: JSON Schema for the tool arguments
"""

from typing import List, Dict, Any


def get_all_tools() -> List[Dict[str, Any]]:
    """Return all 27 tool schemas in OpenAI function-calling format."""
    return TOOL_SCHEMAS


def get_tool_names() -> List[str]:
    """Return list of all tool names."""
    return [t["function"]["name"] for t in TOOL_SCHEMAS]


def get_tool_by_name(name: str) -> Dict[str, Any]:
    """Return a specific tool schema by name."""
    for tool in TOOL_SCHEMAS:
        if tool["function"]["name"] == name:
            return tool
    return None


TOOL_SCHEMAS = [
    # ═══════════════════════════════════════════════════════════════════════
    # 1. TODO READ
    # ═══════════════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "todo_read",
            "description": (
                "Read the current todo list. Use this at the start of every task to check "
                "existing progress and avoid duplicating work. Returns all tasks with their "
                "status (pending, in_progress, done)."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    # ═══════════════════════════════════════════════════════════════════════
    # 2. TODO WRITE
    # ═══════════════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "todo_write",
            "description": (
                "Write/update the todo list. Use this to track task progress. "
                "Rules: (1) Only ONE task can be 'in_progress' at a time. "
                "(2) Tasks should progress: pending -> in_progress -> done. "
                "(3) Include all tasks, not just the current one."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "todos": {
                        "type": "array",
                        "description": "Complete list of all tasks with their current status.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer", "description": "Task ID"},
                                "task": {"type": "string", "description": "Task description"},
                                "status": {
                                    "type": "string",
                                    "enum": ["pending", "in_progress", "done"],
                                },
                            },
                            "required": ["id", "task", "status"],
                        },
                    }
                },
                "required": ["todos"],
            },
        },
    },
    # ═══════════════════════════════════════════════════════════════════════
    # 3. IPYTHON
    # ═══════════════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "ipython",
            "description": (
                "Execute Python code in a stateful IPython/Jupyter kernel. "
                "The kernel maintains state across calls (variables, imports, etc.). "
                "Use for: data analysis, computation, visualization, file processing. "
                "Matplotlib plots are automatically captured as images. "
                "Output is truncated at 10000 characters. "
                "Set restart=true to restart the kernel (clears all state)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code to execute."},
                    "restart": {"type": "boolean", "description": "Restart the kernel. Default: false."},
                },
                "required": ["code"],
            },
        },
    },
    # ═══════════════════════════════════════════════════════════════════════
    # 4. READ FILE
    # ═══════════════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Read the contents of a file. Returns numbered lines for easy reference. "
                "For large files, use offset and limit to read specific sections. "
                "Binary files (images, PDFs) return metadata instead of content. "
                "IMPORTANT: You must read a file before you can edit it."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Absolute path to the file."},
                    "offset": {"type": "integer", "description": "Starting line number (1-indexed). Default: 1."},
                    "limit": {"type": "integer", "description": "Maximum number of lines to return. Default: 1000."},
                },
                "required": ["file_path"],
            },
        },
    },
    # ═══════════════════════════════════════════════════════════════════════
    # 5. WRITE FILE
    # ═══════════════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": (
                "Write content to a file. Creates the file and parent directories if they don't exist. "
                "Use append=true to add content to the end of an existing file. "
                "Content limit: 100000 characters per call."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Absolute path to the file."},
                    "content": {"type": "string", "description": "Content to write."},
                    "append": {"type": "boolean", "description": "Append to existing file. Default: false."},
                },
                "required": ["file_path", "content"],
            },
        },
    },
    # ═══════════════════════════════════════════════════════════════════════
    # 6. EDIT FILE
    # ═══════════════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": (
                "Edit a file by replacing a specific string with a new string. "
                "IMPORTANT: You MUST read_file before editing. "
                "The old_string must match exactly (including whitespace). "
                "If old_string appears multiple times, use replace_all=true."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Absolute path to the file."},
                    "old_string": {"type": "string", "description": "Exact string to find."},
                    "new_string": {"type": "string", "description": "Replacement string."},
                    "replace_all": {"type": "boolean", "description": "Replace all occurrences. Default: false."},
                },
                "required": ["file_path", "old_string", "new_string"],
            },
        },
    },
    # ═══════════════════════════════════════════════════════════════════════
    # 7. SHELL
    # ═══════════════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "shell",
            "description": (
                "Execute a shell command. Each call runs in a fresh shell (non-persistent). "
                "Use for: installing packages, running scripts, file operations. "
                "Output truncated at 10000 chars. Do not run interactive commands."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to execute."},
                    "timeout": {"type": "integer", "description": "Timeout in seconds. Default: 600."},
                },
                "required": ["command"],
            },
        },
    },
    # ═══════════════════════════════════════════════════════════════════════
    # 8. WEB SEARCH
    # ═══════════════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the web for information. Returns results with titles, URLs, and snippets. "
                "Use browser_visit to read full page content from the results."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query string."},
                    "count": {"type": "integer", "description": "Number of results. Default: 5."},
                },
                "required": ["query"],
            },
        },
    },
    # ═══════════════════════════════════════════════════════════════════════
    # 9. BROWSER VISIT
    # ═══════════════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "browser_visit",
            "description": (
                "Navigate to a URL and extract page content. Returns page title, text content, "
                "and interactive elements with indices for browser_click/browser_input."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to visit (include protocol)."},
                    "need_screenshot": {"type": "boolean", "description": "Capture screenshot. Default: false."},
                },
                "required": ["url"],
            },
        },
    },
    # ═══════════════════════════════════════════════════════════════════════
    # 10. BROWSER CLICK
    # ═══════════════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "browser_click",
            "description": "Click an interactive element by its index from browser_visit.",
            "parameters": {
                "type": "object",
                "properties": {
                    "element_index": {"type": "integer", "description": "Element index to click."},
                },
                "required": ["element_index"],
            },
        },
    },
    # ═══════════════════════════════════════════════════════════════════════
    # 11. BROWSER INPUT
    # ═══════════════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "browser_input",
            "description": "Type text into a form field. Clears existing content first.",
            "parameters": {
                "type": "object",
                "properties": {
                    "element_index": {"type": "integer", "description": "Input element index."},
                    "content": {"type": "string", "description": "Text to type."},
                },
                "required": ["element_index", "content"],
            },
        },
    },
    # ═══════════════════════════════════════════════════════════════════════
    # 12. BROWSER SCROLL DOWN
    # ═══════════════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "browser_scroll_down",
            "description": "Scroll down on the current page.",
            "parameters": {
                "type": "object",
                "properties": {
                    "scroll_amount": {"type": "integer", "description": "Pixels to scroll. Default: 500."},
                },
                "required": [],
            },
        },
    },
    # ═══════════════════════════════════════════════════════════════════════
    # 13. BROWSER SCROLL UP
    # ═══════════════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "browser_scroll_up",
            "description": "Scroll up on the current page.",
            "parameters": {
                "type": "object",
                "properties": {
                    "scroll_amount": {"type": "integer", "description": "Pixels to scroll. Default: 500."},
                },
                "required": [],
            },
        },
    },
    # ═══════════════════════════════════════════════════════════════════════
    # 14. BROWSER SCREENSHOT
    # ═══════════════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "browser_screenshot",
            "description": "Take a screenshot of the current browser viewport.",
            "parameters": {
                "type": "object",
                "properties": {
                    "download_path": {"type": "string", "description": "Path to save screenshot."},
                },
                "required": [],
            },
        },
    },
    # ═══════════════════════════════════════════════════════════════════════
    # 15. BROWSER FIND
    # ═══════════════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "browser_find",
            "description": "Search for text on the current page. Returns matches with context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "Text to search for."},
                    "skip": {"type": "integer", "description": "Matches to skip. Default: 0."},
                },
                "required": ["keyword"],
            },
        },
    },
    # ═══════════════════════════════════════════════════════════════════════
    # 16. GENERATE IMAGE
    # ═══════════════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "generate_image",
            "description": (
                "Generate an image from a text prompt using AI (DALL-E 3). "
                "Supports various aspect ratios and resolutions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Detailed image description."},
                    "output_path": {"type": "string", "description": "Path to save the image."},
                    "ratio": {
                        "type": "string",
                        "enum": ["1:1", "3:2", "2:3", "4:3", "3:4", "16:9", "9:16", "21:9"],
                        "description": "Aspect ratio. Default: 1:1.",
                    },
                    "resolution": {
                        "type": "string", "enum": ["1K", "2K", "4K"],
                        "description": "Resolution quality. Default: 1K.",
                    },
                },
                "required": ["prompt"],
            },
        },
    },
    # ═══════════════════════════════════════════════════════════════════════
    # 17. GENERATE SPEECH
    # ═══════════════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "generate_speech",
            "description": (
                "Generate speech audio from text using TTS (OpenAI). "
                "Supports multiple voices and speed control. Output: MP3."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to convert to speech."},
                    "output_path": {"type": "string", "description": "Path to save the audio file."},
                    "voice": {
                        "type": "string",
                        "enum": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
                        "description": "Voice. Default: alloy.",
                    },
                    "speed": {"type": "number", "description": "Speed (0.25-4.0). Default: 1.0."},
                },
                "required": ["text"],
            },
        },
    },
    # ═══════════════════════════════════════════════════════════════════════
    # 18. GENERATE SOUND EFFECT
    # ═══════════════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "generate_sound_effect",
            "description": (
                "Generate a sound effect from a text description via audio synthesis. "
                "Supports: bells, whooshes, clicks, alarms, rain, etc. Output: WAV."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Sound effect description."},
                    "output_path": {"type": "string", "description": "Path to save the sound file."},
                    "duration": {"type": "number", "description": "Duration in seconds. Default: 3.0."},
                },
                "required": ["prompt"],
            },
        },
    },
    # ═══════════════════════════════════════════════════════════════════════
    # 19. GET DATA SOURCE
    # ═══════════════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "get_data_source",
            "description": (
                "Fetch data from external sources: yahoo_finance (stocks), "
                "world_bank (economic indicators), arxiv (papers), google_scholar (research)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "enum": ["yahoo_finance", "world_bank", "world_bank_open_data", "arxiv", "google_scholar"],
                        "description": "Data source to query.",
                    },
                    "query": {"type": "string", "description": "Query (ticker, indicator code, or search terms)."},
                    "params": {
                        "type": "object",
                        "description": "Additional parameters.",
                        "properties": {
                            "country": {"type": "string", "description": "Country code for World Bank."},
                            "max_results": {"type": "integer", "description": "Max results for papers."},
                        },
                    },
                },
                "required": ["source", "query"],
            },
        },
    },
    # ═══════════════════════════════════════════════════════════════════════
    # 20. FIND BBOX
    # ═══════════════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "find_bbox",
            "description": (
                "Find the bounding box of an element in an image using AI vision. "
                "Returns coordinates as percentages of image dimensions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "image_path": {"type": "string", "description": "Path to the image file."},
                    "description": {"type": "string", "description": "What to find (e.g., 'the login button')."},
                },
                "required": ["image_path", "description"],
            },
        },
    },
    # ═══════════════════════════════════════════════════════════════════════
    # 21. CROP IMAGE
    # ═══════════════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "crop_image",
            "description": (
                "Crop a region from an image. Coordinates can be pixels or percentages (0-100). "
                "Use find_bbox first to get coordinates."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "image_path": {"type": "string", "description": "Path to the source image."},
                    "x": {"type": "number", "description": "Left edge of crop region."},
                    "y": {"type": "number", "description": "Top edge of crop region."},
                    "width": {"type": "number", "description": "Width of crop region."},
                    "height": {"type": "number", "description": "Height of crop region."},
                    "output_path": {"type": "string", "description": "Path to save cropped image."},
                },
                "required": ["image_path", "x", "y", "width", "height"],
            },
        },
    },
    # ═══════════════════════════════════════════════════════════════════════
    # 22. CREATE SLIDES
    # ═══════════════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "create_slides",
            "description": (
                "Generate a PowerPoint presentation (PPTX) from structured slide data. "
                "Themes: default, dark, corporate."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "slides": {
                        "type": "array",
                        "description": "Array of slide objects.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "content": {"type": "string"},
                                "notes": {"type": "string"},
                                "layout": {"type": "string"},
                            },
                            "required": ["title"],
                        },
                    },
                    "output_path": {"type": "string", "description": "Path to save the PPTX file."},
                    "theme": {
                        "type": "string", "enum": ["default", "dark", "corporate"],
                        "description": "Theme. Default: default.",
                    },
                },
                "required": ["slides"],
            },
        },
    },
    # ═══════════════════════════════════════════════════════════════════════
    # 23. DEPLOY WEBSITE
    # ═══════════════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "deploy_website",
            "description": (
                "Deploy a static website from a local directory. "
                "Directory must contain index.html."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "local_dir": {"type": "string", "description": "Path to the website directory."},
                    "description": {"type": "string", "description": "Website description."},
                },
                "required": ["local_dir"],
            },
        },
    },
    # ═══════════════════════════════════════════════════════════════════════
    # 24. GET CURRENT TIME
    # ═══════════════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current date and time (ISO format, timestamp).",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    # ═══════════════════════════════════════════════════════════════════════
    # 25. LIST WORKSPACE
    # ═══════════════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "list_workspace",
            "description": "List files and directories in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to list. Default: workspace root."},
                },
                "required": [],
            },
        },
    },
    # ═══════════════════════════════════════════════════════════════════════
    # 26. DOWNLOAD FILE
    # ═══════════════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "download_file",
            "description": "Download a file from a URL to the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to download."},
                    "output_path": {"type": "string", "description": "Local save path."},
                },
                "required": ["url"],
            },
        },
    },
    # ═══════════════════════════════════════════════════════════════════════
    # 27. UPLOAD FILE
    # ═══════════════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "upload_file",
            "description": "Upload a file to the upload directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the file to upload."},
                },
                "required": ["file_path"],
            },
        },
    },
]
