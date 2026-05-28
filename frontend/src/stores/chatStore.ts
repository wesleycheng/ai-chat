import { create } from 'zustand'

interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  createdAt: Date
}

interface Conversation {
  id: string
  title: string | null
  messages: Message[]
}

interface ChatState {
  conversations: Conversation[]
  currentConversationId: string | null
  streamingContent: string
  isStreaming: boolean
  selectedModelId: string | null
  
  setCurrentConversation: (id: string | null) => void
  addConversation: (conversation: Conversation) => void
  addMessage: (conversationId: string, message: Message) => void
  setStreamingContent: (content: string) => void
  appendStreamingContent: (content: string) => void
  setIsStreaming: (isStreaming: boolean) => void
  clearStreamingContent: () => void
  setSelectedModelId: (id: string | null) => void
}

export const useChatStore = create<ChatState>((set) => ({
  conversations: [],
  currentConversationId: null,
  streamingContent: '',
  isStreaming: false,
  selectedModelId: null,
  
  setCurrentConversation: (id) => set({ currentConversationId: id }),
  
  addConversation: (conversation) =>
    set((state) => ({
      conversations: [...state.conversations, conversation],
    })),
  
  addMessage: (conversationId, message) =>
    set((state) => ({
      conversations: state.conversations.map((conv) =>
        conv.id === conversationId
          ? { ...conv, messages: [...conv.messages, message] }
          : conv
      ),
    })),
  
  setStreamingContent: (content) => set({ streamingContent: content }),
  
  appendStreamingContent: (content) =>
    set((state) => ({ streamingContent: state.streamingContent + content })),
  
  setIsStreaming: (isStreaming) => set({ isStreaming }),
  
  clearStreamingContent: () => set({ streamingContent: '' }),
  setSelectedModelId: (id) => set({ selectedModelId: id }),
}))