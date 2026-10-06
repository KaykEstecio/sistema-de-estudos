import type { AxiosInstance } from 'axios'
import type { Attempt, AttemptPage } from './attempts'
import type { Evaluation } from './evaluation'

export interface Review { attempt: Attempt; evaluation: Evaluation | null }
export type EvaluationInput = Pick<Evaluation, 'feedback' | 'skills'>
export async function getReviews(client: AxiosInstance, offset: number, signal: AbortSignal) {
  return (await client.get<AttemptPage>('/reviews/attempts', { params: { limit: 10, offset }, signal })).data
}
export async function getReview(client: AxiosInstance, id: number, signal: AbortSignal) {
  return (await client.get<Review>(`/reviews/attempts/${id}`, { signal })).data
}
export async function createEvaluation(client: AxiosInstance, id: number, data: EvaluationInput, signal: AbortSignal) {
  return (await client.post<Evaluation>(`/reviews/attempts/${id}/evaluation`, data, { signal })).data
}
