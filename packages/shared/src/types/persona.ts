export type RelationType = 'ex_partner' | 'friend' | 'family' | 'other';

export interface Persona {
  id: string;
  user_id: string;
  name: string;
  relation_type: RelationType;
  personality: string | null;
  speaking_style: string | null;
  profile_image_url: string | null;
  safety_notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface PersonaCreateInput {
  name: string;
  relation_type: RelationType;
  personality?: string | null;
  speaking_style?: string | null;
  profile_image_url?: string | null;
  safety_notes?: string | null;
  consent_virtual_persona: boolean;
  consent_data_rights: boolean;
}
