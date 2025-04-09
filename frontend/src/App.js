import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from "react-router-dom";
import { JiraProvider, JiraContext } from "./JiraContext";
import Home from "./pages/Home";
import History from "./pages/History";
import JiraLogin from "./pages/JiraLogin";
import MostCommonIssues from './pages/MostCommonIssues';
import logo from "./millennium.svg";
import logo2 from "./AI-nalyst.svg";
import "./App.css";
import { useContext } from "react";

function NavBar() {
  const { jiraEmail } = useContext(JiraContext);
  const navigate = useNavigate();

  return (
    <nav>
      <div className="nav-container">
        <div className="logo-group">
          <Link to="/">
            <img src={logo} alt="Logo" className="nav-logo small-logo" />
          </Link>
          <Link to="/">
            <img src={logo2} alt="AI-nalyst Logo" className="nav-logo big-logo" />
          </Link>
        </div>

        <ul>
          <li><Link to="/home">Home</Link></li>
          <li><Link to="/history">History</Link></li>
          <li><Link to="/mostcommon">Most Common Issues</Link></li>
        </ul>

        {jiraEmail && (
          <div className="jira-user" onClick={() => navigate("/")}>
            {jiraEmail}
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
            <Route path="/mostcommon" element={<MostCommonIssues />} />
          </Routes>
        </div>
      </Router>
    </JiraProvider>
  );
}

export default App;
