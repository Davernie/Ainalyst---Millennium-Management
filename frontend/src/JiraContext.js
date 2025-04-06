import { createContext, useState } from "react";

export const JiraContext = createContext();

export function JiraProvider({ children }) {
  const [jiraUser, setJiraUser] = useState("");
  const [jiraToken, setJiraToken] = useState("");

  return (
    <JiraContext.Provider value={{ jiraUser, setJiraUser, jiraToken, setJiraToken }}>
      {children}
    </JiraContext.Provider>
  );
}