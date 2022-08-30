module.exports = {
  transpileDependencies: [
    'vuetify'
  ],
  publicPath: process.env.NODE_ENV === 'production' ? '/' : '/',
  chainWebpack: config => {
    config.module.rules.delete('eslint');
    config
      .plugin('html')
      .tap(args => {
        args[0].title = 'FAO';
        args[0].favicon = "./public/favicon-33x32.png";
        return args
      })
  },
  pwa: {
    manifestOptions: {
      name: 'Food and Agriculture Organization',
      short_name: 'FAO',
      description: 'Recolección de eventos por sistemas',
      theme_color: '#004884',
      background_color: '#004884',
      appleMobileWebAppCapable: 'yes',
      start_url: '.',
      display: 'standalone',
      orientation: 'portrait',
      iconPaths: {
        favicon32: './img/icons/favicon-33x32.png',
        favicon16: './img/icons/favicon-33x32.png',
        appleTouchIcon: './img/icons/favicon-33x32.png',
        maskIcon: './img/icons/favicon-33x32.png',
        msTileImage: './img/icons/favicon-33x32.png',
      },
      icons: [
        {
          src: './img/icons/favicon-33x32.png',
          sizes: '33x32',
          type: 'image/png',
        }, {
          src: './img/icons/favicon.ico',
          sizes: '33x32',
        }
      ]
    }
  }
}
