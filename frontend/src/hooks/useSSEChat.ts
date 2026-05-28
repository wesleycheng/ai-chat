import { useCallback } from 'react'
import { EventSourcePolyfill } from 'event-source-polyfill'
import { useAuthStore } from '../stores/authStore'
import { useChatStore } from '../stores/chatStore'

interface SSEEvent extends MessageEvent {
  data: string
}

export function useSSEChat() {
  const { token } = useAuthStore()
  const {
    appendStreamingContent,
    setIsStreaming,
    clearStreamingContent,
  } = useChatStore()

  const sendMessage = useCallback(
    async (conversationId: string, content: string, options?: { file_ids?: string[] }) => {
      clearStreamingContent()
      setIsStreaming(true)

      const eventSource = new EventSourcePolyfill(
        `/api/conversations/${conversationId}/chat?content=${encodeURIComponent(content)}&stream=true`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          method: 'POST',
          body: JSON.stringify({
            content,
            file_ids: options?.file_ids || [],
          }),
        }
      )

      return new Promise<string>((resolve, reject) => {
        let fullContent = ''

        eventSource.onmessage = (event: SSEEvent) => {
          try {
            const data = JSON.parse(event.data)

            if (data.done) {
              eventSource.close()
              setIsStreaming(false)
              resolve(fullContent)
            } else if (data.content) {
              fullContent += data.content
              appendStreamingContent(data.content)
            }
          } catch (err: unknown) {
            console.error('Failed to parse SSE data:', err)
          }
        }

        eventSource.onerror = (err: Event) => {
          eventSource.close()
          setIsStreaming(false)
          reject(err)
        }
      })
    },
    [token, appendStreamingContent, setIsStreaming, clearStreamingContent]
  )

  return { sendMessage }
}
