export function promptForInput(q: string): Promise<string> {
  return new Promise((resolve) => {
    process.stdout.write(q);
    process.stdin.resume();
    process.stdin.setEncoding("utf8");
    process.stdin.once("data", (d) => {
      process.stdin.pause();
      resolve(d.toString("utf8").trim());
    });
  });
}
