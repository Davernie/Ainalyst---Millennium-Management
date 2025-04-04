import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Home from "./pages/Home";
import History from "./pages/History";
import CodeSnippetDisplay from './pages/CodeSnippetDisplay';
import logo from "./logo.svg"; 
import logo2 from "./AI-nalyst.svg"; 
import "./App.css";

function App() {
  return (
    <Router>
      <nav>
        <div className="nav-container">
        <div className="logo-group">
            <img src={logo} alt="Logo" className="nav-logo small-logo" />
            <img src={logo2} alt="AI-nalyst Logo" className="nav-logo big-logo" />
          </div>

          <ul>
            <li><Link to="/">Home</Link></li>
            <li><Link to="/history">History</Link></li> 
          </ul>
          
        </div>
      </nav>

      <div className="app">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/history" element={<History />} />
          <Route path="/snippet" element={<CodeSnippetDisplay />} />
        </Routes>
      </div>
      
    </Router>
  );
}

export default App;

