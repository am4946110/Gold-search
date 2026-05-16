if (typeof require === "function" && typeof process !== "undefined") {
  require("./scripts/run_web_node");
} else {
  window.addEventListener("DOMContentLoaded", () => {
    const statusBox = document.getElementById("status");

    if (statusBox) {
      statusBox.textContent = "./Run_Web.bat";
      statusBox.classList.add("error");
    }
  });
}
