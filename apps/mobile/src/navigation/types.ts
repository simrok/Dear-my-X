// 루트 네비게이션 타입.
export type RootStackParamList = {
  Onboarding: undefined;
  Login: undefined;
  Main: undefined;
  CreatePersona: undefined;
  PersonaDetail: { personaId: string };
  Upload: { personaId: string };
  Chat: { chatRoomId: string; personaId: string };
};

export type MainTabParamList = {
  Home: undefined;
  Settings: undefined;
};
