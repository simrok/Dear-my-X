// 디자인 토큰 (모바일 우선).
// 추후 web 추가 시에도 동일 토큰을 활용 가능하도록 일반화.

export const colors = {
  bg: '#FFFFFF',
  surface: '#F7F7F8',
  text: '#1A1A1A',
  textMuted: '#666666',
  primary: '#7B61FF',
  bubbleMe: '#FFE066',
  bubbleAi: '#F0F0F0',
  border: '#E5E5E5',
  danger: '#E53E3E',
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  xxl: 32,
} as const;

export const radius = {
  sm: 6,
  md: 12,
  lg: 20,
  pill: 999,
} as const;

export const typography = {
  title: { fontSize: 22, fontWeight: '700' as const },
  body: { fontSize: 14, lineHeight: 22 },
  caption: { fontSize: 12, color: colors.textMuted },
} as const;
