module.exports = {
  apps: [
    {
      name: 'IngressMissionArtsBot',
      script: 'src/index.js',
      env: {
        NODE_ENV: 'development',
      },
      env_production: {
        NODE_ENV: 'production',
      },
    },
    {
      name: 'IngressMissionArtsBotSchedule',
      script: 'src/schedule.js',
      env: {
        NODE_ENV: 'development',
      },
      env_production: {
        NODE_ENV: 'production',
      },
    },
  ],
}
