import { useState } from "react";
import ReactMarkdown from "react-markdown";

function History() {
  const [replies, setReplies] = useState([]);
  const [username, setUsername] = useState("");
  const [filePath, setFilePath] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const fetchLogs = async (e) => {
    e.preventDefault();

    if (!username || !filePath) {
      setError("Please enter both Username and File Path.");
      return;
    }

    setLoading(true);
    setError("");
    setReplies([]);

    const url = "http://localhost:8080/getresponse/";

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          userName: username,
          fileName: filePath,
        }),
      });

      if (response.ok) {
        const data = await response.json();

        if (data.length > 0 && data[0].id !== "N/A") {
          const parsedReplies = data.map(reply => {
            return {
              ...reply,
              report_response: JSON.parse(reply.report_response)
            };
          });

          setReplies(parsedReplies);
          setError("");
        } else {
          setError("No logs found for the given Username and File Path.");
        }
      } else {
        setError("Error: Unable to fetch logs.");
      }
    } catch (error) {
      console.error("Database error:", error);
      setError("Error: Database error.");
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
      <h2>View Issue Log</h2>
      <form onSubmit={fetchLogs}>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="text"
          placeholder="File Path"
          value={filePath}
          onChange={(e) => setFilePath(e.target.value)}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Fetching..." : "Fetch Logs"}
        </button>
      </form>

      {error && <div style={{ color: "red" }}><strong>{error}</strong></div>}

      {replies.length > 0 && (
        <div>
          <h3>Issue Reports:</h3>
          {replies.map((reply, index) => {
            const astIssues = reply.report_response["AST Issues"];
            const pep8Issues = reply.report_response["PEP8 Issues"];
            const boxColor = getBoxBackgroundColor(astIssues, pep8Issues);

            return (
              <div
                key={index}
                style={{
                  marginBottom: "20px",
                  border: "1px solid #ccc",
                  padding: "10px",
                  backgroundColor: boxColor,
                  whiteSpace: "pre-wrap",
                }}
              >
                <strong>Timestamp:</strong> {reply.timestamp}<br />
                <strong>ID:</strong> {reply.id}<br />
                <strong>AST Issues:</strong>
                {Array.isArray(astIssues) ? (
                  astIssues.map((issue, idx) => (
                    <div key={idx}>{issue}</div>
                  ))
                ) : (
                  <div>{astIssues}</div>
                )}
                <br />
                <strong>PEP8 Issues:</strong> {pep8Issues}<br />
                <strong>Code Smells:</strong> <ReactMarkdown>{reply.report_response["Code Smells"]}</ReactMarkdown>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default History;
