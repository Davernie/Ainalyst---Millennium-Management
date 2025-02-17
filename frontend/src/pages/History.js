import { useState } from "react";

function History() {
  const [username, setUsername] = useState("");
  const [filePath, setFilePath] = useState("");
  const [log, setLog] = useState(null);

  const fetchLogs = () => {
    console.log("Fetching logs for:", username, filePath);
    setLog(["Issue 1: Syntax error", "Issue 2: Deprecated function used"]); // Placeholder data
  };

  return (
    <div>
      <h2>View Issue Log</h2>
      <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
      <input type="text" placeholder="File Path" value={filePath} onChange={(e) => setFilePath(e.target.value)} />
      <button onClick={fetchLogs}>Fetch Logs</button>

      {log && (
        <div>
          <h3>Previous Issues:</h3>
          <ul>
            {log.map((issue, index) => (
              <li key={index}>{issue}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default History;
