const API_BASE = "http://127.0.0.1:8000";

export async function verifyUser(username: string) {
  const res = await fetch(`${API_BASE}/user/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username }),
  });

  if (!res.ok) {
    throw new Error("User verification failed");
  }

  return res.json();
}

export async function submitTextPreferences(username: string, text: string) {
  const res = await fetch(`${API_BASE}/preferences/text`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, text }),
  });

  if (!res.ok) {
    throw new Error("Text preference failed");
  }

  return res.json();
}

export async function submitMovieLists(
  username: string,
  liked: string[],
  disliked: string[]
) {
  const res = await fetch(`${API_BASE}/preferences/list`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, liked, disliked }),
  });

  if (!res.ok) {
    throw new Error("Movie list submission failed");
  }

  return res.json();
}
