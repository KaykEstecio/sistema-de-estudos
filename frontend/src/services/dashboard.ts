import type { AxiosInstance } from 'axios'

export interface DashboardSkill {
  skill_id: number; name: string; is_active: boolean; score: number; confidence: string
  attempts: number; successful_attempts: number; last_practiced_at: string; updated_at: string
}
export interface Dashboard {
  profile: {
    name: string; onboarding_completed: boolean
    primary_goal: { goal_type: string; description: string | null } | null
    interests: { category_id: number; name: string }[]
  }
  summary: { tracked_skills: number; submitted_attempts: number; pending_reviews: number }
  progress: { items: DashboardSkill[]; total: number; limit: number; offset: number }
}

export async function getDashboard(client: AxiosInstance, offset: number, signal: AbortSignal) {
  const { data } = await client.get<Dashboard>('/dashboard', { params: { limit: 10, offset }, signal })
  return data
}
