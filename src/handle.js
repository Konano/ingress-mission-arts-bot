const MongoClient = require("mongodb").MongoClient;
const escapeStringRegexp = require("escape-string-regexp");

var config_path = "../config.dev";
if (process.env.NODE_ENV === "production") {
  config_path = "../config";
}
const config = require(config_path);

class Handler {
  constructor({ bot, id }) {
    this.bot = bot;
    this.id = id;
    this.reg = /^\[.*\]\s?/;
  }

  sendText(msg, options = {}) {
    const setttins = Object.assign(
      {},
      {
        parse_mode: undefined,
        disable_web_page_preview: "true",
      },
      options
    );

    return this.bot.sendMessage(this.id, msg, setttins);
  }

  sendPhoto(msg) {
    return this.bot.sendPhoto(this.id, msg, { disable_notification: "false" });
  }

  async filterMissions(title) {
    const mongodbUrl = `mongodb://${config.mongo.user}:${config.mongo.pwd}@localhost:27017/`;
    const dbo = await MongoClient.connect(mongodbUrl);
    const db = dbo.db("ingress");
    const collection = db.collection("trello");
    const fixed = escapeStringRegexp(title);
    const pattern = new RegExp(fixed, "i");
    const result = await collection.find({ name: pattern }).toArray();
    db.close();
    return result.filter((v, i, self) => {
      const index = self.findIndex((s) => {
        const vname = v.name.replace(this.reg, "");
        const sname = s.name.replace(this.reg, "");
        return vname === sname;
      });
      return index === i;
    });
  }

  async handleMulti(missions, title) {
    const result = [];
    const len = missions.length;
    let fi = missions.filter((x) => {
      result.push(`/q ${x.name}`);
      return x.name === title;
    });
    if (fi.length == 0 || fi.length > 1) {
      result.push("任务已找到，一共有这么多任务，你要看哪一个呢：");
      await this.sendText(result.join("\n"), { parse_mode: null });
    } else {
      await this.handleSingle(fi, title);
    }
  }
  async sendCoverPhoto(m) {
    if (m.idAttachmentCover) {
      let image;

      const attachment = m.attachments.find((attachment) => {
        return attachment.id === m.idAttachmentCover;
      });

      if (attachment.previews[4]) {
        image = attachment.previews[4].url;
      } else {
        image = attachment.url;
      }

      await this.sendPhoto(image);
    }
  }

  handleLinks(name, shortUrl) {
    const links = [];
    const bgUrl = encodeURI(`https://bannergress.com/search/${name}`)
    links.push(`[Trello](${shortUrl})`);
    links.push(`[bannergress](${bgUrl})`);
    return links.join(" | ");
  }

  async handleSingle(missions, title) {
    if (missions != undefined) {
      const result = [];
      const m = missions[0];
      const name = m.name.replace(this.reg, "");
      const links = this.handleLinks(title, m.shortUrl);

      await this.sendText(`任务已找到 ${links}`, { parse_mode: "Markdown" });
      await this.sendCoverPhoto(m);

      const labels = [];

      if (m.labels) {
        m.labels.forEach((label) => {
          if (label.color === "red" || label.color === "black") {
            labels.push(label.name);
          }
        });
      }

      if (labels.length) {
        result.push(`‼️ ${labels.join(" | ")}\n`);
      }

      result.push(`${m.name}`);
      result.push(`${m.desc}`);

      await this.sendText(result.join("\n"));
    }
  }

  async handleNull() {
    await this.sendText("很抱歉没有查到你想找的任务信息，要不要换个姿势呢？");
  }

  async handle({ msg, match }) {
    if (msg.date < new Date().getTime() / 1000 - 120) {
      return;
    }

    const title = match[1];
    const missions = await this.filterMissions(title);

    let result = [];

    if (missions.length > 1) {
      await this.handleMulti(missions, title);
    } else if (missions.length === 1) {
      await this.handleSingle(missions, title);
    } else {
      await this.handleNull();
    }

    return result.join("\n");
  }
}

module.exports = async function handle({ msg, match, bot, id }) {
  const handler = new Handler({ bot, id });
  try {
    await handler.handle({ msg, match });
    console.error(match);
    if (match[1].includes("广州"))
      await handler.sendText("广州任务 Channel：@IngressMissionCanton");
    if (match[1].includes("大连"))
      await handler.sendText("大连任务 Channel: @DalianSpecopsChannel");
  } catch (error) {
    await handler.sendText(
      `哇哦出错了，快召唤 @NanoApe，错误快照：\n\n\`\`\`\n${error}\n\`\`\``
    );
    console.error(error);
  }
};
