<template>
  <section>
    <div class="page-head">
      <div>
        <h2>课程管理</h2>
        <p>{{ hintText }}</p>
      </div>
      <div class="toolbar">
        <el-input v-model="keyword" clearable placeholder="搜索课程" style="width: 220px" @clear="loadData" @keyup.enter="loadData">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-button :icon="Refresh" @click="refreshAll">刷新</el-button>
        <el-button v-if="auth.user?.role === 'admin'" type="primary" :icon="Plus" @click="openCreate">新增课程</el-button>
      </div>
    </div>

    <section v-if="auth.user?.role === 'admin'" class="panel" style="margin-bottom: 18px">
      <div class="toolbar">
        <div>
          <h3 style="margin: 0 0 6px">选课开放设置</h3>
          <p style="margin: 0; color: var(--muted)">学生只能在开放时间内选课，退课由管理员处理。</p>
        </div>
        <el-button type="primary" @click="saveEnrollmentSetting">保存设置</el-button>
      </div>
      <div class="form-grid">
        <el-form-item label="当前学期">
          <el-input v-model="settingForm.term" />
        </el-form-item>
        <el-form-item label="当前周">
          <el-input-number v-model="settingForm.current_week" :min="1" :max="30" style="width: 100%" />
        </el-form-item>
        <el-form-item label="开始时间">
          <el-input v-model="settingForm.start_time" type="datetime-local" />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-input v-model="settingForm.end_time" type="datetime-local" />
        </el-form-item>
      </div>
      <el-switch v-model="settingForm.is_open" active-text="开放选课" inactive-text="关闭选课" />
    </section>

    <div class="table-card">
      <el-table :data="courses" v-loading="loading">
        <el-table-column prop="name" label="课程名称" min-width="150" />
        <el-table-column prop="teacher_name" label="授课教师" width="120" />
        <el-table-column prop="credit" label="学分" width="80" />
        <el-table-column label="容量" width="130">
          <template #default="{ row }">{{ row.selected_count }} / {{ row.capacity }}</template>
        </el-table-column>
        <el-table-column label="上课安排" min-width="260">
          <template #default="{ row }">
            <div class="schedule-summary">
              <el-tag v-for="item in row.schedules" :key="`${item.weekday}-${item.start_section}-${item.classroom}`" size="small">
                {{ scheduleText(item) }}
              </el-tag>
              <span v-if="!row.schedules.length">未设置</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="课程描述" min-width="220" show-overflow-tooltip />
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button v-if="auth.user?.role === 'student' && !row.is_selected" size="small" type="primary" :icon="Check" @click="handleEnroll(row.id)">选课</el-button>
            <el-tag v-if="auth.user?.role === 'student' && row.is_selected" type="success">已选</el-tag>
            <el-button v-if="auth.user?.role !== 'student'" size="small" :icon="UserFilled" @click="openStudents(row)">学生</el-button>
            <el-button v-if="auth.user?.role === 'admin'" size="small" :icon="Edit" @click="openEdit(row)">编辑</el-button>
            <el-button v-if="auth.user?.role === 'admin'" size="small" type="danger" :icon="Delete" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <WeeklySchedule
      style="margin-top: 18px"
      title="本周课表"
      subtitle="支持周次切换，按课程安排展示"
      :entries="scheduleEntries"
      :week="currentWeek"
      variant="time"
      show-controls
      :show-teacher="auth.user?.role === 'admin'"
      @prev="changeWeek(-1)"
      @next="changeWeek(1)"
      @today="resetWeek"
    />

    <el-dialog v-model="courseDialog" :title="editingCourse ? '编辑课程' : '新增课程'" width="760px">
      <el-form label-position="top">
        <div class="form-grid">
          <el-form-item label="课程名称">
            <el-input v-model="courseForm.name" />
          </el-form-item>
          <el-form-item label="授课教师">
            <el-select v-model="courseForm.teacher_id" style="width: 100%">
              <el-option v-for="teacher in teachers" :key="teacher.id" :label="teacher.real_name" :value="teacher.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="学分">
            <el-input-number v-model="courseForm.credit" :min="1" :max="8" style="width: 100%" />
          </el-form-item>
          <el-form-item label="容量">
            <el-input-number v-model="courseForm.capacity" :min="1" :max="500" style="width: 100%" />
          </el-form-item>
        </div>
        <el-form-item label="课程描述">
          <el-input v-model="courseForm.description" type="textarea" :rows="3" />
        </el-form-item>

        <div class="toolbar">
          <h3 style="margin: 0">上课安排</h3>
          <el-button :icon="Plus" @click="addSchedule">添加安排</el-button>
        </div>
        <div class="schedule-editor">
          <article v-for="(item, index) in courseForm.schedules" :key="index" class="schedule-edit-row">
            <el-select v-model="item.weekday" style="width: 100px">
              <el-option v-for="day in days" :key="day.value" :label="day.label" :value="day.value" />
            </el-select>
            <el-input-number
              v-model="item.start_section"
              :min="1"
              :max="9"
              :step="2"
              style="width: 120px"
              @change="syncScheduleTime(item)"
            />
            <span>至</span>
            <el-input-number v-model="item.end_section" :min="2" :max="10" :step="2" disabled style="width: 120px" />
            <el-input v-model="item.start_time" readonly style="width: 110px" placeholder="08:00" />
            <el-input v-model="item.end_time" readonly style="width: 110px" placeholder="09:35" />
            <el-input v-model="item.classroom" style="width: 160px" placeholder="教室" />
            <el-input v-model="item.weeks" style="width: 120px" placeholder="1-16" />
            <el-tag type="info">{{ settingForm.term }}</el-tag>
            <el-button :icon="Delete" circle @click="removeSchedule(index)" />
          </article>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="courseDialog = false">取消</el-button>
        <el-button type="primary" @click="saveCourse">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="studentDialog" title="选课学生" width="780px">
      <el-table :data="students">
        <el-table-column prop="student_no" label="学号" width="130" />
        <el-table-column prop="real_name" label="姓名" width="120" />
        <el-table-column prop="major" label="专业" />
        <el-table-column prop="class_name" label="班级" />
        <el-table-column v-if="auth.user?.role === 'admin'" label="操作" width="110">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click="handleAdminDrop(row.student_id)">退课</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { Check, Delete, Edit, Plus, Refresh, Search, UserFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  adminRemoveEnrollment,
  createCourse,
  deleteCourse,
  enrollCourse,
  getCourseStudents,
  getCourses,
  getEnrollmentSetting,
  getWeeklySchedule,
  updateCourse,
  updateEnrollmentSetting
} from '../../api/courses'
import { getTeachers } from '../../api/users'
import type { Course, CoursePayload, CourseSchedule, CourseStudent, TeacherAdmin, WeeklyScheduleItem } from '../../api/types'
import WeeklySchedule from '../../components/WeeklySchedule.vue'
import { useAuthStore } from '../../stores/auth'
import { toDatetimeLocal } from '../../utils/time'

