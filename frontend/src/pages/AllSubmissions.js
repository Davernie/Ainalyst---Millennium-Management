import { useState } from "react";
import ReactMarkdown from "react-markdown";

function AllSubmissions() {
  const [replies, setReplies] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const getAllSubs = async (e) => {
    e.preventDefault();


    setLoading(true);
    setError("");
    setReplies([]);

    const url = "http://localhost:8080/responses";

    try {
      const response = await fetch(url);

      if (response.ok) {
        const data = await response.json();

        if (data.length > 0 && data[0].id !== "N/A") {
          const parsedReplies = data.map(reply => {
            return {
              ...reply,
              report_response: JSON.parse(JSON.stringify(reply.report_response))
            };
          });

          setReplies(parsedReplies);
          setError("");
        } else {
          setError("No logs found");
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
      const astIssuesArray = Array.isArray(astIssues) ? astIssues : [astIssues];
      const pep8IssuesArray = Array.isArray(pep8Issues) ? pep8Issues : [pep8Issues];

      if (
        astIssuesArray.some(issue => typeof issue === "string" && issue.includes("Error")) ||
        pep8IssuesArray.some(issue => typeof issue === "string" && issue.includes("Error"))
      ) {
        return "lightcoral"; // Light red background
      } else if (
        astIssuesArray.some(issue => typeof issue === "string" && issue.includes("Warning")) ||
        pep8IssuesArray.some(issue => typeof issue === "string" && issue.includes("Warning"))
      ) {
        return "lightyellow"; // Light yellow background
      }
      return "transparent";
    };


  return (
    <div className="page-container">
      <h2>View All Submissions</h2>
      <form onSubmit={getAllSubs}>
        <button type="submit" disabled={loading}>
          {loading ? "Fetching..." : "Fetch All Submissions"}
        </button>
      </form>

      {replies.length > 0 && (
        <div>
          <h3>Issue Reports:</h3>
          {[...replies].reverse().map((reply, index) => {
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

export default AllSubmissions;
