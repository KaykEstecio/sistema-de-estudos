import type { AxiosInstance } from 'axios'

export type Classification = 'MET' | 'PARTIALLY_MET' | 'NOT_MET' | 'INSUFFICIENT_EVIDENCE'
export interface Evaluation {
  id: number; attempt_id: number; rubric_version: 'manual-v1'; feedback: string; created_at: string
  skills: { skill_id: number; classification: Classification; justification: string }[]
}
export async function getEvaluation(client: AxiosInstance, attemptId: number, signal: AbortSignal) {
  return (await client.get<Evaluation>(`/attempts/${attemptId}/evaluation`, { signal })).data
}