const auth = useAuthStore()
const courses = ref<Course[]>([])
const teachers = ref<TeacherAdmin[]>([])
const students = ref<CourseStudent[]>([])
const scheduleEntries = ref<WeeklyScheduleItem[]>([])
const keyword = ref('')
const loading = ref(false)
const courseDialog = ref(false)
const studentDialog = ref(false)
const editingCourse = ref<Course | null>(null)
const activeCourse = ref<Course | null>(null)
const currentWeek = ref(12)

const days = [
  { label: '周一', value: 1 },
  { label: '周二', value: 2 },
  { label: '周三', value: 3 },
  { label: '周四', value: 4 },
  { label: '周五', value: 5 },
  { label: '周六', value: 6 },
  { label: '周日', value: 7 }
]

const sectionSlots = [
  { start: 1, end: 2, startTime: '08:00', endTime: '09:35' },
  { start: 3, end: 4, startTime: '10:00', endTime: '11:35' },
  { start: 5, end: 6, startTime: '14:00', endTime: '15:35' },
  { start: 7, end: 8, startTime: '16:00', endTime: '17:35' },
  { start: 9, end: 10, startTime: '19:00', endTime: '20:35' }
]

const settingForm = reactive({
  term: '2025-2026-2',
  is_open: true,
  start_time: '',
  end_time: '',
  current_week: 12
})

const courseForm = reactive<CoursePayload>({
  name: '',
  description: '',
  teacher_id: 0,
  credit: 3,
  capacity: 60,
  schedules: []
})

const hintText = computed(() => {
  if (auth.user?.role === 'student') return '查看课程安排，在开放选课时间内完成选课。'
  if (auth.user?.role === 'teacher') return '查看本人授课课程和本周授课安排。'
  return '维护课程、上课时间、教室、周次和选课开放时间。'
})

function defaultSchedule(): CourseSchedule {
  return {
    weekday: 1,
    start_section: 1,
    end_section: 2,
    start_time: '08:00',
    end_time: '09:35',
    classroom: '',
    weeks: '1-16',
    term: settingForm.term || '2025-2026-2'
  }
}

function sectionSlotFor(section: number) {
  const sectionNumber = Number(section) || 1
  return sectionSlots.find((slot) => sectionNumber <= slot.end) || sectionSlots[sectionSlots.length - 1]
}

