import { useState } from "react";

function History() {
  const [username, setUsername] = useState("");
  const [filePath, setFilePath] = useState("");
  const [log, setLog] = useState(null);

  const fetchLogs = async (e) => {
    e.preventDefault();
    console.log("Fetching logs for:", username, filePath);
    try {
      const response = await fetch('http://127.0.0.1:8000/log/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userName: username, fileLocation: filePath }),
      });
  
      if (response.status === 200) {
        const data = await response.json();
        setLog(data);  // Store the full JSON response
        console.log(data);
      } else {
        setLog('Error: Unable to fetch logs');
        console.error('Error: Unable to fetch logs', response.statusText);
      }
    } catch (error) {
      console.error('Database error', error);
      setLog('Error: Database error');
    }
  };
  

  return (
    <div className="page-container">
      <h2>View Issue Log</h2>
      <form>
      <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
      <input type="text" placeholder="File Path" value={filePath} onChange={(e) => setFilePath(e.target.value)} />
      <button onClick={fetchLogs}>Fetch Logs</button>
      </form>
      {log && (
        <div>
          <h3>Previous Issues:</h3>
          <ul>
            {Array.isArray(log) ? log.map((entry, index) => (
              <li key={index}>
                <strong>{entry.date_and_time}:</strong> {entry.response}
              </li>
            )) : <li>{log}</li>}
          </ul>
        </div>
      )}

    </div>
  );
}

export default History;
