import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import type { RootStackParamList } from '@/navigation/types';
import { colors, radius, spacing, typography } from '@/theme';

type Nav = NativeStackNavigationProp<RootStackParamList>;

export function OnboardingScreen() {
  const navigation = useNavigation<Nav>();
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Dear my X</Text>
      <Text style={styles.body}>
        실제 인물을 복제하지 않습니다. 업로드한 대화 기록을 기반으로 가상 AI 페르소나를 생성합니다.
        타인의 개인정보가 포함된 자료를 업로드할 경우 필요한 권리를 보유해야 합니다.
      </Text>
      <Pressable style={styles.btn} onPress={() => navigation.navigate('Login')}>
        <Text style={styles.btnText}>시작하기</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: spacing.xl,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.bg,
  },
  title: { ...typography.title, fontSize: 28, marginBottom: spacing.lg },
  body: {
    ...typography.body,
    textAlign: 'center',
    color: colors.textMuted,
    marginBottom: spacing.xl,
  },
  btn: {
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.xxl,
    borderRadius: radius.pill,
  },
  btnText: { color: '#fff', fontWeight: '600', fontSize: 16 },
});
