import axios from 'axios'

export async function checkHealth(signal: AbortSignal): Promise<void> {
  const { data } = await axios.get<unknown>('/health', {
    signal,
    timeout: 5000,
  })

  if (typeof data !== 'object' || data === null || !('status' in data) || data.status !== 'ok') {
    throw new Error('Resposta de saúde inválida.')
  }
}
