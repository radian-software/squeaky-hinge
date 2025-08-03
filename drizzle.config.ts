import { defineConfig } from "drizzle-kit";
import { join } from "node:path";
import os from "node:os";

export default defineConfig({
  schema: "./src/db/schema.ts",
  out: "./drizzle",
  dialect: "sqlite",
  dbCredentials: {
    url: join(process.env.HOME || os.homedir(), ".squeaky_hinge.db"),
  },
});
