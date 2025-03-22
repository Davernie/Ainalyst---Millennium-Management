import { useState } from "react";

function Home() {
  const [username, setUsername] = useState("");
  const [filePath, setFilePath] = useState("");
  const [fileContent, setFileContent] = useState("");
  const [apiResponse, setApiResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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
      };
      reader.readAsText(file);
    }
  };

  const analyzeCode = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setApiResponse(null);

    console.log("Fetching logs for:", username, filePath);

    try {
      const response = await fetch("http://localhost:8080/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          code: fileContent,
          userName: username,
          fileName: filePath,
        }),
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} - ${response.statusText}`);
      }

      const data = await response.json();
      console.log("API Response:", data);

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
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        type="text"
        placeholder="File name or absolute path"
        value={filePath}
        onChange={(e) => setFilePath(e.target.value)}
      />
      
      <div
        className="file-upload-container"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        <p className="file-upload-text">Drag and drop a Python file here</p>
        <input
          type="file"
          accept=".py"
          onChange={handleFileUpload}
          className="file-upload-input"
        />
        <p className="file-upload-text">Or click to select a file</p>
      </div>

      <button onClick={analyzeCode} disabled={loading || (!fileContent && !filePath)}>
        {loading ? "Analyzing..." : "Submit"}
      </button>

      {/* Display API Response */}
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
        </div>
      )}
    </div>
  );
}

export default Home;
