import { parsePhoneNumber, type PhoneNumber } from "libphonenumber-js/min";
import type { ChainablePromiseElement } from "webdriverio";

export async function isOnHomeScreen(driver: WebdriverIO.Browser) {
  const homeHints = [
    "id=co.hinge.app:id/bottom_navigation",
    "id=co.hinge.app:id/navigation_view_root",
    "id=co.hinge.app:id/discover_nexting_layout",
    "id=co.hinge.app:id/profile_title",
  ];
  for (const sel of homeHints) {
    const el = await findAny(driver, sel, 1500);
    if (el) return true;
  }
  return false;
}

export async function findAny(driver: WebdriverIO.Browser, selector: string, timeoutMs = 15000): Promise<ChainablePromiseElement | null> {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    const el = driver.$(selector);
    if (await el.isExisting()) return el;
    await driver.pause(300);
  }
  return null;
}

export async function tapAny(driver: WebdriverIO.Browser, selector: string, timeoutMs = 15000): Promise<ChainablePromiseElement> {
  const el = await findAny(driver, selector, timeoutMs);
  if (!el) throw new Error(`selector ${selector} not found for tap`);
  await el.click();
  return el;
}

export function parseE164(phone: string): PhoneNumber {
  let p = phone.trim().replace(/[\s\-()]/g, "");
  if (!p.startsWith("+")) throw new Error("provide phone in E.164 format like +15551234567");
  return parsePhoneNumber(p, "US");
}
