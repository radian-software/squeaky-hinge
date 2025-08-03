import { drizzle } from "drizzle-orm/bun-sqlite";
import { Database } from "bun:sqlite";
import { join } from "node:path";
import os from "node:os";
import { eq, desc } from "drizzle-orm";
import { authSnapshots, type AuthSnapshot } from "./schema";

let db: ReturnType<typeof drizzle> | null = null;
let sqlite: Database | null = null;

function nowIso() {
  return new Date().toISOString();
}

export function ensureDB() {
  if (db) return db;
  const file = join(process.env.HOME || os.homedir(), ".squeaky_hinge.db");
  sqlite = new Database(file);
  db = drizzle(sqlite);
  return db;
}

export async function saveAuthSnapshot(authRow: AuthSnapshot) {
  const database = ensureDB();
  const existing = await database.select({ id: authSnapshots.id }).from(authSnapshots).where(eq(authSnapshots.phone, authRow.phone)).limit(1);
  const values = {
    ...authRow,
    updatedAt: nowIso(),
  };

  if (existing.length > 0) {
    await database.update(authSnapshots).set(values).where(eq(authSnapshots.id, existing[0]!.id));
  } else {
    await database.insert(authSnapshots).values({
      ...values,
      createdAt: nowIso(),
    });
  }
}

export async function getLatestAuthByPhone(phone: string): Promise<AuthSnapshot | null> {
  const database = ensureDB();
  const rows = await database.select().from(authSnapshots).where(eq(authSnapshots.phone, phone)).orderBy(desc(authSnapshots.createdAt)).limit(1);
  return rows[0] || null;
}
