import { StatusBar } from 'expo-status-bar';
import { ActivityIndicator, StyleSheet, View } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { NavigationContainer } from '@react-navigation/native';

import { useAuthSession } from '@/features/auth/useAuthSession';
import { RootNavigator } from '@/navigation/RootNavigator';
import { useAuthStore } from '@/stores/useAuthStore';
import { colors } from '@/theme';

function Bootstrap() {
  // Supabase 세션을 zustand 스토어와 동기화
  useAuthSession();
  const status = useAuthStore((s) => s.status);

  if (status === 'unknown') {
    return (
      <View style={styles.loading}>
        <ActivityIndicator />
      </View>
    );
  }
  return <RootNavigator status={status} />;
}

export default function App() {
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <Bootstrap />
        <StatusBar style="auto" />
      </NavigationContainer>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  loading: { flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.bg },
});
