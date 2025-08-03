import { saveAuthSnapshot } from "../db/db";
import { promptForInput } from "../util";
import { fetchAndParsePrefs } from "../extract-auth-from-prefs";
import { findAny, isOnHomeScreen, parseE164, tapAny } from "./util";
import { StartWDIOSession, StartWDIOSessionOpts } from "./start_session";

const Selectors = {
  signIn: "//android.widget.ScrollView/android.view.View[2]/android.widget.Button",
  signInWithPhone: "//android.widget.ScrollView/android.view.View[1]/android.widget.Button",
  phoneNumberInput: '//android.widget.EditText[@resource-id="co.hinge.app:id/phone_number_input"]',
  phoneNumberNext: '//android.view.View[@resource-id="co.hinge.app:id/next_button"]',
  smsCodeInput: '//android.widget.EditText[@resource-id="co.hinge.app:id/sms_code_input"]',
  countryCodeText: '//android.widget.TextView[@resource-id="co.hinge.app:id/country_code"]',
  countryButton: '//android.view.View[@resource-id="co.hinge.app:id/countryButton"]',
  countryListCodeExact: (code: string) =>
    `//androidx.recyclerview.widget.RecyclerView[@resource-id="co.hinge.app:id/country_list"]//android.widget.TextView[@resource-id="co.hinge.app:id/country_code" and @text="${code}"]`,
} as const;

async function setCountryCodeIfDifferent(driver: WebdriverIO.Browser, desiredDial: string) {
  const ccInline = await findAny(driver, Selectors.countryCodeText!, 5000);
  if (!ccInline) throw new Error("Inline country code TextView not found");

  const current = (await ccInline.getText())?.trim() || "";
  if (current === desiredDial) return;

  await tapAny(driver, Selectors.countryButton!, 8000);

  // use UiScrollable fast path to bring exact dial code into view and click it
  driver.$(
    `android=new UiScrollable(new UiSelector().resourceId("co.hinge.app:id/country_list").scrollable(true))` +
      `.scrollIntoView(new UiSelector().resourceId("co.hinge.app:id/country_code").text("${desiredDial}"))`
  );
  const codeEl = await findAny(driver, Selectors.countryListCodeExact(desiredDial), 4000);
  if (!codeEl) throw new Error("scrolled country dropdown selection but we couldnt find a suitable country code");
  await codeEl.click();

  // verify update
  const after = (await ccInline.getText())?.trim() || "";
  if (after !== desiredDial) {
    await driver.pause(500);
    const ccInline2 = await findAny(driver, Selectors.countryCodeText!, 2000);
    const after2 = (await ccInline2?.getText())?.trim() || "";
    if (after2 !== desiredDial) throw new Error(`country code did not update to ${desiredDial}, still ${after2 || after}`);
  }
}

async function enterSmsAndSubmit(driver: WebdriverIO.Browser, code: string) {
  const field = await findAny(driver, Selectors.smsCodeInput!, 15000);
  if (!field) throw new Error("SMS code field not found");
  await field.click();
  await field.setValue(code.trim());
  await driver.pressKeyCode?.(66); // ENTER
}

export async function authenticate(phone: string, opts: StartWDIOSessionOpts) {
  const driver = await StartWDIOSession(opts);
  try {
    // if already authenticated at home, just fetch/parse/persist
    if (await isOnHomeScreen(driver)) {
      await driver.pause(1500);
      const authRow = await fetchAndParsePrefs(phone);
      await saveAuthSnapshot(authRow);
      return authRow;
    }

    // navigate sign-in with phone
    await tapAny(driver, Selectors.signIn!, 15000);
    await tapAny(driver, Selectors.signInWithPhone!, 15000);

    // handle potential popup (such as update google services) by back once
    const popup = driver.$("//hierarchy/android.widget.FrameLayout");
    if (await popup.isExisting()) {
      await driver.back();
      await driver.pause(500);
    }

    // fill country and phone
    const phoneParsed = parseE164(phone);
    await setCountryCodeIfDifferent(driver, "+" + phoneParsed.countryCallingCode);
    const phoneEl = await findAny(driver, Selectors.phoneNumberInput!, 5000);
    if (!phoneEl) throw new Error("Phone input not found");
    await phoneEl.click();
    try {
      await driver.pressKeyCode(123); // END
      for (let i = 0; i < 20; i++) await driver.pressKeyCode(67); // DEL
    } catch {
      await phoneEl.clearValue();
    }
    await phoneEl.setValue(phoneParsed.nationalNumber);
    await tapAny(driver, Selectors.phoneNumberNext!, 15000);

    const code = await promptForInput("Enter SMS Code:");
    await enterSmsAndSubmit(driver, code);
    // give it some time to login
    // todo: try selecting home page elements until we got hit, better than sleep.
    await driver.pause(1500);
    const authRow = await fetchAndParsePrefs(phone);
    await saveAuthSnapshot(authRow);
    return authRow;
  } finally {
    await driver.deleteSession();
  }
}
