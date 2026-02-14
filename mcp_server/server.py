"""
MCP Code-Runner Server
======================
Runs as a standalone HTTP server on port 8001.
Start it with:  python server.py
MCP endpoint:   http://127.0.0.1:8001/mcp

Supported languages: python, javascript, java
"""

from mcp.server.fastmcp import FastMCP
import subprocess
import tempfile
import shutil
import os
import sys
import traceback

mcp = FastMCP(
    "code-runner",
    host="127.0.0.1",
    port=8001,
    stateless_http=True,
)

# ─────────────────────────────────────────────────────────────────────────────
#  Language configurations
#  Each entry defines:
#    suffix   - temp file extension
#    command  - callable(path) that returns the subprocess command list
#    cleanup  - callable(path) that removes any extra files after execution
# ─────────────────────────────────────────────────────────────────────────────

def _java_class_name(path: str) -> str:
    """Java requires the filename to match the public class name. We use Main."""
    return "Main"

def _java_command(path: str) -> list:
    """Compile then run. We return the compile command; run happens after."""
    return ["javac", path]

def _find_node() -> str:
    found = shutil.which("node")
    if not found:
        raise FileNotFoundError("node not found on PATH")
    return found

def _find_java() -> str:
    found = shutil.which("java")
    if not found:
        raise FileNotFoundError("java not found on PATH")
    return found

def _find_javac() -> str:
    found = shutil.which("javac")
    if not found:
        raise FileNotFoundError("javac not found on PATH")
    return found


@mcp.tool()
def run_code(language: str, code: str) -> dict:
    """
    Execute candidate code in a sandboxed subprocess.

    Args:
        language: One of 'python', 'javascript', 'java'.
        code:     The source code string to execute.

    Returns:
        dict with stdout, stderr, and exit_code.
    """
    lang = language.strip().lower()
    files_to_cleanup = []

    try:

        # ── PYTHON ────────────────────────────────────────────────────────
        if lang == "python":
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".py", mode="w", encoding="utf-8"
            ) as f:
                f.write(code)
                path = f.name
            files_to_cleanup.append(path)

            result = subprocess.run(
                [sys.executable, path],
                capture_output=True, text=True, timeout=10,
                env={**os.environ, "PYTHONNOUSERSITE": "1"},
            )

        # ── JAVASCRIPT ────────────────────────────────────────────────────
        elif lang == "javascript":
            node = _find_node()

            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".js", mode="w", encoding="utf-8"
            ) as f:
                f.write(code)
                path = f.name
            files_to_cleanup.append(path)

            result = subprocess.run(
                [node, path],
                capture_output=True, text=True, timeout=10,
            )

        # ── JAVA ──────────────────────────────────────────────────────────
        elif lang == "java":
            javac = _find_javac()
            java  = _find_java()

            # Java requires the file name to match the public class name.
            # We wrap the candidate's code in a Main class if they haven't
            # already defined one, and always save as Main.java.
            tmp_dir = tempfile.mkdtemp()
            files_to_cleanup.append(tmp_dir)

            java_path = os.path.join(tmp_dir, "Main.java")

            # ── Detect what the candidate wrote and wrap appropriately ────
            #
            # Case 1: already has a class definition → use as-is
            # Case 2: method definition(s) (contains return type + parens
            #         but no class keyword) → wrap in class, call from main
            # Case 3: bare statements → wrap in class + main()
            #
            import re

            has_class    = bool(re.search(r'\bclass\s+\w+', code))
            has_method   = bool(re.search(
                r'(public|private|protected|static)\s+\S+\s+\w+\s*\(', code
            ))

            if has_class:
                # Full class — use as-is, just make sure it's named Main
                # Replace the first class name with Main so javac is happy
                wrapped = re.sub(
                    r'\bclass\s+\w+', 'class Main', code, count=1
                )

            elif has_method:
                # Method(s) but no class — wrap in Main class.
                # Add a main() that instantiates Main and calls the first
                # method with a sample value so the code actually runs.
                # The candidate can see the output even without a main().
                wrapped = (
                    "import java.util.*;\n"
                    "public class Main {\n"
                    + "\n".join("    " + line for line in code.splitlines())
                    + "\n\n"
                    "    public static void main(String[] args) {\n"
                    "        Main sol = new Main();\n"
                    "        System.out.println(\"Solution loaded. Add test calls or submit.\");\n"
                    "    }\n"
                    "}\n"
                )

            else:
                # Bare statements — wrap in class + main()
                wrapped = (
                    "import java.util.*;\n"
                    "public class Main {\n"
                    "    public static void main(String[] args) {\n"
                    + "\n".join("        " + line for line in code.splitlines())
                    + "\n    }\n}\n"
                )

            with open(java_path, "w", encoding="utf-8") as f:
                f.write(wrapped)

            # Step 1: compile
            compile_result = subprocess.run(
                [javac, java_path],
                capture_output=True, text=True, timeout=15,
            )

            if compile_result.returncode != 0:
                return {
                    "stdout": "",
                    "stderr": compile_result.stderr,
                    "exit_code": compile_result.returncode,
                }

            # Step 2: run
            result = subprocess.run(
                [java, "-cp", tmp_dir, "Main"],
                capture_output=True, text=True, timeout=10,
            )

        # ── UNSUPPORTED ───────────────────────────────────────────────────
        else:
            return {
                "stdout": "",
                "stderr": (
                    f"Language '{language}' is not supported. "
                    "Supported: python, javascript, java."
                ),
                "exit_code": 1,
            }

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": int(result.returncode),
        }

    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": "Execution timed out after 10 seconds.",
            "exit_code": 1,
        }

    except FileNotFoundError as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "exit_code": 1,
        }

    except Exception:
        return {
            "stdout": "",
            "stderr": traceback.format_exc(),
            "exit_code": 1,
        }

    finally:
        # Clean up all temp files / dirs
        for item in files_to_cleanup:
            try:
                if os.path.isdir(item):
                    shutil.rmtree(item, ignore_errors=True)
                elif os.path.exists(item):
                    os.remove(item)
            except OSError:
                pass


if __name__ == "__main__":
    print("MCP Code-Runner starting on http://127.0.0.1:8001/mcp")
    print("Supported languages: python, javascript, java")
    mcp.run(transport="streamable-http")