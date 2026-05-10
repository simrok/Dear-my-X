import { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { useNavigation, useRoute, type RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';

import { Pill } from '@/components/common/Pill';
import { usePersona } from '@/features/persona/usePersonas';
import type { RootStackParamList } from '@/navigation/types';
import { ApiError } from '@/services/api/client';
import { PersonasApi, type PersonaUpdateInput } from '@/services/api/personas';
import { colors, radius, spacing, typography } from '@/theme';
import { RELATION_LABELS, RELATION_OPTIONS, type RelationType } from '@dear-my-x/shared';

type Nav = NativeStackNavigationProp<RootStackParamList, 'PersonaDetail'>;
type R = RouteProp<RootStackParamList, 'PersonaDetail'>;

function emptyToNull(s: string): string | null {
  const t = s.trim();
  return t.length === 0 ? null : t;
}

export function PersonaDetailScreen() {
  const route = useRoute<R>();
  const navigation = useNavigation<Nav>();
  const { personaId } = route.params;
  const { data, isLoading, error, refresh } = usePersona(personaId);

  const [editing, setEditing] = useState(false);
  const [savingBusy, setSavingBusy] = useState(false);
  const [deletingBusy, setDeletingBusy] = useState(false);

  // 편집 폼 로컬 상태 (data 로 초기화)
  const [name, setName] = useState('');
  const [relation, setRelation] = useState<RelationType>('friend');
  const [personality, setPersonality] = useState('');
  const [speaking, setSpeaking] = useState('');
  const [safety, setSafety] = useState('');
  const [imageUrl, setImageUrl] = useState('');

  useEffect(() => {
    if (data && !editing) {
      setName(data.name);
      setRelation((data.relation_type as RelationType) ?? 'friend');
      setPersonality(data.personality ?? '');
      setSpeaking(data.speaking_style ?? '');
      setSafety(data.safety_notes ?? '');
      setImageUrl(data.profile_image_url ?? '');
    }
  }, [data, editing]);

  const handleSave = async () => {
    if (!data) return;
    if (!name.trim()) {
      Alert.alert('이름이 필요해요');
      return;
    }
    const body: PersonaUpdateInput = {
      name: name.trim(),
      relation_type: relation,
      personality: emptyToNull(personality),
      speaking_style: emptyToNull(speaking),
      safety_notes: emptyToNull(safety),
      profile_image_url: emptyToNull(imageUrl),
    };
    setSavingBusy(true);
    try {
      await PersonasApi.update(data.id, body);
      await refresh();
      setEditing(false);
    } catch (e) {
      const msg = e instanceof ApiError ? `${e.code}: ${e.message}` : String(e);
      Alert.alert('저장 실패', msg);
    } finally {
      setSavingBusy(false);
    }
  };

  const handleDelete = () => {
    if (!data) return;
    Alert.alert('삭제 확인', `"${data.name}" 을 삭제할까요? 이 작업은 되돌릴 수 없어요.`, [
      { text: '취소', style: 'cancel' },
      {
        text: '삭제',
        style: 'destructive',
        onPress: async () => {
          setDeletingBusy(true);
          try {
            await PersonasApi.delete(data.id);
            navigation.goBack();
          } catch (e) {
            const msg = e instanceof ApiError ? `${e.code}: ${e.message}` : String(e);
            Alert.alert('삭제 실패', msg);
          } finally {
            setDeletingBusy(false);
          }
        },
      },
    ]);
  };

  if (isLoading && !data) {
    return (
      <View style={styles.center}>
        <ActivityIndicator />
      </View>
    );
  }

  if (error || !data) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>{error ?? '페르소나를 찾을 수 없어요.'}</Text>
        <Pressable onPress={refresh} style={styles.retryBtn}>
          <Text style={styles.retryText}>다시 시도</Text>
        </Pressable>
      </View>
    );
  }

  // ---------------- READ MODE ----------------
  if (!editing) {
    return (
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.header}>
          <Text style={styles.name}>{data.name}</Text>
          <Text style={styles.relation}>
            {RELATION_LABELS[data.relation_type as RelationType] ?? data.relation_type}
          </Text>
        </View>

        <ReadField label="성격" value={data.personality} />
        <ReadField label="말투" value={data.speaking_style} />
        <ReadField label="주의 주제" value={data.safety_notes} />
        <ReadField label="프로필 이미지" value={data.profile_image_url} mono />
        <ReadField label="생성일" value={data.created_at} mono />

        <View style={styles.row}>
          <Pressable
            style={[styles.secondaryBtn, deletingBusy && styles.disabled]}
            onPress={() => setEditing(true)}
            disabled={deletingBusy}
          >
            <Text style={styles.secondaryBtnText}>수정</Text>
          </Pressable>

          <Pressable
            style={[styles.dangerBtn, deletingBusy && styles.disabled]}
            onPress={handleDelete}
            disabled={deletingBusy}
          >
            {deletingBusy ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.dangerBtnText}>삭제</Text>
            )}
          </Pressable>
        </View>

        <Pressable
          style={styles.secondaryBtn}
          onPress={() => navigation.navigate('Upload', { personaId: data.id })}
        >
          <Text style={styles.secondaryBtnText}>대화 업로드</Text>
        </Pressable>

        {/* TODO: 채팅 단계 구현되면 여기서 ChatRoom 생성 → Chat 화면으로 이동 */}
        <Pressable style={[styles.primaryBtn, styles.disabled]} disabled>
          <Text style={styles.primaryBtnText}>채팅 시작 (구현 예정)</Text>
        </Pressable>
      </ScrollView>
    );
  }

  // ---------------- EDIT MODE ----------------
  return (
    <KeyboardAvoidingView
      style={{ flex: 1, backgroundColor: colors.bg }}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
        <EditField label="이름">
          <TextInput
            style={styles.input}
            value={name}
            onChangeText={setName}
            editable={!savingBusy}
            maxLength={80}
          />
        </EditField>

        <EditField label="관계 유형">
          <View style={styles.pillRow}>
            {RELATION_OPTIONS.map((opt) => (
              <Pill
                key={opt.value}
                label={opt.label}
                selected={relation === opt.value}
                onPress={() => setRelation(opt.value)}
                disabled={savingBusy}
              />
            ))}
          </View>
        </EditField>

        <EditField label="성격">
          <TextInput
            style={[styles.input, styles.multiline]}
            value={personality}
            onChangeText={setPersonality}
            editable={!savingBusy}
            multiline
          />
        </EditField>

        <EditField label="말투">
          <TextInput
            style={[styles.input, styles.multiline]}
            value={speaking}
            onChangeText={setSpeaking}
            editable={!savingBusy}
            multiline
          />
        </EditField>

        <EditField label="주의 주제">
          <TextInput
            style={[styles.input, styles.multiline]}
            value={safety}
            onChangeText={setSafety}
            editable={!savingBusy}
            multiline
          />
        </EditField>

        <EditField label="프로필 이미지 URL">
          <TextInput
            style={styles.input}
            value={imageUrl}
            onChangeText={setImageUrl}
            editable={!savingBusy}
            autoCapitalize="none"
            keyboardType="url"
          />
        </EditField>

        <View style={styles.row}>
          <Pressable
            style={[styles.secondaryBtn, savingBusy && styles.disabled]}
            onPress={() => setEditing(false)}
            disabled={savingBusy}
          >
            <Text style={styles.secondaryBtnText}>취소</Text>
          </Pressable>
          <Pressable
            style={[styles.primaryBtn, savingBusy && styles.disabled]}
            onPress={handleSave}
            disabled={savingBusy}
          >
            {savingBusy ? <ActivityIndicator color="#fff" /> : <Text style={styles.primaryBtnText}>저장</Text>}
          </Pressable>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

function ReadField({ label, value, mono }: { label: string; value: string | null; mono?: boolean }) {
  return (
    <View style={styles.readField}>
      <Text style={styles.readLabel}>{label}</Text>
      <Text style={[styles.readValue, mono && styles.mono]}>{value ?? '—'}</Text>
    </View>
  );
}

function EditField({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <View style={styles.field}>
      <Text style={styles.label}>{label}</Text>
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { padding: spacing.xl, gap: spacing.lg, paddingBottom: spacing.xxl + 24 },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: spacing.xl, backgroundColor: colors.bg, gap: spacing.md },
  header: { marginBottom: spacing.md, gap: spacing.xs },
  name: { ...typography.title, fontSize: 26 },
  relation: { ...typography.caption, fontSize: 13 },
  readField: { gap: 4 },
  readLabel: { fontSize: 12, color: colors.textMuted, fontWeight: '600' },
  readValue: { ...typography.body, color: colors.text },
  mono: { fontFamily: 'Courier', fontSize: 12 },
  field: { gap: spacing.sm },
  label: { fontSize: 13, color: colors.textMuted, fontWeight: '600' },
  input: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    padding: spacing.md,
    fontSize: 15,
    backgroundColor: colors.surface,
    color: colors.text,
  },
  multiline: { minHeight: 64, textAlignVertical: 'top' },
  pillRow: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm },
  row: { flexDirection: 'row', gap: spacing.md, marginTop: spacing.lg },
  primaryBtn: {
    flex: 1,
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    borderRadius: radius.md,
    alignItems: 'center',
  },
  primaryBtnText: { color: '#fff', fontWeight: '700', fontSize: 16 },
  secondaryBtn: {
    flex: 1,
    paddingVertical: spacing.md,
    borderRadius: radius.md,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.border,
  },
  secondaryBtnText: { color: colors.text, fontWeight: '600' },
  dangerBtn: {
    flex: 1,
    backgroundColor: colors.danger,
    paddingVertical: spacing.md,
    borderRadius: radius.md,
    alignItems: 'center',
  },
  dangerBtnText: { color: '#fff', fontWeight: '700' },
  disabled: { opacity: 0.6 },
  errorText: { color: colors.danger, textAlign: 'center' },
  retryBtn: { paddingVertical: spacing.sm, paddingHorizontal: spacing.lg },
  retryText: { color: colors.primary, fontWeight: '600' },
});
