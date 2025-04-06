import { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import { JiraContext } from "../JiraContext";

function JiraLogin() {
  const { setJiraUser, setJiraToken } = useContext(JiraContext);
  const [username, setUsername] = useState("");
  const [token, setToken] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    setJiraUser(username);
    setJiraToken(token);
    navigate("/home"); // go to Home after submitting
  };

  return (
    <div className="page-container">
      <h2>Enter Jira Credentials</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Jira Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Jira Token"
          value={token}
          onChange={(e) => setToken(e.target.value)}
          required
        />
        <button type="submit">Submit</button>
      </form>
    </div>
  );
}

export default JiraLogin;
