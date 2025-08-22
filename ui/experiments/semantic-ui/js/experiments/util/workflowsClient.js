import { safeFetch } from "./safeFetch";

const API_URL = "http://localhost:8062/api"

export const fetchAvailableWorkflows = async (files) => {
  const data = {
    files
  };

  const response = await safeFetch(`${API_URL}/v1/workflows/available`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  return response;
};

export const createWorkflow = async (recordId, workflowName, files) => {
  const data = {
    recordId,
    name: workflowName,
    files, 
  };

  const response = await safeFetch(`${API_URL}/v1/workflows`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  return response;
}
