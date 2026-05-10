import { useState } from 'react';
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
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';

import { Pill } from '@/components/common/Pill';
import { ApiError } from '@/services/api/client';
import { PersonasApi } from '@/services/api/personas';
import { colors, radius, spacing, typography } from '@/theme';
import {
  RELATION_OPTIONS,
  type PersonaCreateInput,
  type RelationType,
} from '@dear-my-x/shared';

import type { RootStackParamList } from '@/navigation/types';

type Nav = NativeStackNavigationProp<RootStackParamList, 'CreatePersona'>;

function emptyToNull(s: string): string | null {
  const t = s.trim();
  return t.length === 0 ? null : t;
}

export function CreatePersonaScreen() {
  const navigation = useNavigation<Nav>();

  const [name, setName] = useState('');
  const [relation, setRelation] = useState<RelationType>('friend');
  const [personality, setPersonality] = useState('');
  const [speaking, setSpeaking] = useState('');
  const [safety, setSafety] = useState('');
  const [imageUrl, setImageUrl] = useState('');
  const [consentVirtual, setConsentVirtual] = useState(false);
  const [consentRights, setConsentRights] = useState(false);
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    if (!name.trim()) {
      Alert.alert('이름이 필요해요', '페르소나 이름을 입력해 주세요.');
      return;
    }
    if (!consentVirtual || !consentRights) {
      Alert.alert('동의 필요', '두 가지 동의 항목을 모두 체크해 주세요.');
      return;
    }

    const body: PersonaCreateInput = {
      name: name.trim(),
      relation_type: relation,
      personality: emptyToNull(personality),
      speaking_style: emptyToNull(speaking),
      safety_notes: emptyToNull(safety),
      profile_image_url: emptyToNull(imageUrl),
      consent_virtual_persona: consentVirtual,
      consent_data_rights: consentRights,
    };

    setBusy(true);
    try {
      await PersonasApi.create(body);
      // 홈으로 돌아가면 useFocusEffect 가 목록을 새로고침한다.
      navigation.goBack();
    } catch (e) {
      const msg = e instanceof ApiError ? `${e.code}: ${e.message}` : String(e);
      Alert.alert('생성 실패', msg);
    } finally {
      setBusy(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={{ flex: 1, backgroundColor: colors.bg }}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
        <Field label="이름 *">
          <TextInput
            style={styles.input}
            placeholder="예: 민수"
            value={name}
            onChangeText={setName}
            editable={!busy}
            maxLength={80}
          />
        </Field>

        <Field label="관계 유형 *">
          <View style={styles.pillRow}>
            {RELATION_OPTIONS.map((opt) => (
              <Pill
                key={opt.value}
                label={opt.label}
                selected={relation === opt.value}
                onPress={() => setRelation(opt.value)}
                disabled={busy}
              />
            ))}
          </View>
        </Field>

        <Field label="성격 키워드">
          <TextInput
            style={[styles.input, styles.multiline]}
            placeholder="예: 다정함, 약간 시니컬함, 잘 챙김"
            value={personality}
            onChangeText={setPersonality}
            editable={!busy}
            multiline
          />
        </Field>

        <Field label="말투 스타일">
          <TextInput
            style={[styles.input, styles.multiline]}
            placeholder='예: 짧게 답함. "ㅇㅇ" 자주 사용. 반말.'
            value={speaking}
            onChangeText={setSpeaking}
            editable={!busy}
            multiline
          />
        </Field>

        <Field label="주의할 주제">
          <TextInput
            style={[styles.input, styles.multiline]}
            placeholder="예: 건강 얘기는 가볍게 받지 않음"
            value={safety}
            onChangeText={setSafety}
            editable={!busy}
            multiline
          />
        </Field>

        <Field label="프로필 이미지 URL (선택)">
          <TextInput
            style={styles.input}
            placeholder="https://..."
            value={imageUrl}
            onChangeText={setImageUrl}
            editable={!busy}
            autoCapitalize="none"
            keyboardType="url"
          />
        </Field>

        <View style={styles.consentBox}>
          <Checkbox
            checked={consentVirtual}
            onPress={() => setConsentVirtual((v) => !v)}
            disabled={busy}
            label="이 AI 는 실제 인물이 아니라 가상 페르소나임을 이해했습니다."
          />
          <Checkbox
            checked={consentRights}
            onPress={() => setConsentRights((v) => !v)}
            disabled={busy}
            label="업로드하는 대화 기록에 대한 사용 권한이 있음을 확인합니다."
          />
        </View>

        <Pressable
          style={[styles.primaryBtn, busy && styles.disabled]}
          onPress={submit}
          disabled={busy}
        >
          {busy ? <ActivityIndicator color="#fff" /> : <Text style={styles.primaryBtnText}>만들기</Text>}
        </Pressable>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <View style={styles.field}>
      <Text style={styles.label}>{label}</Text>
      {children}
    </View>
  );
}

function Checkbox({
  checked,
  onPress,
  disabled,
  label,
}: {
  checked: boolean;
  onPress: () => void;
  disabled?: boolean;
  label: string;
}) {
  return (
    <Pressable style={styles.checkRow} onPress={onPress} disabled={disabled} hitSlop={6}>
      <View style={[styles.checkbox, checked && styles.checkboxOn]}>
        {checked && <Text style={styles.checkMark}>✓</Text>}
      </View>
      <Text style={styles.checkLabel}>{label}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  container: { padding: spacing.xl, gap: spacing.lg, paddingBottom: spacing.xxl + 60 },
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
  consentBox: { gap: spacing.md, marginTop: spacing.sm },
  checkRow: { flexDirection: 'row', alignItems: 'flex-start', gap: spacing.md },
  checkbox: {
    width: 22,
    height: 22,
    borderRadius: 4,
    borderWidth: 1.5,
    borderColor: colors.border,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 2,
  },
  checkboxOn: { backgroundColor: colors.primary, borderColor: colors.primary },
  checkMark: { color: '#fff', fontSize: 14, fontWeight: '700' },
  checkLabel: { ...typography.body, flex: 1, fontSize: 13 },
  primaryBtn: {
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    borderRadius: radius.md,
    alignItems: 'center',
    marginTop: spacing.md,
  },
  primaryBtnText: { color: '#fff', fontWeight: '700', fontSize: 16 },
  disabled: { opacity: 0.6 },
});
