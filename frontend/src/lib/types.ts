export interface User {
  id: number
  full_name: string
  email: string
  role: string
  is_active: boolean
}

export interface Project {
  id: number
  project_name: string
  description?: string | null
  created_by: number
  created_at: string
}

export interface Issue {
  id: number
  title: string
  description?: string | null
  status: string
  priority: string
  severity: string
  assigned_to?: number | null
  reporter: number
  project_id: number
  created_at: string
  updated_at: string
}

export interface AiEnhanceResponse {
  enhanced_description: string
  severity: string
  priority: string
  category: string
  component: string
  root_cause: string
  resolution: string
  test_cases: string
  estimated_time: string
  confidence: string
}
