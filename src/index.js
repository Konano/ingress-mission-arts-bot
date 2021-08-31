const TelegramBot = require("node-telegram-bot-api");
const handle = require("./handle");

var config_path = "../config.dev";
if (process.env.NODE_ENV === "production") {
  config_path = "../config";
}
const config = require(config_path);
const token = config.token;

if (!token) {
  console.error("No Token");
  process.exit(1);
}

const bot = new TelegramBot(token, { webHook: config.webhook });

bot.setWebHook(
  `https://${config.webhook.domain}:${config.webhook.port}/bot${token}`,
  { certificate: config.webhook.cert }
);

bot.onText(/\/q (.+)/, (msg, match) => {
  handle({ msg, match, bot, id: msg.chat.id });
});

bot.onText(/\/q@ingress_mission_trello_bot (.+)/, (msg, match) => {
  console.log(match);
  console.log(msg);
  handle({ msg, match, bot, id: msg.chat.id });
  bot.sendMessage(msg.chat.id, "查询任务格式为: /q 任务名");
});

bot.onText(/^\/q$/, (msg, match) => {
  bot.sendMessage(msg.chat.id, "查询任务格式为: /q 任务名");
});

console.log("start");
