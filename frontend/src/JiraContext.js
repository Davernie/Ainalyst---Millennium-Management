import { createContext, useState } from "react";

export const JiraContext = createContext();

export function JiraProvider({ children }) {
  // State to hold Jira credentials
  const [jiraServer, setJiraServer] = useState("");
  const [jiraEmail, setJiraEmail] = useState("");
  const [jiraApiToken, setJiraApiToken] = useState("");
  const [branchName, setBranchName] = useState("");

  return (
    <JiraContext.Provider
      value={{
        jiraServer,
        setJiraServer,
        jiraEmail,
        setJiraEmail,
        jiraApiToken,
        setJiraApiToken,
        branchName,
        setBranchName,
      }}
    >
      {children}
    </JiraContext.Provider>
  );
}
