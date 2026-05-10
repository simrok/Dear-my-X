export type MessageSender = 'user' | 'persona';

export interface Message {
  id: string;
  chat_room_id: string;
  sender_type: MessageSender;
  content: string;
  created_at: string;
}

export interface MessageCreateInput {
  content: string;
}
