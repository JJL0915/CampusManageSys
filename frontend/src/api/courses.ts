import request from './http'
import type { Course, CoursePayload, CourseStudent, EnrollmentSetting, WeeklyScheduleItem } from './types'

export function getCourses(params?: { keyword?: string; only_mine?: boolean }) {
  return request.get<unknown, Course[]>('/courses', { params })
}

export function createCourse(payload: CoursePayload) {
  return request.post<unknown, Course>('/courses', payload)
}

export function updateCourse(id: number, payload: CoursePayload) {
  return request.put<unknown, Course>(`/courses/${id}`, payload)
}

export function deleteCourse(id: number) {
  return request.delete<unknown, null>(`/courses/${id}`)
}

export function enrollCourse(id: number) {
  return request.post<unknown, Course>(`/courses/${id}/enroll`)
}

export function cancelEnrollment(id: number) {
  return request.delete<unknown, null>(`/courses/${id}/enroll`)
}

export function adminRemoveEnrollment(courseId: number, studentId: number) {
  return request.delete<unknown, null>(`/courses/${courseId}/students/${studentId}/enroll`)
}

export function getCourseStudents(id: number) {
  return request.get<unknown, CourseStudent[]>(`/courses/${id}/students`)
}

export function getEnrollmentSetting() {
  return request.get<unknown, EnrollmentSetting>('/courses/enrollment/settings')
}

export function updateEnrollmentSetting(payload: Omit<EnrollmentSetting, 'id'>) {
  return request.put<unknown, EnrollmentSetting>('/courses/enrollment/settings', payload)
}

export function getWeeklySchedule(params?: { week?: number; term?: string }) {
  return request.get<unknown, WeeklyScheduleItem[]>('/courses/schedule/weekly', { params })
}
