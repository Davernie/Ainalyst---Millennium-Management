import { useState } from "react";

function Home() {
  const [username, setUsername] = useState("");
  const [filePath, setFilePath] = useState("");
  const [fileContent, setFileContent] = useState("");
  const [apiResponse, setApiResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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

  const getBoxBackgroundColor = (astIssues, pep8Issues) => {
    // Ensure astIssues and pep8Issues are arrays
    const astIssuesArray = Array.isArray(astIssues) ? astIssues : [astIssues];
    const pep8IssuesArray = Array.isArray(pep8Issues) ? pep8Issues : [pep8Issues];

    if (astIssuesArray.some(issue => issue.includes("Error")) || pep8IssuesArray.some(issue => issue.includes("Error"))) {
      return "lightcoral"; // Light red background
    } else if (astIssuesArray.some(issue => issue.includes("Warning")) || pep8IssuesArray.some(issue => issue.includes("Warning"))) {
      return "lightyellow"; // Light yellow background
    }
    return "transparent";
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
        placeholder="File name"
        value={filePath}
        onChange={(e) => setFilePath(e.target.value)}
      />
      <input type="file" accept=".py" onChange={handleFileUpload} />
      <button onClick={analyzeCode} disabled={loading || !fileContent}>
        {loading ? "Analyzing..." : "Submit"}
      </button>

      {error && <p style={{ color: "red" }}>ERROR: {error}</p>}
      {apiResponse && (
        <div>
          <h3>Analysis Results:</h3>
          <div
            style={{
              marginBottom: "20px",
              border: "1px solid #ccc",
              padding: "10px",
              backgroundColor: getBoxBackgroundColor(
                apiResponse["AST Issues"],
                apiResponse["PEP8 Issues"]
              ),
              whiteSpace: "pre-wrap",
            }}
          >
            <p><strong>Status:</strong> {apiResponse.Status}</p>
            <p><strong>Request ID:</strong> {apiResponse.id}</p>
            <strong>AST Issues:</strong>
            {Array.isArray(apiResponse["AST Issues"]) ? (
              apiResponse["AST Issues"].map((issue, idx) => (
                <div key={idx}>{issue}</div>
              ))
            ) : (
              <div>{apiResponse["AST Issues"]}</div>
            )}
            <br />
            {Array.isArray(apiResponse["PEP8 Issues"]) ? (
              apiResponse["PEP8 Issues"].map((issue, idx) => (
                <div key={idx}>{issue}</div>
              ))
            ) : (
              <div>{apiResponse["PEP8 Issues"]}</div>
            )}
            <br />
            <strong>Code Smells:</strong> {apiResponse["Code Smells"]}
          </div>
        </div>
      )}
    </div>
  );
}

export default Home;
