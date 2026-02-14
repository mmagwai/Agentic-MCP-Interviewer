from crewai.tools import BaseTool
import subprocess
import tempfile
import os


class RunCodeTool(BaseTool):
    name: str = "run_code"
    description: str = "Executes Python code and returns the output."

    def _run(self, code: str) -> str:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
                f.write(code.encode())
                temp_path = f.name

            result = subprocess.run(
                ["python", temp_path],
                capture_output=True,
                text=True,
                timeout=5
            )

            os.remove(temp_path)

            if result.returncode != 0:
                return result.stderr

            return result.stdout

        except Exception as e:
            return str(e)
