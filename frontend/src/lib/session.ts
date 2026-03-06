export type JiraConfig = {
  jiraUrl: string;
  jiraProjectKey: string;
  jiraEmail: string;
  jiraApiToken: string;
  jiraIssueType?: string;
};

type StoredUser = {
  _id: string;
  name: string;
  email: string;
};

const USER_KEY = "user";
const TOKEN_KEY = "token";
const JIRA_KEY = "jiraConfig";

export const loginDemo = (email: string) => {
  const fakeUser: StoredUser = {
    _id: `user_${Date.now()}`,
    name: email.split("@")[0] || "User",
    email
  };
  const payload = { id: fakeUser._id, exp: Date.now() / 1000 + 60 * 60 * 24 };
  const token = btoa(JSON.stringify(payload));

  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(fakeUser));
  return fakeUser;
};

export const logout = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
};

export const isAuthenticated = () => Boolean(localStorage.getItem(TOKEN_KEY));

export const getUser = (): StoredUser | null => {
  const stored = localStorage.getItem(USER_KEY);
  if (!stored) return null;
  try {
    return JSON.parse(stored) as StoredUser;
  } catch {
    return null;
  }
};

export const getJiraConfig = (): JiraConfig | null => {
  const stored = localStorage.getItem(JIRA_KEY);
  if (!stored) return null;
  try {
    return JSON.parse(stored) as JiraConfig;
  } catch {
    return null;
  }
};

export const saveJiraConfig = (config: JiraConfig) => {
  const normalized = {
    jiraUrl: config.jiraUrl.trim().replace(/\/$/, ""),
    jiraProjectKey: config.jiraProjectKey.trim().toUpperCase(),
    jiraEmail: config.jiraEmail.trim(),
    jiraApiToken: config.jiraApiToken.trim(),
    jiraIssueType: (config.jiraIssueType || "Task").trim()
  };
  localStorage.setItem(JIRA_KEY, JSON.stringify(normalized));
  return normalized;
};

export const hasJiraConfig = () => {
  const config = getJiraConfig();
  return Boolean(
    config &&
      config.jiraUrl &&
      config.jiraProjectKey &&
      config.jiraEmail &&
      config.jiraApiToken
  );
};
