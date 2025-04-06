import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from "react-router-dom";
import { JiraProvider, JiraContext } from "./JiraContext";
import Home from "./pages/Home";
import History from "./pages/History";
import JiraLogin from "./pages/JiraLogin";
import logo from "./logo.svg";
import logo2 from "./AI-nalyst.svg";
import "./App.css";
import { useContext } from "react";

function NavBar() {
  const { jiraUser } = useContext(JiraContext);
  const navigate = useNavigate();

  return (
    <nav>
      <div className="nav-container">
        <div className="logo-group">
          <img src={logo} alt="Logo" className="nav-logo small-logo" />
          <img src={logo2} alt="AI-nalyst Logo" className="nav-logo big-logo" />
        </div>

        <ul>
          <li><Link to="/home">Home</Link></li>
          <li><Link to="/history">History</Link></li>
        </ul>

        {jiraUser && (
          <div className="jira-user" onClick={() => navigate("/")}>
            {jiraUser}
          </div>
        )}
      </div>
    </nav>
  );
}

function App() {
  return (
    <JiraProvider>
      <Router>
        <NavBar />
        <div className="app">
          <Routes>
            <Route path="/" element={<JiraLogin />} />
            <Route path="/home" element={<Home />} />
            <Route path="/history" element={<History />} />
          </Routes>
        </div>
      </Router>
    </JiraProvider>
  );
}

export default App;
