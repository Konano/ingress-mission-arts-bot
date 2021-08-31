module.exports = {
  apps: [
    {
      name: 'IngressMissionArtsBot',
      script: 'src/index.js',
      env: {
        NODE_ENV: 'development',
        NODE_PROGRESSBAR: 'off',
      },
      env_production: {
        NODE_ENV: 'production',
        NODE_PROGRESSBAR: 'off',
      },
      watch: ['src'],
    },
    {
      name: 'IngressMissionArtsBotSchedule',
      script: 'src/schedule.js',
      env: {
        NODE_ENV: 'development',
        NODE_PROGRESSBAR: 'off',
      },
      env_production: {
        NODE_ENV: 'production',
        NODE_PROGRESSBAR: 'off',
      },
      watch: ['src'],
    },
  ],
}
