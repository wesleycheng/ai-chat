declare module 'event-source-polyfill' {
  export class EventSourcePolyfill {
    constructor(url: string, options?: {
      headers?: Record<string, string>
      method?: string
      body?: string
    })
    onmessage: ((event: MessageEvent) => void) | null
    onerror: ((event: Event) => void) | null
    close(): void
    readyState: number
    readonly CONNECTING = 0
    readonly OPEN = 1
    readonly CLOSED = 2
  }
}
