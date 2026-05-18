import request from './http'
import type { OverviewStats } from './types'

export function getOverviewStats() {
  return request.get<unknown, OverviewStats>('/statistics/overview')
}

