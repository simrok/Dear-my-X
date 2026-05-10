import { StyleSheet, Text, View } from 'react-native';

export function ChatScreen() {
  // TODO: 상단 프로필 / 메시지 리스트 / 하단 입력창
  return (
    <View style={styles.container}>
      <Text>채팅 (placeholder)</Text>
    </View>
  );
}

const styles = StyleSheet.create({ container: { flex: 1, padding: 16 } });
