// 홈 화면의 페르소나 카드.
import { Image, Pressable, StyleSheet, Text, View } from 'react-native';

import { colors, radius, spacing, typography } from '@/theme';
import { RELATION_LABELS, type Persona, type RelationType } from '@dear-my-x/shared';

interface Props {
  persona: Persona;
  onPress?: () => void;
}

function relationLabel(type: string): string {
  return RELATION_LABELS[type as RelationType] ?? type;
}

function formatDate(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '';
  const now = Date.now();
  const diff = now - d.getTime();
  const day = 86_400_000;
  if (diff < day) return '오늘';
  if (diff < 2 * day) return '어제';
  if (diff < 7 * day) return `${Math.floor(diff / day)}일 전`;
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(
    d.getDate(),
  ).padStart(2, '0')}`;
}

export function PersonaCard({ persona, onPress }: Props) {
  return (
    <Pressable style={({ pressed }) => [styles.card, pressed && styles.pressed]} onPress={onPress}>
      <View style={styles.avatarBox}>
        {persona.profile_image_url ? (
          <Image source={{ uri: persona.profile_image_url }} style={styles.avatar} />
        ) : (
          <View style={[styles.avatar, styles.avatarFallback]}>
            <Text style={styles.avatarInitial}>{persona.name.slice(0, 1)}</Text>
          </View>
        )}
      </View>

      <View style={styles.body}>
        <Text style={styles.name} numberOfLines={1}>
          {persona.name}
        </Text>
        <Text style={styles.meta} numberOfLines={1}>
          {relationLabel(persona.relation_type)} · {formatDate(persona.updated_at)}
        </Text>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.md,
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    gap: spacing.md,
  },
  pressed: { opacity: 0.7 },
  avatarBox: { width: 56, height: 56 },
  avatar: { width: 56, height: 56, borderRadius: 28 },
  avatarFallback: {
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarInitial: { color: '#fff', fontSize: 24, fontWeight: '700' },
  body: { flex: 1, gap: 4 },
  name: { ...typography.body, fontWeight: '600', color: colors.text, fontSize: 16 },
  meta: { ...typography.caption },
});
