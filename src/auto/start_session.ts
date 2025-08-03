import { remote } from "webdriverio";
import { ensureDB } from "../db/db";
type RemoteOptions = Parameters<typeof remote>[0];
const APP_PACKAGE = "co.hinge.app";

export type WebDriverLogTypes = "trace" | "debug" | "info" | "warn" | "error" | "silent";
export class StartWDIOSessionOpts {
  appium_host: string;
  appium_port: number;
  appium_path: string;
  log_level: WebDriverLogTypes;

  constructor(appium_host: string = "127.0.0.1", appium_port = 4723, appium_path = "/", log_level: WebDriverLogTypes = "info") {
    this.appium_host = appium_host;
    this.appium_port = appium_port;
    this.appium_path = appium_path;
    this.log_level = log_level;
  }
}
/**
 * Attaches to existing android emulator and launches Hinge app.
 * @param opts Appium options
 * @returns
 */
export async function StartWDIOSession(opts: StartWDIOSessionOpts) {
  ensureDB();

  const caps: RemoteOptions["capabilities"] = {
    platformName: "Android",
    "appium:automationName": "UiAutomator2",
    "appium:deviceName": "Android Emulator",
    "appium:appPackage": APP_PACKAGE,
    "appium:autoGrantPermissions": true,
    "appium:newCommandTimeout": 300,
    "appium:noReset": true,
  };

  const driver = await remote({
    protocol: "http",
    hostname: opts.appium_host,
    port: opts.appium_port,
    path: opts.appium_path,
    capabilities: caps,
    logLevel: opts.log_level,
  });

  await driver.activateApp(APP_PACKAGE);
  return driver;
}
