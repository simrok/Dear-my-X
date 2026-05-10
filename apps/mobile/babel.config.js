module.exports = function (api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      [
        'module-resolver',
        {
          root: ['./'],
          extensions: ['.ios.js', '.android.js', '.js', '.ts', '.tsx', '.json'],
          alias: {
            '@': './src',
            '@dear-my-x/shared': '../../packages/shared/src',
          },
        },
      ],
      // reanimated 는 항상 마지막
      'react-native-reanimated/plugin',
    ],
  };
};
