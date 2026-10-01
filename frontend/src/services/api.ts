import axios from 'axios'

export const api = axios.create({ baseURL: '/api/v1', timeout: 10000 })

export function errorMessage(error: unknown): string {
  if (!axios.isAxiosError(error)) return 'Não foi possível concluir. Tente novamente.'
  const status = error.response?.status
  if (status === 401) return 'E-mail ou senha inválidos.'
  if (status === 409) return 'Este e-mail já está cadastrado. Entre na sua conta.'
  if (status === 422) return 'Confira os campos informados e tente novamente.'
  if (status === 403) return 'Você não tem permissão para esta operação.'
  return 'Não foi possível conectar ao servidor. Tente novamente.'
}
