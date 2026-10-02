import type { AxiosInstance } from 'axios'

export interface AttemptSummary {
  id: number; challenge_id: number; title: string; status: 'IN_PROGRESS' | 'SUBMITTED'
  attempt_number: number; started_at: string; submitted_at: string | null; last_activity_at: string
}
export interface AttemptPage { items: AttemptSummary[]; total: number; limit: number; offset: number }
export interface Attempt extends Omit<AttemptSummary, 'title'> {
  draft_answer: string
  challenge_snapshot: { title: string; description: string; challenge_type: string; difficulty: string
    difficulty_score: number; estimated_minutes: number; starter_code: string | null
    skills: { skill_id: number; weight: number }[] }
}
export async function getAttempts(client: AxiosInstance, offset: number, signal: AbortSignal) {
  return (await client.get<AttemptPage>('/attempts', { params: { limit: 10, offset }, signal })).data
}
export async function getAttempt(client: AxiosInstance, id: number, signal: AbortSignal) {
  return (await client.get<Attempt>(`/attempts/${id}`, { signal })).data
}
export async function startAttempt(client: AxiosInstance, id: number, signal: AbortSignal) {
  return (await client.post<Attempt>(`/challenges/${id}/attempts`, undefined, { signal })).data
}

export async function saveAttempt(client: AxiosInstance, id: number, answer: string, signal: AbortSignal) {
  return (await client.patch<Attempt>(`/attempts/${id}`, { draft_answer: answer }, { signal })).data
}

export async function submitAttempt(client: AxiosInstance, id: number, signal: AbortSignal) {
  return (await client.post<Attempt>(`/attempts/${id}/submit`, undefined, { signal })).data
}
