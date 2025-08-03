import { Command } from "commander";
import { authenticate, Recommended } from "./src";
import { StartWDIOSessionOpts } from "./src/auto/start_session";

const program = new Command();

program.name("squeaky-hinge").description("CLI for Hinge Unofficial API");

program
  .command("auth")
  .description("authenticate with hinge")
  .argument("<phone>", "phone number for authentication")
  .action(async (phone: string) => {
    await authenticate(phone, new StartWDIOSessionOpts());
  });

program
  .command("rec")
  .description("get recommendation feed")
  .argument("<phone>", "phone number")
  .option("-g, --gender <gender>", "gender of authenticated user")
  .option("-p, --gender-preference <preference>", "preferred gender of recommendations")
  .option("--lat <latitude>", "latitude of querying user")
  .option("--lon <longitude>", "longitude of querying user")
  .action(async (phone: string, options: any) => {
    await Recommended(phone, options.gender, options.genderPreference, parseFloat(options.lat), parseFloat(options.lon));
  });

program.parse();
