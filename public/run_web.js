window.addEventListener("DOMContentLoaded", () => {
  const statusBox = document.getElementById("status");

  if (statusBox && location.protocol === "file:") {
    statusBox.textContent = "Run E:\\pyGetDate\\Run_Web.bat and use the /web page it opens.";
    statusBox.classList.add("error");
  }
});
