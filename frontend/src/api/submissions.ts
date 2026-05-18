import request from './http'
import type { Submission } from './types'

export function getSubmissions(params?: { assignment_id?: number; course_id?: number; status?: string }) {
  return request.get<unknown, Submission[]>('/submissions', { params })
}

export function submitAssignment(payload: { assignment_id: number; content: string }) {
  return request.post<unknown, Submission>('/submissions', payload)
}

export function submitAssignmentWithFiles(payload: { assignment_id: number; content: string; files: File[] }) {
  const data = new FormData()
  data.append('assignment_id', String(payload.assignment_id))
  data.append('content', payload.content)
  payload.files.forEach((file) => data.append('files', file))
  return request.post<unknown, Submission>('/submissions/with-files', data)
}

export function updateSubmission(id: number, payload: { content: string }) {
  return request.put<unknown, Submission>(`/submissions/${id}`, payload)
}

export function updateSubmissionWithFiles(
  id: number,
  payload: { content: string; files: File[]; keep_attachment_ids: number[] }
) {
  const data = new FormData()
  data.append('content', payload.content)
  data.append('keep_attachment_ids', JSON.stringify(payload.keep_attachment_ids))
  payload.files.forEach((file) => data.append('files', file))
  return request.put<unknown, Submission>(`/submissions/${id}/with-files`, data)
}

export function gradeSubmission(id: number, payload: { grade: number; feedback?: string | null }) {
  return request.post<unknown, Submission>(`/submissions/${id}/grade`, payload)
}
