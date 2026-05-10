// Expo 앱 진입점.
// `package.json` 의 "main": "App.tsx" 를 직접 가리키므로
// registerRootComponent 를 명시적으로 호출해 RN/Web 양쪽에서 안정 동작하게 한다.
import 'react-native-gesture-handler';
import 'react-native-url-polyfill/auto';
import { registerRootComponent } from 'expo';

import App from './src/app/App';

registerRootComponent(App);

export default App;
