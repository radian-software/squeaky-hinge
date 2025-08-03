import { XMLParser } from "fast-xml-parser";
import { $ } from "bun";
import type { AuthSnapshot } from "./db/schema";

function parseXMLToAuthRow(parsed: any, phone: string): AuthSnapshot {
  // Android SharedPreferences exported as:
  // <map><string name="x">v</string> <int name="y" value="1"/> <set name="Z"><string>...</string></set> ...
  const map = parsed?.map;
  const prefs: Record<string, any> = {};

  const handleEntry = (entry: any, type: string) => {
    if (entry == null) return;
    if (Array.isArray(entry)) {
      for (const e of entry) handleEntry(e, type);
      return;
    }

    const name = entry["@_name"];
    if (!name) return;

    switch (type) {
      case "string": {
        const text = typeof entry["#text"] === "string" ? entry["#text"] : entry["#text"] ?? "";
        prefs[name] = text;
        break;
      }
      case "int":
      case "long": {
        const v = Number(entry["@_value"]);
        prefs[name] = Number.isFinite(v) ? v : 0;
        break;
      }
      case "boolean": {
        prefs[name] = String(entry["@_value"]).toLowerCase() === "true";
        break;
      }
      case "float": {
        const v = Number(entry["@_value"]);
        prefs[name] = Number.isFinite(v) ? v : 0;
        break;
      }
      case "set": {
        const inner = entry["string"];
        let values: string[] = [];
        if (Array.isArray(inner)) {
          values = inner.map((s: any) => (typeof s === "string" ? s : s?.["#text"] ?? "")).filter((s: any) => typeof s === "string");
        } else if (typeof inner === "string") {
          values = [inner];
        } else if (inner && typeof inner === "object" && typeof inner["#text"] === "string") {
          values = [inner["#text"]];
        }
        prefs[name] = values;
        break;
      }
    }
  };

  handleEntry(map["string"], "string");
  handleEntry(map["int"], "int");
  handleEntry(map["long"], "long");
  handleEntry(map["boolean"], "boolean");
  handleEntry(map["float"], "float");
  handleEntry(map["set"], "set");

  return convertPrefsToAuthRow(prefs, phone);
}

function boolToInt(v: any): number | null {
  if (typeof v === "boolean") return v ? 1 : 0;
  if (v === 0 || v === 1) return v;
  return null;
}

function convertPrefsToAuthRow(prefs: Record<string, any>, phone: string): AuthSnapshot {
  return {
    id: 0, // placeholder id, should be set by database
    phone,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    bearerToken: prefs.bearerToken ?? null,
    firebaseIdToken: prefs.firebaseIdToken ?? null,
    sendbirdToken: prefs.sendBirdToken ?? null,
    pushToken: prefs.pushToken ?? null,
    installId: prefs.installId ?? null,
    firebaseUid: prefs.firebaseUid ?? null,
    identityId: prefs.identityId ?? null,
    sessionId: prefs.sessionId ?? null,
    hingeTokenExpires: prefs.hingeTokenExpires ?? null,
    lastVersionCode: prefs.lastVersionCode ?? null,
    country: prefs.country ?? null,
    authState: prefs.authState ?? null,
    lastSigninMethod: prefs.lastSigninMethod ?? null,
    userState: prefs.userState ?? null,
    isBanned: boolToInt(prefs.isBanned),
    headerAuthorization: prefs.bearerToken ? `Bearer ${prefs.bearerToken}` : null,
    headerXBuildNumber: prefs.lastVersionCode ? String(prefs.lastVersionCode) : null,
    headerXAppVersion: "9.83",
    headerXInstallId: prefs.installId ?? null,
    headerXSessionId: prefs.sessionId ?? null,
    permissionsJson: Array.isArray(prefs.USER_PERMISSIONS) && prefs.USER_PERMISSIONS.length ? JSON.stringify(prefs.USER_PERMISSIONS) : null,
    rawSelectedJson: JSON.stringify(prefs),
  };
}
export async function ParsePreferences(pref_contents: string, phone: string): Promise<AuthSnapshot> {
  const parser = new XMLParser({
    ignoreAttributes: false,
    attributeNamePrefix: "@_",
    textNodeName: "#text",
    allowBooleanAttributes: true,
    parseTagValue: false,
    parseAttributeValue: false,
    trimValues: false,
  });

  const parsed = parser.parse(pref_contents);
  return parseXMLToAuthRow(parsed, phone);
}

/**
 * Print /data/data/co.hinge.app/shared_prefs/default.xml to stdout from the emulator/device,
 * then parse it.
 */
export async function fetchAndParsePrefs(phone: string): Promise<AuthSnapshot> {
  const su = await $`adb shell 'su 0 cat /data/data/co.hinge.app/shared_prefs/default.xml'`;
  const xmlContents = String(su.stdout || "").trim();
  if (!xmlContents || su.exitCode !== 0) {
    throw new Error("could not read default.xml from device/emulator via run-as or su.");
  }
  return await ParsePreferences(xmlContents, phone);
}
