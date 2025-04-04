import React from 'react';

function CodeSnippetDisplay() {
  return (
    <div style={{ padding: '2rem' }}>
      <h2>Code Snippet Display</h2>
      <p>When a flagged issue is selected, the relevant code snippet and suggestions will be shown here.</p>
      {/* Later you'll dynamically show snippet, issue description, and AI suggestion */}
    </div>
  );
}

export default CodeSnippetDisplay;
