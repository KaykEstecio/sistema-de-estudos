import axios from 'axios'

export type Option = 'A' | 'B' | 'C' | 'D'
export interface Item { id: number; skill_id: number; position: number; prompt: string; options: Record<Option, string>; selected_option: Option | null }
export interface Assessment { id: number; completed_at: string | null; items: Item[]; results: { skill_id: number; score: number; confidence: number; correct_count: number; question_count: number }[] }
export interface Skill { id: number; name: string }
export function validId(value: string) { return /^[1-9]\d*$/.test(value) && Number(value) <= 2147483647 }
const key = (userId: number) => `codetrack:last-assessment:${userId}`
export function lastAssessment(userId: number): string {
  try { const value = localStorage.getItem(key(userId)) ?? ''; return validId(value) ? value : '' } catch { return '' }
}
export function rememberAssessment(userId: number, id: number) {
  try { localStorage.setItem(key(userId), String(id)) } catch { /* O link continua disponível sem armazenamento. */ }
}
export function forgetAssessment(userId: number, id: string) {
  try { if (lastAssessment(userId) === id) localStorage.removeItem(key(userId)) } catch { /* Armazenamento opcional. */ }
}
export function assessmentError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (error.response?.status === 404) return 'Diagnóstico ou conteúdo indisponível para esta conta.'
    if (error.response?.status === 403) return 'Sua conta não tem permissão para esta operação.'
    if (error.response?.status === 422) return 'Confira a seleção e os dados informados.'
    if (error.response?.status === 409 && typeof error.response.data?.detail === 'string') return error.response.data.detail
  }
  return 'Não foi possível concluir a operação. Tente novamente; respostas já salvas permanecem no servidor.'
}
