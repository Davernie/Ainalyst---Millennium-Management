import { useState } from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function MostCommonIssues() {
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#f07d70', '#ffcc00'];
  const [username, setUsername] = useState("");
  const [commonIssues, setCommonIssues] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const fetchCommonIssues = async (e) => {
    e.preventDefault();
    if (!username) {
      setError("Please enter a username");
      return;
    }

    setLoading(true);
    setError("");
    setCommonIssues([]);

    const url = "http://localhost:8080/common_issues/" + username;

    try {
      const response = await fetch(url);

      if (!response.ok) {
        const errorText = "Error with status " + response.status.toString();
        setError(errorText);
      }

      const data = await response.json();
      setCommonIssues(data);
    } catch (error) {
      console.error("Failed to fetch common issues, error", error);
      setError("Failed to fetch common issues");
    } finally {
      setLoading(false);
    }
  };

  const renderCustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{ background: 'white', border: '1px solid #ccc', padding: 10 }}>
          <p style={{ margin: 0, fontWeight: 'bold' }}>{payload[0].name}</p>
          <p style={{ margin: 0 }}>Value: {payload[0].value}</p>
        </div>
      );
    }
    return null;
  };

  const renderPieChart = (issues, title) => {
    if (!issues || !Array.isArray(issues) || issues.length === 0) {
      return <p>No {title.toLowerCase()} found</p>;
    }

    const chartData = issues.slice(0, 5).map(([name, value], index) => ({
      name: name, // Full name for tooltip
      displayName: name.length > 20 ? `${name.substring(0, 20)}...` : name, // Short label
      value: value,
      color: COLORS[index % COLORS.length]
    }));

    return (
      <div style={{ width: "100%", height: 400, marginBottom: 20 }}>
        <h3>{title}</h3>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={120}
              label={({ index }) => chartData[index].displayName}
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip content={renderCustomTooltip} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    );
  };

  return (
    <div style={{ maxWidth: 1200, margin: "0 auto", padding: 20 }}>
      <h2>Common Issues Analysis</h2>
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
        <button onClick={fetchCommonIssues} disabled={loading }>
        {loading ? "Analyzing..." : "Get Most Common Issues"}
      </button>

      {error && (
        <div style={{ color: 'red', margin: '10px 0' }}>
          {error}
        </div>
      )}

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 20 }}>
        {commonIssues?.common_AST_Issues &&
          renderPieChart(commonIssues.common_AST_Issues, 'Common AST Issues')}
        {commonIssues?.common_PEP8_Issues &&
          renderPieChart(commonIssues.common_PEP8_Issues, 'Common PEP8 Issues')}
      </div>
    </div>
  );
}

export default MostCommonIssues;
