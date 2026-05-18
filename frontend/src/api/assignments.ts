import request from './http'
import type { Assignment, AssignmentPayload } from './types'

export function getAssignments(params?: { course_id?: number; only_mine?: boolean }) {
  return request.get<unknown, Assignment[]>('/assignments', { params })
}

export function getAssignment(id: number) {
  return request.get<unknown, Assignment>(`/assignments/${id}`)
}

export function createAssignment(payload: AssignmentPayload) {
  return request.post<unknown, Assignment>('/assignments', payload)
}

export function createAssignmentWithFiles(payload: AssignmentPayload, files: File[]) {
  const data = new FormData()
  data.append('course_id', String(payload.course_id))
  data.append('title', payload.title)
  data.append('deadline', payload.deadline)
  data.append('description', payload.description || '')
  files.forEach((file) => data.append('files', file))
  return request.post<unknown, Assignment>('/assignments/with-files', data)
}

export function updateAssignment(id: number, payload: Omit<AssignmentPayload, 'course_id'>) {
  return request.put<unknown, Assignment>(`/assignments/${id}`, payload)
}

export function deleteAssignment(id: number) {
  return request.delete<unknown, null>(`/assignments/${id}`)
}
