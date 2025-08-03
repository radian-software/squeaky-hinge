import { eq } from "drizzle-orm";
import { ensureDB, getLatestAuthByPhone } from "../db/db";
import { authSnapshots } from "../db/schema";
import { fetch } from "bun";
import { API_URL, COMMON_HEADERS } from ".";
import type { GenderPreference } from "./const";

/**
 *
 * @param phone Phone number
 * @param gender Gender of authenticated user
 * @param genderPreference Preferred gender of recommendations
 * @param lat Latitude of querying user
 * @param lon Longitude of querying user
 */
export async function Recommended(phone: string, gender: GenderPreference, genderPreference: GenderPreference, lat: number, lon: number) {
  const auth = await getLatestAuthByPhone(phone);
  if (!auth) {
    throw new Error("phone number not authenticated");
  }
  if (!auth.bearerToken || !auth.installId) {
    throw new Error("auth information not valid, please logout and authenticate again.");
  }
  const response = await fetch(API_URL + "/rec", {
    method: "POST",
    headers: {
      authorization: "Bearer " + auth.bearerToken.trim(),
      "x-install-id": auth.installId,
      "x-device-id": "64c6d4bea4eaaef6", // todo: also extract this from the authentication information...
      ...COMMON_HEADERS,
    },
    body: JSON.stringify({
      latitude: lat,
      longitude: lon,
      genderId: gender,
      genderPrefId: genderPreference,
      excludedFeedIds: [], // todo: whats this??
    }),
  });
  console.log(response); // do something with the response...
}
