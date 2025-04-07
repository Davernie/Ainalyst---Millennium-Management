import { useState } from "react";

function Home() {
  const [username, setUsername] = useState("");
  const [filePath, setFilePath] = useState("");
  const [fileContent, setFileContent] = useState("");
  const [apiResponse, setApiResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [mode, setMode] = useState("upload"); // 'upload' or 'path'

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setFileContent(event.target.result);
        setFilePath(file.name);
      };
      reader.readAsText(file);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setFileContent(event.target.result);
        setFilePath(file.name);
      };
      reader.readAsText(file);
    }
  };

  const analyzeCode = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setApiResponse(null);

    try {
      const response = await fetch("http://localhost:8080/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          code: mode === "path" ? null : fileContent,
          userName: username,
          fileName: filePath,
        }),
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} - ${response.statusText}`);
      }

      const data = await response.json();
      setApiResponse(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <h2>Analyze Python Code</h2>
      <form onSubmit={analyzeCode}>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        {/* Mode toggle */}
        <div style={{ display: "flex", gap: "15px" }}>
          <label>
            <input
              type="radio"
              value="upload"
              checked={mode === "upload"}
              onChange={() => setMode("upload")}
            />
            Upload File
          </label>
          <label>
            <input
              type="radio"
              value="path"
              checked={mode === "path"}
              onChange={() => setMode("path")}
            />
            Use File Path
          </label>
        </div>

        {mode === "path" ? (
          <input
            type="text"
            placeholder="Enter absolute file path"
            value={filePath}
            onChange={(e) => setFilePath(e.target.value)}
          />
        ) : (
          <div
            className="file-upload-container"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >
            <p className="file-upload-text">
              {fileContent ? "File Selected" : "Drag & Drop Python File or Click to Choose"}
            </p>
            <input
              type="file"
              accept=".py"
              onChange={handleFileUpload}
              className="file-upload-input"
            />
          </div>
        )}

        <button type="submit" disabled={loading || (mode === "upload" && !fileContent)}>
          {loading ? "Analyzing..." : "Submit"}
        </button>
      </form>

      {error && <p style={{ color: "red" }}>ERROR: {error}</p>}

      {apiResponse && (
        <div>
          <h3>Analysis Results:</h3>
          <p><strong>Status:</strong> {apiResponse.Status}</p>
          <p><strong>Request ID:</strong> {apiResponse.id}</p>
          <p><strong>AST Issues:</strong></p>
          <pre>{JSON.stringify(apiResponse["AST Issues"], null, 2)}</pre>
          <p><strong>PEP8 Issues:</strong></p>
          <pre>{JSON.stringify(apiResponse["PEP8 Issues"], null, 2)}</pre>
          <p><strong>Code Smells:</strong></p>
          <pre>{JSON.stringify(apiResponse["Code Smells"], null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default Home;
