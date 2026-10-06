import type { AxiosInstance } from 'axios'

export interface StudySummary { id: number; skill_id: number; skill_name: string; title: string; completed_at: string | null }
export interface StudyContent extends StudySummary { explanation: string; code_example: string; common_mistakes: string }
export interface StudyPage { items: StudySummary[]; total: number; limit: number; offset: number }
export type StudyInput = Pick<StudyContent, 'skill_id' | 'title' | 'explanation' | 'code_example' | 'common_mistakes'>
export async function getStudy(client: AxiosInstance, id: number, signal: AbortSignal) {
  return (await client.get<StudyContent>(`/study/${id}`, { signal })).data
}
export async function getStudyPage(client: AxiosInstance, skillId: number | undefined, offset: number, signal: AbortSignal) {
  return (await client.get<StudyPage>('/study', { params: { skill_id: skillId, offset, limit: 10 }, signal })).data
}
