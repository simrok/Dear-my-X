import { useCallback } from 'react';
import {
  ActivityIndicator,
  Alert,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import { useNavigation, useRoute, type RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';

import { InfoCard } from '@/components/common/InfoCard';
import { Pill } from '@/components/common/Pill';
import { useUploadFlow } from '@/features/upload/useUploadFlow';
import type { RootStackParamList } from '@/navigation/types';
import { colors, radius, spacing, typography } from '@/theme';

type Nav = NativeStackNavigationProp<RootStackParamList, 'Upload'>;
type R = RouteProp<RootStackParamList, 'Upload'>;

const KAKAO_STEPS = [
  '카카오톡에서 대화방을 엽니다.',
  '우측 상단의 메뉴(≡)를 누릅니다.',
  '대화방 설정으로 들어갑니다.',
  '대화 내용 내보내기를 선택합니다.',
  '"텍스트만 보내기" 또는 "텍스트로 저장"을 선택합니다.',
  '생성된 .txt 파일을 Dear my X에 업로드합니다.',
];

export function UploadScreen() {
  const route = useRoute<R>();
  const navigation = useNavigation<Nav>();
  const { personaId } = route.params;
  const flow = useUploadFlow(personaId);

  const onPickFile = useCallback(async () => {
    flow.startPicking();
    try {
      const res = await DocumentPicker.getDocumentAsync({
        type: ['text/plain', 'text/*'],
        copyToCacheDirectory: true,
        multiple: false,
      });
      if (res.canceled || !res.assets?.[0]) {
        flow.cancelPicking();
        return;
      }
      const a = res.assets[0];
      await flow.upload({ uri: a.uri, name: a.name, mimeType: a.mimeType });
    } catch (e) {
      Alert.alert('파일 선택 실패', String(e));
      flow.cancelPicking();
    }
  }, [flow]);

  const onCaptureOnly = useCallback(() => {
    Alert.alert(
      '캡처 업로드는 아직 지원하지 않아요',
      '현재는 카카오톡의 "대화 내용 내보내기 → 텍스트로 저장"으로 만든 .txt 파일만 분석할 수 있어요. 위의 안내를 따라 .txt 파일을 만들어 업로드해 주세요.',
    );
  }, []);

  const onDone = useCallback(() => {
    navigation.goBack();
  }, [navigation]);

  // ---------- 단계별 화면 ----------
  return (
    <ScrollView style={{ flex: 1, backgroundColor: colors.bg }} contentContainerStyle={styles.container}>
      {/* 안내 카드 */}
      <InfoCard title="카카오톡 .txt 파일 만드는 방법" steps={KAKAO_STEPS} />

      {/* 진행 영역 */}
      {flow.step === 'idle' || flow.step === 'picking' || flow.step === 'error' ? (
        <View style={styles.actions}>
          <Pressable
            style={[styles.primaryBtn, flow.step === 'picking' && styles.disabled]}
            onPress={onPickFile}
            disabled={flow.step === 'picking'}
          >
            {flow.step === 'picking' ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.primaryBtnText}>txt 파일 업로드하기</Text>
            )}
          </Pressable>

          <Pressable style={styles.secondaryBtn} onPress={onCaptureOnly}>
            <Text style={styles.secondaryBtnText}>캡처밖에 없어요</Text>
          </Pressable>

          {flow.step === 'error' && flow.error && (
            <View style={styles.errorBox}>
              <Text style={styles.errorText}>{flow.error}</Text>
              <Pressable onPress={flow.reset} hitSlop={6}>
                <Text style={styles.retryText}>다시 시도</Text>
              </Pressable>
            </View>
          )}
        </View>
      ) : null}

      {flow.step === 'uploading' && (
        <View style={styles.statusBox}>
          <ActivityIndicator />
          <Text style={styles.statusText}>업로드 중…</Text>
        </View>
      )}

      {flow.step === 'choose-speaker' && flow.preview && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>AI 페르소나로 사용할 발화자를 골라주세요</Text>
          <Text style={styles.sectionHint}>
            메시지 {flow.preview.message_count.toLocaleString()}건 ·{' '}
            형식 {flow.preview.detected_format} · 무시된 줄 {flow.preview.skipped_lines}
          </Text>
          <View style={styles.pillRow}>
            {flow.preview.speakers.map((s) => (
              <Pill key={s} label={s} selected={false} onPress={() => flow.ingest(s)} />
            ))}
          </View>
        </View>
      )}

      {flow.step === 'ingesting' && (
        <View style={styles.statusBox}>
          <ActivityIndicator />
          <Text style={styles.statusText}>마스킹 → 청크 → 임베딩 중…</Text>
          <Text style={styles.statusHint}>대화 양에 따라 수십 초가 걸릴 수 있어요.</Text>
        </View>
      )}

      {flow.step === 'done' && flow.result && (
        <View style={[styles.statusBox, styles.successBox]}>
          <Text style={styles.statusTitle}>완료!</Text>
          <Text style={styles.statusText}>
            {flow.result.speaker} 발화 → {flow.result.chunks_created}개 chunk 저장됨
          </Text>
          {Object.keys(flow.result.masked_counts).length > 0 && (
            <Text style={styles.statusHint}>
              마스킹: {Object.entries(flow.result.masked_counts).map(([k, v]) => `${k}×${v}`).join(', ')}
            </Text>
          )}
          <Pressable style={[styles.primaryBtn, { marginTop: spacing.md }]} onPress={onDone}>
            <Text style={styles.primaryBtnText}>완료</Text>
          </Pressable>
        </View>
      )}

      <Text style={styles.footnote}>
        업로드된 파일은 가상 페르소나 학습 외 다른 용도로 사용되지 않습니다. 개인정보(전화번호/이메일/계좌 등)는
        자동으로 마스킹됩니다.
      </Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: spacing.xl, gap: spacing.lg, paddingBottom: spacing.xxl },
  actions: { gap: spacing.md },
  primaryBtn: {
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    borderRadius: radius.md,
    alignItems: 'center',
  },
  primaryBtnText: { color: '#fff', fontWeight: '700', fontSize: 16 },
  secondaryBtn: {
    paddingVertical: spacing.md,
    borderRadius: radius.md,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.border,
  },
  secondaryBtnText: { color: colors.text, fontWeight: '600' },
  disabled: { opacity: 0.6 },
  errorBox: {
    padding: spacing.md,
    backgroundColor: '#FFE5E5',
    borderRadius: radius.md,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: spacing.md,
  },
  errorText: { color: colors.danger, flex: 1, fontSize: 12 },
  retryText: { color: colors.danger, fontWeight: '600' },
  statusBox: {
    padding: spacing.lg,
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    alignItems: 'center',
    gap: spacing.sm,
  },
  successBox: { backgroundColor: '#E8F5E9' },
  statusTitle: { ...typography.body, fontWeight: '700', fontSize: 16 },
  statusText: { ...typography.body, fontSize: 14 },
  statusHint: { ...typography.caption },
  section: { gap: spacing.md },
  sectionTitle: { ...typography.body, fontWeight: '600' },
  sectionHint: { ...typography.caption },
  pillRow: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm },
  footnote: { ...typography.caption, fontSize: 11, marginTop: spacing.lg },
});
