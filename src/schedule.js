const MongoClient = require("mongodb").MongoClient;
const schedule = require("node-schedule");
const ProgressBar = require("progress");
const fs = require("fs");

var config_path = "../config.dev";
if (process.env.NODE_ENV === "production") {
  config_path = "../config";
}
const config = require(config_path);

const { exec } = require("child_process");
schedule.scheduleJob("45 * * * * *", function () {
  console.log(`ScheduledJob Starts on ${new Date()}`);
  exec("python3 ./src/crawler.py ./data/trello.json", (err, stdout, stderr) => {
    if (err) {
      console.log(err);
      console.log(`ScheduledJob Finished on ${new Date()}`);
      return;
    }
    console.log("import Trello data done!");
    if (stderr) {
      console.log(`crawler.py stderr: ${stderr}`);
    }

    const data = JSON.parse(fs.readFileSync("./data/trello.json", "utf8"));
    MongoClient.connect(
      `mongodb://${config.mongo.user}:${config.mongo.pwd}@localhost:27017/`,
      function (err, dbo) {
        if (err) throw err;
        const db = dbo.db("ingress");
        db.createCollection("trello");
        db.dropCollection("trello", function (err, res) {
          if (err) throw err;
          console.log("drop collection done!");
          db.createCollection("trello", function (err, res) {
            if (err) throw err;
            console.log("create collection done!");

            var num = 0;
            for (let i = 0; i < data.length; ++i) num += data[i].length;

            if (process.env.NODE_PROGRESSBAR !== "off") {
              const bar = new ProgressBar(
                "inserting [:bar] :current/total :percent :etas",
                {
                  complete: "=",
                  incomplete: " ",
                  total: num,
                }
              );
            }

            for (let i = 0; i < data.length; ++i) {
              for (let j = 0; j < data[i].length; ++j) {
                db.collection("trello").insertOne(
                  data[i][j],
                  function (err, res) {
                    if (err) throw err;
                    if (process.env.NODE_PROGRESSBAR !== "off") {
                      bar.tick();
                      if (bar.complete) {
                        console.log(`ScheduledJob Finished on ${new Date()}`);
                      }
                    } else {
                      if (--num == 0) {
                        console.log(`ScheduledJob Finished on ${new Date()}`);
                      }
                    }
                  }
                );
              }
            }
            db.close();
          });
        });
      }
    );
  });
});

module.exports = {};
