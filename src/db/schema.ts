import { integer, sqliteTable, text, primaryKey } from "drizzle-orm/sqlite-core";
import { sql } from "drizzle-orm";

export const authSnapshots = sqliteTable("auth_snapshots", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  phone: text("phone").notNull().unique(),
  createdAt: text("created_at")
    .notNull()
    .default(sql`(datetime('now'))`),
  updatedAt: text("updated_at").notNull(),

  // Tokens
  bearerToken: text("bearer_token"),
  firebaseIdToken: text("firebase_id_token"),
  sendbirdToken: text("sendbird_token"),
  pushToken: text("push_token"),

  // IDs
  installId: text("install_id"),
  firebaseUid: text("firebase_uid"),
  identityId: text("identity_id"),
  sessionId: text("session_id"),

  // Metadata
  hingeTokenExpires: integer("hinge_token_expires"),
  lastVersionCode: integer("last_version_code"),
  country: text("country"),
  authState: text("auth_state"),
  lastSigninMethod: text("last_signin_method"),
  userState: integer("user_state"),
  isBanned: integer("is_banned"),

  // Headers
  headerAuthorization: text("header_authorization"),
  headerXBuildNumber: text("header_x_build_number"),
  headerXAppVersion: text("header_x_app_version"),
  headerXInstallId: text("header_x_install_id"),
  headerXSessionId: text("header_x_session_id"),

  // JSON data
  permissionsJson: text("permissions_json"),
  rawSelectedJson: text("raw_selected_json"),
});

export type AuthSnapshot = typeof authSnapshots.$inferSelect;
