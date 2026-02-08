/**
 * Server-Sent Events (SSE) client for real-time generation progress updates
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:2501';

// ============================================================================
// Types
// ============================================================================

export interface SSEMessage {
  type: 'progress' | 'partial' | 'complete' | 'error';
  data: any;
}

export interface GenerationProgress {
  progress: number; // 0-100
  step: string;
  message?: string;
  estimatedTimeRemaining?: number;
  currentCost?: number;
}

export interface PartialResult {
  type: 'concept' | 'screenplay' | 'scene' | 'document';
  data: any;
}

export type SSECallback = (message: SSEMessage) => void;
export type SSEErrorCallback = (error: Error) => void;

// ============================================================================
// SSE Client
// ============================================================================

export class SSEClient {
  private eventSource: EventSource | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private maxReconnectDelay = 30000; // Max 30 seconds
  private callbacks: Set<SSECallback> = new Set();
  private errorCallbacks: Set<SSEErrorCallback> = new Set();
  private isManualClose = false;

  constructor(private jobId: string) {}

  /**
   * Connect to SSE endpoint and start receiving updates
   */
  connect(): void {
    if (this.eventSource) {
      return; // Already connected
    }

    this.isManualClose = false;
    const token = localStorage.getItem('auth_token');
    const url = new URL(`${API_BASE_URL}/api/stream/generation/${this.jobId}`);

    if (token) {
      url.searchParams.append('token', token);
    }

    try {
      this.eventSource = new EventSource(url.toString());

      this.eventSource.onopen = () => {
        console.log(`SSE connected for job ${this.jobId}`);
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;
      };

      this.eventSource.onmessage = (event) => {
        try {
          const message: SSEMessage = JSON.parse(event.data);
          this.notifyCallbacks(message);

          // Auto-close on completion or error
          if (message.type === 'complete' || message.type === 'error') {
            this.close();
          }
        } catch (error) {
          console.error('Failed to parse SSE message:', error);
        }
      };

      this.eventSource.onerror = (error) => {
        console.error('SSE error:', error);

        if (!this.isManualClose && this.shouldReconnect()) {
          this.reconnect();
        } else {
          this.notifyErrorCallbacks(
            new Error('SSE connection failed after maximum retry attempts')
          );
          this.close();
        }
      };

      // Listen for specific event types
      this.eventSource.addEventListener('progress', (event) => {
        this.handleEvent('progress', event);
      });

      this.eventSource.addEventListener('partial', (event) => {
        this.handleEvent('partial', event);
      });

      this.eventSource.addEventListener('complete', (event) => {
        this.handleEvent('complete', event);
      });

      this.eventSource.addEventListener('error', (event: Event) => {
        // For error events, we don't have message data
        this.notifyErrorCallbacks(new Error('SSE connection error'));
      });
    } catch (error) {
      this.notifyErrorCallbacks(
        error instanceof Error ? error : new Error('Failed to create EventSource')
      );
    }
  }

  /**
   * Handle specific event types
   */
  private handleEvent(type: SSEMessage['type'], event: MessageEvent): void {
    try {
      const data = JSON.parse(event.data);
      this.notifyCallbacks({ type, data });
    } catch (error) {
      console.error(`Failed to parse ${type} event:`, error);
    }
  }

  /**
   * Check if we should attempt to reconnect
   */
  private shouldReconnect(): boolean {
    return this.reconnectAttempts < this.maxReconnectAttempts;
  }

  /**
   * Attempt to reconnect with exponential backoff
   */
  private reconnect(): void {
    this.reconnectAttempts++;
    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
      this.maxReconnectDelay
    );

    console.log(
      `Reconnecting SSE in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`
    );

    setTimeout(() => {
      if (this.eventSource) {
        this.eventSource.close();
        this.eventSource = null;
      }
      this.connect();
    }, delay);
  }

  /**
   * Subscribe to SSE messages
   */
  subscribe(callback: SSECallback): () => void {
    this.callbacks.add(callback);

    // Return unsubscribe function
    return () => {
      this.callbacks.delete(callback);
    };
  }

  /**
   * Subscribe to SSE errors
   */
  onError(callback: SSEErrorCallback): () => void {
    this.errorCallbacks.add(callback);

    // Return unsubscribe function
    return () => {
      this.errorCallbacks.delete(callback);
    };
  }

  /**
   * Notify all subscribers of a new message
   */
  private notifyCallbacks(message: SSEMessage): void {
    this.callbacks.forEach((callback) => {
      try {
        callback(message);
      } catch (error) {
        console.error('Error in SSE callback:', error);
      }
    });
  }

  /**
   * Notify all error subscribers
   */
  private notifyErrorCallbacks(error: Error): void {
    this.errorCallbacks.forEach((callback) => {
      try {
        callback(error);
      } catch (err) {
        console.error('Error in SSE error callback:', err);
      }
    });
  }

  /**
   * Close the SSE connection
   */
  close(): void {
    this.isManualClose = true;
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    this.callbacks.clear();
    this.errorCallbacks.clear();
  }

  /**
   * Check if currently connected
   */
  isConnected(): boolean {
    return (
      this.eventSource !== null &&
      this.eventSource.readyState === EventSource.OPEN
    );
  }
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Create and connect an SSE client for a job
 */
export function createSSEClient(jobId: string): SSEClient {
  const client = new SSEClient(jobId);
  client.connect();
  return client;
}

/**
 * Subscribe to generation progress updates
 */
export function subscribeToProgress(
  jobId: string,
  onProgress: (progress: GenerationProgress) => void,
  onPartial?: (result: PartialResult) => void,
  onComplete?: (result: any) => void,
  onError?: (error: Error) => void
): () => void {
  const client = createSSEClient(jobId);

  const unsubscribe = client.subscribe((message) => {
    switch (message.type) {
      case 'progress':
        onProgress(message.data as GenerationProgress);
        break;
      case 'partial':
        onPartial?.(message.data as PartialResult);
        break;
      case 'complete':
        onComplete?.(message.data);
        client.close();
        break;
      case 'error':
        onError?.(new Error(message.data.message || 'Generation failed'));
        client.close();
        break;
    }
  });

  if (onError) {
    client.onError(onError);
  }

  // Return cleanup function
  return () => {
    unsubscribe();
    client.close();
  };
}

export default SSEClient;