function syncScheduleTime(item: CourseSchedule) {
  const slot = sectionSlotFor(item.start_section)
  item.start_section = slot.start
  item.end_section = slot.end
  item.start_time = slot.startTime
  item.end_time = slot.endTime
}

function normalizedSchedule(item: CourseSchedule): CourseSchedule {
  const next = { ...item }
  syncScheduleTime(next)
  return next
}

function scheduleText(item: CourseSchedule) {
  const day = days.find((dayItem) => dayItem.value === item.weekday)?.label || `周${item.weekday}`
  return `${day} ${item.start_section}-${item.end_section}节 / ${item.classroom || '未定'} / ${item.weeks}周`
}

async function loadTeachers() {
  if (auth.user?.role === 'admin') {
    teachers.value = await getTeachers()
  }
}

async function loadSetting() {
  const setting = await getEnrollmentSetting()
  Object.assign(settingForm, {
    ...setting,
    start_time: toDatetimeLocal(setting.start_time),
    end_time: toDatetimeLocal(setting.end_time)
  })
  currentWeek.value = setting.current_week
}

async function saveEnrollmentSetting() {
  await updateEnrollmentSetting({ ...settingForm })
  await loadSetting()
  await refreshAll()
}

async function loadData() {
  loading.value = true
  try {
    courses.value = await getCourses({
      keyword: keyword.value || undefined,
      only_mine: auth.user?.role === 'teacher'
    })
  } finally {
    loading.value = false
  }
}

async function loadSchedule() {
  scheduleEntries.value = await getWeeklySchedule({ week: currentWeek.value })
}

async function refreshAll() {
  await loadData()
  await loadSchedule()
}

function openCreate() {
  editingCourse.value = null
  Object.assign(courseForm, { name: '', description: '', teacher_id: teachers.value[0]?.id || 0, credit: 3, capacity: 60, schedules: [defaultSchedule()] })
  courseDialog.value = true
}

function openEdit(row: Course) {
  editingCourse.value = row
  Object.assign(courseForm, {
    name: row.name,
    description: row.description,
    teacher_id: row.teacher_id,
    credit: row.credit,
    capacity: row.capacity,
    schedules: row.schedules.length ? row.schedules.map((item) => normalizedSchedule(item)) : [defaultSchedule()]
  })
  courseDialog.value = true
}

function addSchedule() {
  courseForm.schedules.push(defaultSchedule())
}

function removeSchedule(index: number) {
  courseForm.schedules.splice(index, 1)
}

function buildCoursePayload(): CoursePayload {
  return {
    ...courseForm,
    schedules: courseForm.schedules.map((item) => {
      const normalized = normalizedSchedule(item)
      return {
        weekday: normalized.weekday,
        start_section: normalized.start_section,
        end_section: normalized.end_section,
        start_time: normalized.start_time,
        end_time: normalized.end_time,
        classroom: normalized.classroom,
        weeks: normalized.weeks,
        term: settingForm.term
      }
    })
  }
}

async function saveCourse() {
  if (!courseForm.name || !courseForm.teacher_id) {
    ElMessage.warning('请填写课程名称并选择授课教师')
    return
  }
  const payload = buildCoursePayload()
  if (editingCourse.value) {
    await updateCourse(editingCourse.value.id, payload)
  } else {
    await createCourse(payload)
  }
  courseDialog.value = false
  await loadSetting()
  await refreshAll()
}

async function handleDelete(row: Course) {
  await ElMessageBox.confirm(`确认删除课程「${row.name}」？`, '删除确认', { type: 'warning' })
  await deleteCourse(row.id)
  await refreshAll()
}

async function handleEnroll(id: number) {
  await enrollCourse(id)
  await refreshAll()
}

async function openStudents(row: Course) {
  activeCourse.value = row
  students.value = await getCourseStudents(row.id)
  studentDialog.value = true
}

async function handleAdminDrop(studentId: number) {
  if (!activeCourse.value) return
  await ElMessageBox.confirm('确认由管理员为该学生退课？', '退课确认', { type: 'warning' })
  await adminRemoveEnrollment(activeCourse.value.id, studentId)
  students.value = await getCourseStudents(activeCourse.value.id)
  await refreshAll()
}

async function changeWeek(offset: number) {
  currentWeek.value = Math.max(1, currentWeek.value + offset)
  await loadSchedule()
}

async function resetWeek() {
  currentWeek.value = settingForm.current_week || 12
  await loadSchedule()
}

onMounted(async () => {
  await loadTeachers()
  await loadSetting()
  await refreshAll()
})
</script>
