export type Role = 'student' | 'teacher' | 'admin'

export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface UserProfile {
  id: number
  username: string
  real_name: string
  role: Role
  profile_id: number | null
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: UserProfile
}

export interface Course {
  id: number
  name: string
  description: string | null
  teacher_id: number
  teacher_name: string
  credit: number
  capacity: number
  selected_count: number
  is_selected: boolean
  created_at: string
  schedules: CourseSchedule[]
}

export interface CourseSchedule {
  id?: number
  course_id?: number
  weekday: number
  start_section: number
  end_section: number
  start_time: string
  end_time: string
  classroom: string
  weeks: string
  term: string
}

export interface CoursePayload {
  name: string
  description: string | null
  teacher_id: number
  credit: number
  capacity: number
  schedules: CourseSchedule[]
}

export interface CourseStudent {
  student_id: number
  student_no: string
  real_name: string
  major: string | null
  class_name: string | null
  selected_at: string
}

export interface Attachment {
  id: number
  original_name: string
  url: string
  content_type: string | null
  size: number
  is_image: boolean
  created_at: string
}

export interface Assignment {
  id: number
  course_id: number
  course_name: string
  title: string
  description: string | null
  deadline: string
  status: 'open' | 'closed'
  submitted: boolean
  submission_id: number | null
  submission_status: string | null
  grade: number | null
  max_score: number
  assignment_type: string
  required_level: string
  created_at: string
  attachments: Attachment[]
}

export interface AssignmentPayload {
  course_id: number
  title: string
  description: string | null
  deadline: string
}

export interface Submission {
  id: number
  assignment_id: number
  assignment_title: string
  course_id: number
  course_name: string
  student_id: number
  student_no: string
  student_name: string
  content: string
  grade: number | null
  feedback: string | null
  submit_time: string
  graded_at: string | null
  status: 'submitted' | 'graded'
  attachments: Attachment[]
}

export interface StatCard {
  label: string
  value: number | string
  trend: string
}

export interface OverviewStats {
  cards: StatCard[]
  submission_status: Array<{ name: string; value: number }>
  grade_distribution: Array<{ range: string; count: number }>
  course_assignment_counts: Array<{ course: string; assignments: number; submissions: number }>
  grade_by_course: Array<{ course: string; average: number; graded_count: number }>
  weekly_schedule: WeeklyScheduleItem[]
  recent_activities: Array<{ id: number; title: string; description: string | null; created_at: string }>
}

export interface EnrollmentSetting {
  id: number
  term: string
  is_open: boolean
  start_time: string
  end_time: string
  current_week: number
}

export interface WeeklyScheduleItem {
  course_id: number
  course_name: string
  teacher_name: string
  weekday: number
  start_section: number
  end_section: number
  start_time: string
  end_time: string
  classroom: string
  weeks: string
  term: string
}

export interface StudentAdmin {
  id: number
  user_id: number
  username: string
  real_name: string
  student_no: string
  major: string | null
  class_name: string | null
  is_active: boolean
}

export interface TeacherAdmin {
  id: number
  user_id: number
  username: string
  real_name: string
  teacher_no: string
  title: string | null
  department: string | null
  is_active: boolean
}
