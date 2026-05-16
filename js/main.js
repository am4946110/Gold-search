const form = document.getElementById("searchForm");
const queryInput = document.getElementById("query");
const statusBox = document.getElementById("status");
const resultsBox = document.getElementById("results");
const submitButton = form.querySelector("button");

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const query = queryInput.value.trim();
  if (!query) {
    setStatus("Search text is required.", true);
    return;
  }

  submitButton.disabled = true;
  setStatus("Searching...");
  resultsBox.replaceChildren();

  try {
    const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
    const contentType = response.headers.get("content-type") || "";
    const responseText = await response.text();

    if (!contentType.includes("application/json")) {
      throw new Error("The page is not connected to the local API. Close this tab, run Run_Web.bat, and use the /web address it opens.");
    }

    const payload = JSON.parse(responseText);

    if (!response.ok || !payload.ok) {
      throw new Error(payload.error || "Search failed.");
    }

    renderResults(payload.results || []);
    setStatus(`${payload.results.length} result${payload.results.length === 1 ? "" : "s"} found.`);
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    submitButton.disabled = false;
  }
});

function setStatus(message, isError = false) {
  statusBox.textContent = message;
  statusBox.classList.toggle("error", isError);
}

function renderResults(results) {
  resultsBox.replaceChildren();

  if (!results.length) {
    setStatus("No results found.");
    return;
  }

  const fragment = document.createDocumentFragment();

  results.forEach((item) => {
    const article = document.createElement("article");
    article.className = "result";

    const title = document.createElement("h2");
    const link = document.createElement("a");
    link.href = item.link || "#";
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = item.title || "Untitled result";
    title.appendChild(link);

    const url = document.createElement("a");
    url.href = item.link || "#";
    url.target = "_blank";
    url.rel = "noopener noreferrer";
    url.textContent = item.link || "";

    const snippet = document.createElement("p");
    snippet.textContent = item.snippet || "";

    article.append(title, url, snippet);
    fragment.appendChild(article);
  });

  resultsBox.appendChild(fragment);
}
