import { useCallback } from 'react';
import {
  ActivityIndicator,
  FlatList,
  Pressable,
  RefreshControl,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { useFocusEffect, useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';

import { PersonaCard } from '@/components/common/PersonaCard';
import { usePersonas } from '@/features/persona/usePersonas';
import type { RootStackParamList } from '@/navigation/types';
import { colors, radius, spacing, typography } from '@/theme';

type Nav = NativeStackNavigationProp<RootStackParamList>;

export function HomeScreen() {
  const navigation = useNavigation<Nav>();
  const { data, isLoading, error, refresh } = usePersonas();

  // 화면 포커스 시 자동 새로고침 (Create / Detail 에서 변경 후 돌아왔을 때 반영)
  useFocusEffect(
    useCallback(() => {
      void refresh();
    }, [refresh]),
  );

  const empty = !isLoading && data.length === 0;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Dear my X</Text>
      </View>

      {error && (
        <View style={styles.errorBox}>
          <Text style={styles.errorText}>{error}</Text>
          <Pressable onPress={refresh} hitSlop={8}>
            <Text style={styles.retryText}>다시 시도</Text>
          </Pressable>
        </View>
      )}

      {isLoading && data.length === 0 ? (
        <View style={styles.center}>
          <ActivityIndicator />
        </View>
      ) : empty ? (
        <View style={styles.center}>
          <Text style={styles.emptyTitle}>아직 만든 페르소나가 없어요</Text>
          <Text style={styles.emptyBody}>
            아래 + 버튼으로 첫 번째 가상 X 를 만들어보세요.
          </Text>
        </View>
      ) : (
        <FlatList
          data={data}
          keyExtractor={(p) => p.id}
          contentContainerStyle={styles.listContent}
          ItemSeparatorComponent={() => <View style={{ height: spacing.md }} />}
          refreshControl={<RefreshControl refreshing={isLoading} onRefresh={refresh} />}
          renderItem={({ item }) => (
            <PersonaCard
              persona={item}
              onPress={() => navigation.navigate('PersonaDetail', { personaId: item.id })}
            />
          )}
        />
      )}

      <Pressable
        style={styles.fab}
        onPress={() => navigation.navigate('CreatePersona')}
        accessibilityLabel="새 X 만들기"
      >
        <Text style={styles.fabIcon}>+</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  header: {
    paddingTop: spacing.xxl,
    paddingHorizontal: spacing.xl,
    paddingBottom: spacing.md,
  },
  title: { ...typography.title, fontSize: 22 },
  listContent: { paddingHorizontal: spacing.xl, paddingBottom: 96 },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: spacing.xl },
  emptyTitle: { ...typography.body, fontSize: 16, fontWeight: '600', marginBottom: spacing.sm },
  emptyBody: { ...typography.caption, textAlign: 'center' },
  errorBox: {
    marginHorizontal: spacing.xl,
    marginBottom: spacing.md,
    padding: spacing.md,
    backgroundColor: '#FFE5E5',
    borderRadius: radius.md,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  errorText: { color: colors.danger, flex: 1, marginRight: spacing.md, fontSize: 12 },
  retryText: { color: colors.danger, fontWeight: '600' },
  fab: {
    position: 'absolute',
    right: spacing.xl,
    bottom: spacing.xl,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 4,
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowRadius: 6,
    shadowOffset: { width: 0, height: 2 },
  },
  fabIcon: { color: '#fff', fontSize: 28, lineHeight: 30, fontWeight: '300' },
});
