// 안내 카드 (제목 + 본문 + optional 이모지/번호 리스트).
import { StyleSheet, Text, View } from 'react-native';

import { colors, radius, spacing, typography } from '@/theme';

interface Props {
  title: string;
  steps?: string[];
  body?: string;
  variant?: 'info' | 'warning';
}

export function InfoCard({ title, steps, body, variant = 'info' }: Props) {
  return (
    <View style={[styles.card, variant === 'warning' && styles.warning]}>
      <Text style={styles.title}>{title}</Text>
      {body && <Text style={styles.body}>{body}</Text>}
      {steps && steps.length > 0 && (
        <View style={styles.steps}>
          {steps.map((s, i) => (
            <View key={i} style={styles.stepRow}>
              <Text style={styles.stepNum}>{i + 1}.</Text>
              <Text style={styles.stepText}>{s}</Text>
            </View>
          ))}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    padding: spacing.lg,
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    gap: spacing.sm,
  },
  warning: { backgroundColor: '#FFF8E1', borderColor: '#FFE082' },
  title: { ...typography.body, fontWeight: '700', fontSize: 15 },
  body: { ...typography.body, fontSize: 13, color: colors.textMuted, lineHeight: 20 },
  steps: { gap: spacing.xs, marginTop: spacing.xs },
  stepRow: { flexDirection: 'row', gap: spacing.sm },
  stepNum: { ...typography.body, fontSize: 13, color: colors.primary, fontWeight: '700', width: 22 },
  stepText: { ...typography.body, fontSize: 13, flex: 1, lineHeight: 20 },
});
