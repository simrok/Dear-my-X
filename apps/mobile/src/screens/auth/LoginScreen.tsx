import { useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { SupabaseAuth } from '@/services/supabase/auth';
import { colors, radius, spacing, typography } from '@/theme';

type Mode = 'signIn' | 'signUp';

export function LoginScreen() {
  const [mode, setMode] = useState<Mode>('signIn');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    if (!email || !password) {
      Alert.alert('입력 필요', '이메일과 비밀번호를 입력해 주세요.');
      return;
    }
    setBusy(true);
    try {
      const { error } =
        mode === 'signIn'
          ? await SupabaseAuth.signInWithEmail(email.trim(), password)
          : await SupabaseAuth.signUpWithEmail(email.trim(), password);

      if (error) {
        Alert.alert('실패', error.message);
        return;
      }
      if (mode === 'signUp') {
        Alert.alert(
          '확인',
          '가입 메일을 확인해 주세요. (Supabase 프로젝트 설정에 따라 이메일 인증이 필요할 수 있습니다)',
        );
      }
      // 성공 시: onAuthStateChange 가 스토어를 업데이트 → Navigator 가 Main 으로 자동 전환.
    } finally {
      setBusy(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <Text style={styles.title}>{mode === 'signIn' ? '로그인' : '회원가입'}</Text>

      <TextInput
        style={styles.input}
        placeholder="이메일"
        autoCapitalize="none"
        autoComplete="email"
        keyboardType="email-address"
        value={email}
        onChangeText={setEmail}
        editable={!busy}
      />
      <TextInput
        style={styles.input}
        placeholder="비밀번호"
        secureTextEntry
        autoComplete={mode === 'signIn' ? 'password' : 'new-password'}
        value={password}
        onChangeText={setPassword}
        editable={!busy}
      />

      <Pressable
        style={[styles.primaryBtn, busy && styles.disabled]}
        onPress={submit}
        disabled={busy}
      >
        {busy ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.primaryBtnText}>{mode === 'signIn' ? '로그인' : '가입하기'}</Text>
        )}
      </Pressable>

      <Pressable
        onPress={() => setMode((m) => (m === 'signIn' ? 'signUp' : 'signIn'))}
        disabled={busy}
        hitSlop={8}
      >
        <Text style={styles.toggle}>
          {mode === 'signIn' ? '계정이 없나요? 회원가입' : '이미 계정이 있나요? 로그인'}
        </Text>
      </Pressable>

      <View style={styles.notice}>
        <Text style={styles.noticeText}>
          Dear my X 는 실제 인물을 복제하지 않습니다. 가상 AI 페르소나 앱입니다.
        </Text>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bg,
    padding: spacing.xl,
    justifyContent: 'center',
  },
  title: { ...typography.title, marginBottom: spacing.xl, textAlign: 'center' },
  input: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    padding: spacing.md,
    marginBottom: spacing.md,
    fontSize: 16,
    backgroundColor: colors.surface,
  },
  primaryBtn: {
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    borderRadius: radius.md,
    alignItems: 'center',
    marginTop: spacing.sm,
  },
  primaryBtnText: { color: '#fff', fontSize: 16, fontWeight: '600' },
  disabled: { opacity: 0.6 },
  toggle: {
    marginTop: spacing.lg,
    textAlign: 'center',
    color: colors.primary,
  },
  notice: {
    marginTop: spacing.xxl,
    padding: spacing.md,
    backgroundColor: colors.surface,
    borderRadius: radius.md,
  },
  noticeText: { ...typography.caption, textAlign: 'center' },
});
