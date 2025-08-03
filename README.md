# Squeaky Hinge

> "The squeaky Hinge gets the match"

A well-known issue (to me) with the dating app
[Hinge](https://hinge.co/) is that it sometimes fails to send both
push and email notifications on Android. This applies to both direct
messages as well as new matches. I have already spoken to Hinge's
support team about this and they declined to provide any information
about why this might be, or any assurance that it would be fixed (well
actually, they told me they fixed it and I should just upgrade the
app, but they didn't actually fix it). So, because I got tired of
accidentally ghosting people after not seeing their messages, I took
matters into my own hands and reverse-engineered the mobile API to set
up actual reliable notifications for messages.

**Table of contents**

<!-- toc -->

- [Squeaky Hinge](#squeaky-hinge)
  - [Disclaimer](#disclaimer)
  - [Usage](#usage)
    - [Requirements](#requirements)
    - [Setup](#setup)
    - [Run](#run)

<!-- tocstop -->

## Disclaimer


This project is an UNOFFICIAL library for interacting with Hinge's internal APIs. It is NOT affiliated with, endorsed, or sponsored by Hinge.

USE AT YOUR OWN RISK:

- Account Safety: Using this library may violate Hinge's Terms of Service. This can lead to actions against your account, including but not limited to rate-limiting, suspension, or permanent banning.
- API Instability: Internal APIs are subject to change without notice. This library may break at any time.
- No Warranty: This software is provided "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
- No Liability: IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
-  By using this library, you acknowledge and agree that you understand these risks and take full responsibility for any consequences that may arise from its use.

## Usage

### Requirements
- Android SDK + Emulator (API 22-30,S except 28, with Google Play Services, tested with Pixel 5 API 30)
  - **this process REQUIRES root, hence why API 22-30**. 
- APK of the official app (package: co.hinge.app)
- [Bun](https://bun.com/docs/installation)

### Setup
1) Android emulator
   - Create an AVD (e.g., Pixel 5, Android 11 or higher), best choice is Android Studio Virtual Device Manager
   - Start it from command line or Virtual Device Manager:
     `emulator -avd Pixel_5_API_30`
   - Root the device, [follow these steps](https://github.com/shakalaca/MagiskOnEmulator). It is really easy, but I will gladly help you.
2) Install the app
   - `adb devices`
   - `adb install hinge.apk`
     (If already installed, ensure the package name is co.hinge.app)

3) Appium
   - `bun i -g appium`
   - `bunx appium driver install uiautomator2`
   - `bunx appium`
     (Leave running on default port 4723)

### Run
`bun install && bun migrate`
`bun cli.ts auth +15551234567`
`bun cli.ts rec +90XXXXXXXXXX -g 2 -p 2 --lat 37.416866 --lon -122.0776`

...