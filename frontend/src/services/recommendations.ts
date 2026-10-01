import type { AxiosInstance } from 'axios'

export interface CatalogSkill { id: number; name: string; is_active: boolean }
export interface SkillPage { items: CatalogSkill[]; total: number; limit: number; offset: number }
export interface Recommendation {
  challenge_id: number; title: string; difficulty_score: number; estimated_minutes: number
  kind: 'EXPLORATION' | 'PRACTICE' | 'PROGRESSION' | 'REVIEW'
  practiced_recently: boolean; reason: string
}
export interface Recommendations { items: Recommendation[]; empty_reason: string | null }
export interface ChallengeDetail {
  id: number; title: string; description: string; difficulty_score: number
  estimated_minutes: number; starter_code: string | null; is_active: boolean
}
export async function getSkills(client: AxiosInstance, category: number, offset: number, signal: AbortSignal) {
  return (await client.get<SkillPage>('/skills', { params: { category_id: category, is_active: true, limit: 20, offset }, signal })).data
}
export async function getRecommendations(client: AxiosInstance, skill: number, signal: AbortSignal) {
  return (await client.get<Recommendations>('/recommendations', { params: { skill_id: skill, limit: 5 }, signal })).data
}
export async function getChallenge(client: AxiosInstance, id: number, signal: AbortSignal) {
  return (await client.get<ChallengeDetail>(`/challenges/${id}`, { signal })).data
}
