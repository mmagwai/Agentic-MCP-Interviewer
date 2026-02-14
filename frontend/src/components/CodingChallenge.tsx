import { useState } from "react";
import Editor from "@monaco-editor/react";
import { gradeCodeApi } from "../services/api";

interface Props {
  challenge: string;
  language: string;
}

// ─────────────────────────────────────────────────────────────────────────────
//  Maps the selected_tech string from the CV to:
//    monacoLang  - language ID for Monaco editor syntax highlighting
//    serverLang  - language string sent to the MCP server run_code tool
//    starter     - default code shown in the editor
//
//  Supported runtimes on this machine: python, javascript (node), java
// ─────────────────────────────────────────────────────────────────────────────

interface LangConfig {
  monacoLang: string;
  serverLang: string;
  starter: string;
}

function mapTechToConfig(tech: string): LangConfig {
  const t = tech.toLowerCase();

  if (t.includes("python")) {
    return {
      monacoLang: "python",
      serverLang: "python",
      starter: "# Write your solution here\n\n",
    };
  }

  if (t.includes("javascript") || t.includes("node") || t.includes("react") || t.includes("vue") || t.includes("angular")) {
    return {
      monacoLang: "javascript",
      serverLang: "javascript",
      starter: "// Write your solution here\n\n",
    };
  }

  if (t.includes("java") && !t.includes("javascript")) {
    return {
      monacoLang: "java",
      serverLang: "java",
      // The MCP server auto-wraps bare code in a Main class,
      // but we show a full template so the candidate knows the structure.
      starter:
        "public class Main {\n" +
        "    public static void main(String[] args) {\n" +
        "        // Write your solution here\n" +
        "    }\n" +
        "}\n",
    };
  }

  // Fallback — unsupported runtime, editor still works but Run will error
  return {
    monacoLang: "plaintext",
    serverLang: t,
    starter: "// Write your solution here\n\n",
  };
}

export default function CodingChallenge({ challenge, language }: Props) {
  const config = mapTechToConfig(language);

  const [code, setCode] = useState(config.starter);
  const [result, setResult] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [runOutput, setRunOutput] = useState("");

  if (!challenge) return null;

  // ================= RUN =================
  const runCode = async () => {
    setRunOutput("Running...\n");

    try {
      const res = await fetch("http://127.0.0.1:8000/run-code", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          language: config.serverLang,
          code,
        }),
      });

      const data = await res.json();

      let output = "";
      if (data.stdout) output += data.stdout;
      if (data.stderr) output += "\nERROR:\n" + data.stderr;
      if (!output) output = "Program finished with no output.";
      output += `\n\nExit code: ${data.exit_code}`;

      setRunOutput(output);
    } catch (err) {
      setRunOutput("Execution failed — is the backend running?");
    }
  };

  // ================= SUBMIT =================
  const submit = async () => {
    setLoading(true);
    try {
      const res = await gradeCodeApi(challenge, code, "");
      setResult(res);
    } catch {
      alert("Grading failed");
    }
    setLoading(false);
  };

  // ================= RESULT SCREEN =================
  if (result) {
    return (
      <div className="section">
        <h2>Challenge Result</h2>
        <div className="gradeCard">
          <p>Score: {result.score}</p>
          <p className={result.verdict === "pass" ? "pass" : "fail"}>
            {result.verdict?.toUpperCase()}
          </p>
          <p>{result.feedback}</p>
        </div>
      </div>
    );
  }

  // ================= EDITOR SCREEN =================
  return (
    <div className="section">
      <h2>Coding Challenge</h2>

      <pre style={{ background: "#111", color: "#0f0" }}>
        {challenge}
      </pre>

      {/* Monaco Editor */}
      <Editor
        height="45vh"
        width="100%"
        language={config.monacoLang}
        value={code}
        onChange={(v) => setCode(v || "")}
        theme="vs-dark"
      />

      {/* BUTTONS */}
      <div style={{ display: "flex", gap: "10px", marginTop: "15px" }}>
        <button onClick={runCode}>Run Code</button>
        <button onClick={submit} className="primaryButton">
          Submit
        </button>
      </div>

      {/* TERMINAL OUTPUT */}
      {runOutput && (
        <div
          style={{
            marginTop: "15px",
            background: "#000",
            color: "#0f0",
            padding: "10px",
            minHeight: "120px",
            fontFamily: "monospace",
            whiteSpace: "pre-wrap",
          }}
        >
          {runOutput}
        </div>
      )}

      {loading && <p>Working...</p>}
    </div>
  );
}
