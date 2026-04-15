export type StageType =
  | '刚结课'
  | '已激活'
  | '已联系'
  | '有兴趣'
  | '明确需求'
  | '高意向'
  | '已成交'
  | '沉默'
  | '流失'

export interface Student {
  id: number
  name: string
  wechat?: string
  phone?: string
  course_name?: string
  class_name?: string
  graduation_date?: string
  current_direction?: string
  current_stage: StageType
  intent_level?: string
  owner?: string
  last_interaction_at?: string
  next_follow_time?: string
  remark?: string
  created_at: string
  updated_at: string
}

export interface Profile {
  id: number
  student_id: number
  user_type?: string
  main_goal?: string
  main_concerns?: string
  interest_direction?: string
  risk_tags?: string
  recommended_course?: string
  recommended_action?: string
  summary?: string
  updated_at: string
}

export interface ChatRecord {
  id: number
  student_id: number
  content: string
  source?: string
  created_at: string
}

export interface AIAnalysis {
  id: number
  student_id: number
  chat_record_id?: number
  stage?: string
  main_need?: string
  core_concerns?: string
  interest_direction?: string
  risk_points?: string
  recommended_course?: string
  recommended_action?: string
  tags?: string[]
  tags_json?: string
  summary?: string
  raw_json?: string
  created_at: string
}

export interface FollowUp {
  id: number
  student_id: number
  follow_time: string
  follow_method?: string
  content: string
  student_feedback?: string
  judgment?: string
  next_action?: string
  next_follow_time?: string
  created_at: string
}

export interface Asset {
  id: number
  asset_type: string
  title: string
  scene?: string
  stage?: string
  direction?: string
  content?: string
  link?: string
  description?: string
  created_at: string
  updated_at: string
}

export interface ApiResp<T> {
  success: boolean
  message: string
  data: T
}
