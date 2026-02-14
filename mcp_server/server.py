"""
MCP Code-Runner Server
======================
Runs as a standalone HTTP server on port 8001.
Start it with:  python server.py
MCP endpoint:   http://127.0.0.1:8001/mcp

Supported languages: python, javascript, java, csharp, cpp
"""

from mcp.server.fastmcp import FastMCP
import subprocess
import tempfile
import shutil
import os
import sys
import traceback
import platform

mcp = FastMCP(
    "code-runner",
    host="127.0.0.1",
    port=8001,
    stateless_http=True,
)

# ─────────────────────────────────────────────────────────────────────────────
#  Compiler/Runtime Finders
# ─────────────────────────────────────────────────────────────────────────────

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

def _find_csc() -> str:
    """Find C# compiler (csc on Windows, mcs/csc on Linux/Mac)"""
    found = shutil.which("csc") or shutil.which("mcs")
    if not found:
        raise FileNotFoundError(
            "C# compiler not found. Install .NET SDK or Mono"
        )
    return found

def _find_cpp_compiler() -> str:
    """Find C++ compiler (g++ or clang++)"""
    found = shutil.which("g++") or shutil.which("clang++")
    if not found:
        raise FileNotFoundError(
            "C++ compiler not found. Install g++ or clang++"
        )
    return found


