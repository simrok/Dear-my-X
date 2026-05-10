import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';

import { OnboardingScreen } from '@/screens/onboarding/OnboardingScreen';
import { LoginScreen } from '@/screens/auth/LoginScreen';
import { HomeScreen } from '@/screens/home/HomeScreen';
import { CreatePersonaScreen } from '@/screens/persona/CreatePersonaScreen';
import { PersonaDetailScreen } from '@/screens/persona/PersonaDetailScreen';
import { UploadScreen } from '@/screens/upload/UploadScreen';
import { ChatScreen } from '@/screens/chat/ChatScreen';
import { SettingsScreen } from '@/screens/settings/SettingsScreen';
import type { AuthStatus } from '@/stores/useAuthStore';

import type { MainTabParamList, RootStackParamList } from './types';

const RootStack = createNativeStackNavigator<RootStackParamList>();
const MainTab = createBottomTabNavigator<MainTabParamList>();

function MainTabs() {
  return (
    <MainTab.Navigator screenOptions={{ headerShown: false }}>
      <MainTab.Screen name="Home" component={HomeScreen} />
      <MainTab.Screen name="Settings" component={SettingsScreen} />
    </MainTab.Navigator>
  );
}

interface Props {
  status: AuthStatus;
}

export function RootNavigator({ status }: Props) {
  // 인증 여부에 따라 보여주는 스택 자체를 분기 → 화면 전환이 자연스럽게 일어남.
  if (status === 'authenticated') {
    return (
      <RootStack.Navigator>
        <RootStack.Screen
          name="Main"
          component={MainTabs}
          options={{ headerShown: false }}
        />
        <RootStack.Screen
          name="CreatePersona"
          component={CreatePersonaScreen}
          options={{ title: '새 X 만들기' }}
        />
        <RootStack.Screen
          name="PersonaDetail"
          component={PersonaDetailScreen}
          options={{ title: '상세' }}
        />
        <RootStack.Screen
          name="Upload"
          component={UploadScreen}
          options={{ title: '대화 업로드' }}
        />
        <RootStack.Screen
          name="Chat"
          component={ChatScreen}
          options={{ title: '채팅' }}
        />
      </RootStack.Navigator>
    );
  }

  // 비로그인: 온보딩 → 로그인
  return (
    <RootStack.Navigator initialRouteName="Onboarding">
      <RootStack.Screen
        name="Onboarding"
        component={OnboardingScreen}
        options={{ headerShown: false }}
      />
      <RootStack.Screen
        name="Login"
        component={LoginScreen}
        options={{ title: '로그인' }}
      />
    </RootStack.Navigator>
  );
}
