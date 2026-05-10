import { useState } from 'react';
import { ActivityIndicator, Alert, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { AuthApi } from '@/services/api/auth';
import { ApiError } from '@/services/api/client';
import { SupabaseAuth } from '@/services/supabase/auth';
import { useAuthStore } from '@/stores/useAuthStore';
import { colors, radius, spacing, typography } from '@/theme';
import type { User } from '@dear-my-x/shared';

export function SettingsScreen() {
  const userId = useAuthStore((s) => s.userId);
  const email = useAuthStore((s) => s.email);
  const [meBusy, setMeBusy] = useState(false);
  const [me, setMe] = useState<User | null>(null);
  const [meError, setMeError] = useState<string | null>(null);

  const callMe = async () => {
    setMeBusy(true);
    setMeError(null);
    try {
      const data = await AuthApi.me();
      setMe(data);
    } catch (e) {
      if (e instanceof ApiError) {
        setMeError(`${e.status} ${e.code}: ${e.message}`);
      } else {
        setMeError(String(e));
      }
      setMe(null);
    } finally {
      setMeBusy(false);
    }
  };

  const signOut = async () => {
    const { error } = await SupabaseAuth.signOut();
    if (error) Alert.alert('로그아웃 실패', error.message);
    setMe(null);
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>설정</Text>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>현재 세션 (클라이언트)</Text>
        <Text style={styles.kv}>id: {userId ?? '-'}</Text>
        <Text style={styles.kv}>email: {email ?? '-'}</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>서버 /auth/me 테스트</Text>
        <Pressable
          style={[styles.btn, meBusy && styles.disabled]}
          onPress={callMe}
          disabled={meBusy}
        >
          {meBusy ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>호출</Text>}
        </Pressable>
        {me && (
          <View style={styles.result}>
            <Text style={styles.kv}>id: {me.id}</Text>
            <Text style={styles.kv}>email: {me.email}</Text>
            <Text style={styles.kv}>created_at: {me.created_at}</Text>
          </View>
        )}
        {meError && (
          <Text style={[styles.kv, { color: colors.danger }]}>{meError}</Text>
        )}
      </View>

      <Pressable style={styles.dangerBtn} onPress={signOut}>
        <Text style={styles.btnText}>로그아웃</Text>
      </Pressable>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: spacing.xl, gap: spacing.lg, backgroundColor: colors.bg, flexGrow: 1 },
  title: { ...typography.title },
  card: {
    padding: spacing.lg,
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    gap: spacing.sm,
  },
  cardTitle: { fontSize: 14, fontWeight: '600', marginBottom: spacing.sm },
  kv: { fontSize: 13, color: colors.text, fontFamily: 'Courier' },
  btn: {
    backgroundColor: colors.primary,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.lg,
    borderRadius: radius.md,
    alignItems: 'center',
    alignSelf: 'flex-start',
  },
  btnText: { color: '#fff', fontWeight: '600' },
  disabled: { opacity: 0.6 },
  result: { marginTop: spacing.md, gap: spacing.xs },
  dangerBtn: {
    backgroundColor: colors.danger,
    paddingVertical: spacing.md,
    borderRadius: radius.md,
    alignItems: 'center',
    marginTop: spacing.lg,
  },
});
