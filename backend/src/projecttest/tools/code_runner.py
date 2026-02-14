import subprocess
import tempfile
import textwrap


def run_code_tool(code: str) -> str:
    """Execute python code and return stdout or error."""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(textwrap.dedent(code))
            filename = f.name

        result = subprocess.run(
            ["python", filename],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode != 0:
            return f"Error:\n{result.stderr}"

        return result.stdout or "No output."

    except Exception as e:
        return f"Execution failed: {str(e)}"
