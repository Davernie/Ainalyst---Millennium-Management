import { useState } from "react";

function History() {
  const [replies, setReplies] = useState([]); // Store multiple responses
  const [username, setUsername] = useState("");
  const [filePath, setFilePath] = useState("");
  const [error, setError] = useState(""); // State to store error message
  const [loading, setLoading] = useState(false); // State to track loading status

  const fetchLogs = async (e) => {
    e.preventDefault(); // Prevent form reload

    if (!username || !filePath) {
      setError("Please enter both Username and File Path.");
      return;
    }

    setLoading(true); // Set loading to true before fetching
    setError(""); // Reset previous errors
    setReplies([]); // Clear previous results

    const url = "http://localhost:8080/getresponse/";

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          userName: username, // Match FastAPI's expected request field names
          fileName: filePath,
        }),
      });

      if (response.ok) {
        const data = await response.json();

        if (data.length > 0 && data[0].id !== "N/A") {
          setReplies(data); // Store all responses
          setError(""); // Clear any previous error
          console.log("Response:", data);
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
      setLoading(false); // Reset loading state after fetching
    }
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
          {replies.map((reply, index) => (
            <div key={index} style={{ marginBottom: "20px", border: "1px solid #ccc", padding: "10px" }}>
              <ul>
                <li><strong>Timestamp:</strong> {reply.timestamp}</li>
                <li><strong>ID:</strong> {reply.id}</li>
                <li><strong>Response:</strong> {reply.report_response}</li>
                {/* Uncomment when Code Smells API is available */}
                {/* <li><strong>Code Smells:</strong> {reply.report_response["Code Smells"]}</li> */}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default History;