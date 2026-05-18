import request from './http'
import type { StudentAdmin, TeacherAdmin } from './types'

export function getStudents() {
  return request.get<unknown, StudentAdmin[]>('/users/students')
}

export function createStudent(payload: Record<string, unknown>) {
  return request.post<unknown, StudentAdmin>('/users/students', payload)
}

export function updateStudent(id: number, payload: Record<string, unknown>) {
  return request.put<unknown, StudentAdmin>(`/users/students/${id}`, payload)
}

export function getTeachers() {
  return request.get<unknown, TeacherAdmin[]>('/users/teachers')
}

export function createTeacher(payload: Record<string, unknown>) {
  return request.post<unknown, TeacherAdmin>('/users/teachers', payload)
}

export function updateTeacher(id: number, payload: Record<string, unknown>) {
  return request.put<unknown, TeacherAdmin>(`/users/teachers/${id}`, payload)
}

export function disableUser(id: number) {
  return request.post<unknown, null>(`/users/${id}/disable`)
}

