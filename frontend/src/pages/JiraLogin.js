import { useState } from "react";
import { useNavigate } from "react-router-dom";

function JiraLogin() {
  const [jiraServer, setJiraServer] = useState("");
  const [jiraEmail, setJiraEmail] = useState("");
  const [jiraApiToken, setJiraApiToken] = useState("");
  const [issueKey, setIssueKey] = useState("");
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      // Prepare the credentials payload
      const credentials = {
        jiraServer,
        jiraEmail,
        jiraApiToken,
        issueKey,
      };

      // Make the API call to the backend
      const response = await fetch("http://localhost:8080/update-env", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        throw new Error("Failed to update environment variables");
      }

      const data = await response.json();

      if (data.message) {
        navigate("/home"); // Go to Home after submitting
      } else {
        setError("Something went wrong.");
      }
    } catch (error) {
      console.error("Error:", error);
      setError(error.message || "An unexpected error occurred.");
    }
  };

  return (
    <div className="page-container">
      <h2>Enter Jira Credentials</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Jira Server URL"
          value={jiraServer}
          onChange={(e) => setJiraServer(e.target.value)}
        />
        <input
          type="email"
          placeholder="Jira Email"
          value={jiraEmail}
          onChange={(e) => setJiraEmail(e.target.value)}
        />
        <input
          type="text"
          placeholder="Jira API Token"
          value={jiraApiToken}
          onChange={(e) => setJiraApiToken(e.target.value)}
        />
        <input
          type="text"
          placeholder="Jira Branch Name"
          value={issueKey}
          onChange={(e) => setIssueKey(e.target.value)}
        />
        <button type="submit">Submit</button>
      </form>

      {error && <p style={{ color: "red" }}>{error}</p>} {/* Display error message if any */}
    </div>
  );
}

export default JiraLogin;
