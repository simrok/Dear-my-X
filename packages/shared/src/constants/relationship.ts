import type { RelationType } from '../types/persona';

export const RELATION_LABELS: Record<RelationType, string> = {
  ex_partner: '전 연인',
  friend: '친구',
  family: '가족',
  other: '기타',
};

export const RELATION_OPTIONS: Array<{ value: RelationType; label: string }> = [
  { value: 'ex_partner', label: RELATION_LABELS.ex_partner },
  { value: 'friend', label: RELATION_LABELS.friend },
  { value: 'family', label: RELATION_LABELS.family },
  { value: 'other', label: RELATION_LABELS.other },
];