@mcp.tool()
def run_code(language: str, code: str) -> dict:
    """
    Execute candidate code in a sandboxed subprocess.

    Args:
        language: One of 'python', 'javascript', 'java', 'csharp', 'cpp'.
        code:     The source code string to execute.

    Returns:
        dict with stdout, stderr, and exit_code.
    """
    lang = language.strip().lower()
    files_to_cleanup = []

    try:
        import re

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

            tmp_dir = tempfile.mkdtemp()
            files_to_cleanup.append(tmp_dir)
            java_path = os.path.join(tmp_dir, "Main.java")

            has_class    = bool(re.search(r'\bclass\s+\w+', code))
            has_method   = bool(re.search(
                r'(public|private|protected|static)\s+\S+\s+\w+\s*\(', code
            ))

            if has_class:
                wrapped = re.sub(r'\bclass\s+\w+', 'class Main', code, count=1)
            elif has_method:
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
                wrapped = (
                    "import java.util.*;\n"
                    "public class Main {\n"
                    "    public static void main(String[] args) {\n"
                    + "\n".join("        " + line for line in code.splitlines())
                    + "\n    }\n}\n"
                )

            with open(java_path, "w", encoding="utf-8") as f:
                f.write(wrapped)

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

            result = subprocess.run(
                [java, "-cp", tmp_dir, "Main"],
                capture_output=True, text=True, timeout=10,
            )

        # ── C# ────────────────────────────────────────────────────────────
        elif lang in ("csharp", "c#", "cs"):
            csc = _find_csc()
            
            tmp_dir = tempfile.mkdtemp()
            files_to_cleanup.append(tmp_dir)
            cs_path = os.path.join(tmp_dir, "Program.cs")
            exe_path = os.path.join(tmp_dir, "Program.exe")

            # Detect what was written
            has_class = bool(re.search(r'\bclass\s+\w+', code))
            has_method = bool(re.search(
                r'(public|private|protected|static|internal)\s+\S+\s+\w+\s*\(', code
            ))
            has_namespace = bool(re.search(r'\bnamespace\s+\w+', code))

            if has_namespace or (has_class and 'Main' in code):
                # Full program - use as-is
                wrapped = code
            elif has_class:
                # Has class but no Main - wrap in namespace and add Main
                wrapped = (
                    "using System;\n"
                    "using System.Collections.Generic;\n"
                    "using System.Linq;\n\n"
                    + code + "\n\n"
                    "class Program {\n"
                    "    static void Main() {\n"
                    "        Console.WriteLine(\"Solution loaded. Add test calls or submit.\");\n"
                    "    }\n"
                    "}\n"
                )
            elif has_method:
                # Method(s) only - wrap in class with Main
                wrapped = (
                    "using System;\n"
                    "using System.Collections.Generic;\n"
                    "using System.Linq;\n\n"
                    "class Solution {\n"
                    + "\n".join("    " + line for line in code.splitlines())
                    + "\n}\n\n"
                    "class Program {\n"
                    "    static void Main() {\n"
                    "        Solution sol = new Solution();\n"
                    "        Console.WriteLine(\"Solution loaded. Add test calls or submit.\");\n"
                    "    }\n"
                    "}\n"
                )
            else:
                # Bare statements - wrap in Main
                wrapped = (
                    "using System;\n"
                    "using System.Collections.Generic;\n"
                    "using System.Linq;\n\n"
                    "class Program {\n"
                    "    static void Main() {\n"
                    + "\n".join("        " + line for line in code.splitlines())
                    + "\n    }\n}\n"
                )

            with open(cs_path, "w", encoding="utf-8") as f:
                f.write(wrapped)

            # Compile
            compile_cmd = [csc, f"/out:{exe_path}", cs_path]
            if platform.system() != "Windows":
                compile_cmd = [csc, f"-out:{exe_path}", cs_path]
            
            compile_result = subprocess.run(
                compile_cmd,
                capture_output=True, text=True, timeout=15,
            )

            if compile_result.returncode != 0:
                return {
                    "stdout": "",
                    "stderr": compile_result.stderr,
                    "exit_code": compile_result.returncode,
                }

            # Run
            run_cmd = [exe_path] if platform.system() == "Windows" else ["mono", exe_path]
            if platform.system() != "Windows" and not shutil.which("mono"):
                run_cmd = ["dotnet", exe_path.replace(".exe", ".dll")]
            
            result = subprocess.run(
                run_cmd,
                capture_output=True, text=True, timeout=10,
            )

        # ── C++ ───────────────────────────────────────────────────────────
        elif lang in ("cpp", "c++", "cxx"):
            compiler = _find_cpp_compiler()
            
            tmp_dir = tempfile.mkdtemp()
            files_to_cleanup.append(tmp_dir)
            cpp_path = os.path.join(tmp_dir, "main.cpp")
            exe_path = os.path.join(tmp_dir, "main.exe" if platform.system() == "Windows" else "main")

            # Detect what was written
            has_main = bool(re.search(r'\bint\s+main\s*\(', code))
            has_function = bool(re.search(
                r'\b(void|int|float|double|bool|char|string|auto)\s+\w+\s*\([^)]*\)\s*\{', code
            ))

            if has_main:
                # Full program with main - use as-is
                wrapped = (
                    "#include <iostream>\n"
                    "#include <vector>\n"
                    "#include <string>\n"
                    "#include <algorithm>\n"
                    "using namespace std;\n\n"
                    + code
                )
            elif has_function:
                # Function(s) only - wrap with main
                wrapped = (
                    "#include <iostream>\n"
                    "#include <vector>\n"
                    "#include <string>\n"
                    "#include <algorithm>\n"
                    "using namespace std;\n\n"
                    + code + "\n\n"
                    "int main() {\n"
                    "    cout << \"Solution loaded. Add test calls or submit.\" << endl;\n"
                    "    return 0;\n"
                    "}\n"
                )
            else:
                # Bare statements - wrap in main
                wrapped = (
                    "#include <iostream>\n"
                    "#include <vector>\n"
                    "#include <string>\n"
                    "#include <algorithm>\n"
                    "using namespace std;\n\n"
                    "int main() {\n"
                    + "\n".join("    " + line for line in code.splitlines())
                    + "\n    return 0;\n}\n"
                )

            with open(cpp_path, "w", encoding="utf-8") as f:
                f.write(wrapped)

            # Compile
            compile_result = subprocess.run(
                [compiler, cpp_path, "-o", exe_path, "-std=c++17"],
                capture_output=True, text=True, timeout=15,
            )

            if compile_result.returncode != 0:
                return {
                    "stdout": "",
                    "stderr": compile_result.stderr,
                    "exit_code": compile_result.returncode,
                }

            # Run
            result = subprocess.run(
                [exe_path],
                capture_output=True, text=True, timeout=10,
            )

        # ── UNSUPPORTED ───────────────────────────────────────────────────
        else:
            return {
                "stdout": "",
                "stderr": (
                    f"Language '{language}' is not supported. "
                    "Supported: python, javascript, java, csharp, cpp."
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
    print("Supported languages: python, javascript, java, csharp, cpp")
    mcp.run(transport="streamable-http")
