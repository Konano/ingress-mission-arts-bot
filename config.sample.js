var config = {
  token: "000000000:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  mongo: {
    user: "root",
    pwd: "password",
  },
  webhook: {
    port: 8443,
    key: "./secret/private.key",
    cert: "./secret/cert.pem",
    domain: "",
    token: "",
  },
};

module.exports = config;
