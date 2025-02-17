import { useState } from "react";

function Home() {
  const [file, setFile] = useState(null);
  const [username, setUsername] = useState("");
  const [filePath, setFilePath] = useState("");

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    console.log("File:", file);
    console.log("Username:", username);
    console.log("File Path:", filePath);
  };

  return (
    <div className="container">
      <h2>Upload a File for Analysis</h2>
      <form onSubmit={handleSubmit}>
        <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
        <input type="text" placeholder="File Path" value={filePath} onChange={(e) => setFilePath(e.target.value)} />
        <input type="file" onChange={handleFileChange} />
        <button type="submit">Upload</button>
      </form>
    </div>
  );
}

export default Home;
