import { drizzle } from "drizzle-orm/bun-sqlite";
import { migrate } from "drizzle-orm/bun-sqlite/migrator";
import { Database } from "bun:sqlite";
import { join } from "node:path";
import os from "node:os";

/**
 * Run database migrations using drizzle-kit generated SQL files
 */
export async function runMigrations() {
  const file = join(process.env.HOME || os.homedir(), ".squeaky_hinge.db");
  const sqlite = new Database(file);
  const db = drizzle(sqlite);
  migrate(db, { migrationsFolder: "./drizzle" });
}

// if run directly, execute migrations
if (import.meta.main) {
  runMigrations().catch(console.error);
}
