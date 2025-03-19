import React from 'react';
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/esm/styles/hljs';

const sampleCode = `
function foo() {
  // TODO: Implement this function
}
`;

const CodeSnippetDisplay = () => {
    return (
        <div style={{ padding: '20px' }}>
            <h1>Code Snippet Display</h1>
            <p>Issue: Function 'foo' has an empty body.</p>
            
            <SyntaxHighlighter language="javascript" style={docco}>
                {sampleCode}
            </SyntaxHighlighter>

            <p><strong>Suggestion:</strong> Consider adding logic inside the function.</p>
        </div>
    );
};

export default CodeSnippetDisplay;
