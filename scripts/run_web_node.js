const { spawn } = require("child_process");
const path = require("path");

const projectRoot = path.resolve(__dirname, "..");
const batFile = path.join(projectRoot, "Run_Web.bat");
const port = process.argv[2] || "";

const args = ["/c", batFile];
if (port) {
  args.push(port);
}

const child = spawn("cmd.exe", args, {
  cwd: projectRoot,
  stdio: "inherit",
  windowsHide: false,
});

child.on("error", (error) => {
  console.error(`Could not start ${batFile}`);
  console.error(error.message);
  process.exit(1);
});

child.on("exit", (code) => {
  process.exit(code || 0);
});
