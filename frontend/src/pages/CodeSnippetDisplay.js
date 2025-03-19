import { useState } from "react";
// import SyntaxHighlighter from "react-syntax-highlighter";
// import { docco } from "react-syntax-highlighter/dist/esm/styles/hljs";

const CodeSnippetDisplay = () => {
  // State for user inputs
  const [username, setUsername] = useState("");
  const [fileName, setFileName] = useState("");
  const [timestamp, setTimestamp] = useState(new Date().toLocaleString());

  // Simulated flagged issue data
  const [issue, setIssue] = useState({
    code: `function foo() {\n  // TODO: Implement this function\n}`,
    description: "Function 'foo' has an empty body.",
    suggestion: "Consider adding logic inside the function.",
    errors: [
      { line: 1, message: "Function 'foo' is declared but not used." },
      { line: 2, message: "Empty function body detected." },
    ],
  });

  return (
    <div className="page-container">
      <h2>Code Snippet Display</h2>

      {/* User Inputs */}
      <div style={{ marginBottom: "20px" }}>
        <label><strong>Username:</strong></label>
        <input 
          type="text" 
          value={username} 
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Enter your username"
          style={{ width: "100%", padding: "8px", margin: "5px 0", borderRadius: "5px", border: "1px solid #ccc" }}
        />

        <label><strong>File Name:</strong></label>
        <input 
          type="text" 
          value={fileName} 
          onChange={(e) => setFileName(e.target.value)}
          placeholder="Enter file name"
          style={{ width: "100%", padding: "8px", margin: "5px 0", borderRadius: "5px", border: "1px solid #ccc" }}
        />

        <label><strong>Timestamp:</strong></label>
        <input 
          type="text" 
          value={timestamp} 
          disabled
          style={{ width: "100%", padding: "8px", margin: "5px 0", borderRadius: "5px", border: "1px solid #ccc", background: "#f0f0f0" }}
        />
      </div>

      {/* Issue Details */}
      <p><strong>Issue:</strong> {issue.description}</p>

      {/* Code Snippet with Syntax Highlighting */}
      {/* <SyntaxHighlighter language="javascript" style={docco} showLineNumbers>
        {issue.code}
      </SyntaxHighlighter> */}

      {/* Errors & Warnings */}
      <h3>Errors & Warnings:</h3>
      <ul>
        {issue.errors.map((error, index) => (
          <li 
            key={index} 
            style={{ cursor: "pointer", color: "red", fontWeight: "bold" }}>
            ⚠️ Line {error.line}: {error.message}
          </li>
        ))}
      </ul>

      {/* AI Suggestion */}
      <h3>AI Suggestion:</h3>
      <p>{issue.suggestion}</p>
    </div>
  );
};

export default CodeSnippetDisplay;
