<template>
  <section>
    <div class="page-head">
      <div>
        <h2>账号维护</h2>
        <p>维护学生和教师账号基础资料，停用异常账号。</p>
      </div>
      <el-button :icon="Refresh" @click="loadAll">刷新</el-button>
    </div>

    <el-tabs v-model="activeTab" class="panel">
      <el-tab-pane label="学生账号" name="students">
        <div class="toolbar">
          <span></span>
          <el-button type="primary" :icon="Plus" @click="openStudentCreate">新增学生</el-button>
        </div>
        <el-table :data="students">
          <el-table-column prop="username" label="用户名" width="130" />
          <el-table-column prop="real_name" label="姓名" width="120" />
          <el-table-column prop="student_no" label="学号" width="140" />
          <el-table-column prop="major" label="专业" />
          <el-table-column prop="class_name" label="班级" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '停用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180">
            <template #default="{ row }">
              <el-button size="small" :icon="Edit" @click="openStudentEdit(row)">编辑</el-button>
              <el-button size="small" type="danger" :icon="CircleClose" :disabled="!row.is_active" @click="handleDisable(row.user_id)">停用</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="教师账号" name="teachers">
        <div class="toolbar">
          <span></span>
          <el-button type="primary" :icon="Plus" @click="openTeacherCreate">新增教师</el-button>
        </div>
        <el-table :data="teachers">
          <el-table-column prop="username" label="用户名" width="130" />
          <el-table-column prop="real_name" label="姓名" width="120" />
          <el-table-column prop="teacher_no" label="教工号" width="140" />
          <el-table-column prop="title" label="职称" />
          <el-table-column prop="department" label="院系" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '停用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180">
            <template #default="{ row }">
              <el-button size="small" :icon="Edit" @click="openTeacherEdit(row)">编辑</el-button>
              <el-button size="small" type="danger" :icon="CircleClose" :disabled="!row.is_active" @click="handleDisable(row.user_id)">停用</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="studentDialog" :title="editingStudent ? '编辑学生' : '新增学生'" width="560px">
      <el-form label-position="top">
        <div class="form-grid">
          <el-form-item v-if="!editingStudent" label="用户名">
            <el-input v-model="studentForm.username" />
          </el-form-item>
          <el-form-item v-if="!editingStudent" label="初始密码">
            <el-input v-model="studentForm.password" type="password" show-password />
          </el-form-item>
          <el-form-item label="姓名">
            <el-input v-model="studentForm.real_name" />
          </el-form-item>
          <el-form-item label="学号">
            <el-input v-model="studentForm.student_no" />
          </el-form-item>
          <el-form-item label="专业">
            <el-input v-model="studentForm.major" />
          </el-form-item>
          <el-form-item label="班级">
            <el-input v-model="studentForm.class_name" />
          </el-form-item>
        </div>
        <el-form-item v-if="editingStudent" label="账号状态">
          <el-switch v-model="studentForm.is_active" active-text="启用" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="studentDialog = false">取消</el-button>
        <el-button type="primary" @click="saveStudent">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="teacherDialog" :title="editingTeacher ? '编辑教师' : '新增教师'" width="560px">
      <el-form label-position="top">
        <div class="form-grid">
          <el-form-item v-if="!editingTeacher" label="用户名">
            <el-input v-model="teacherForm.username" />
          </el-form-item>
          <el-form-item v-if="!editingTeacher" label="初始密码">
            <el-input v-model="teacherForm.password" type="password" show-password />
          </el-form-item>
          <el-form-item label="姓名">
            <el-input v-model="teacherForm.real_name" />
          </el-form-item>
          <el-form-item label="教工号">
            <el-input v-model="teacherForm.teacher_no" />
          </el-form-item>
          <el-form-item label="职称">
            <el-input v-model="teacherForm.title" />
          </el-form-item>
          <el-form-item label="院系">
            <el-input v-model="teacherForm.department" />
          </el-form-item>
        </div>
        <el-form-item v-if="editingTeacher" label="账号状态">
          <el-switch v-model="teacherForm.is_active" active-text="启用" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="teacherDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTeacher">保存</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { CircleClose, Edit, Plus, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createStudent,
  createTeacher,
  disableUser,
  getStudents,
  getTeachers,
  updateStudent,
  updateTeacher
} from '../../api/users'
import type { StudentAdmin, TeacherAdmin } from '../../api/types'

const activeTab = ref('students')
const students = ref<StudentAdmin[]>([])
const teachers = ref<TeacherAdmin[]>([])
const studentDialog = ref(false)
const teacherDialog = ref(false)
const editingStudent = ref<StudentAdmin | null>(null)
const editingTeacher = ref<TeacherAdmin | null>(null)

const studentForm = reactive({
  username: '',
  password: '123456',
  real_name: '',
  student_no: '',
  major: '',
  class_name: '',
  is_active: true
})

const teacherForm = reactive({
  username: '',
  password: '123456',
  real_name: '',
  teacher_no: '',
  title: '',
  department: '',
  is_active: true
})

async function loadAll() {
  const [studentList, teacherList] = await Promise.all([getStudents(), getTeachers()])
  students.value = studentList
  teachers.value = teacherList
}

function openStudentCreate() {
  editingStudent.value = null
  Object.assign(studentForm, { username: '', password: '123456', real_name: '', student_no: '', major: '', class_name: '', is_active: true })
  studentDialog.value = true
}

function openStudentEdit(row: StudentAdmin) {
  editingStudent.value = row
  Object.assign(studentForm, {
    username: row.username,
    password: '',
    real_name: row.real_name,
    student_no: row.student_no,
    major: row.major || '',
    class_name: row.class_name || '',
    is_active: row.is_active
  })
  studentDialog.value = true
}

async function saveStudent() {
  if (!studentForm.real_name || !studentForm.student_no || (!editingStudent.value && (!studentForm.username || !studentForm.password))) {
    ElMessage.warning('请填写学生账号、姓名和学号')
    return
  }
  if (editingStudent.value) {
    await updateStudent(editingStudent.value.id, {
      real_name: studentForm.real_name,
      student_no: studentForm.student_no,
      major: studentForm.major,
      class_name: studentForm.class_name,
      is_active: studentForm.is_active
    })
  } else {
    await createStudent({ ...studentForm })
  }
  studentDialog.value = false
  await loadAll()
}

function openTeacherCreate() {
  editingTeacher.value = null
  Object.assign(teacherForm, { username: '', password: '123456', real_name: '', teacher_no: '', title: '', department: '', is_active: true })
  teacherDialog.value = true
}

function openTeacherEdit(row: TeacherAdmin) {
  editingTeacher.value = row
  Object.assign(teacherForm, {
    username: row.username,
    password: '',
    real_name: row.real_name,
    teacher_no: row.teacher_no,
    title: row.title || '',
    department: row.department || '',
    is_active: row.is_active
  })
  teacherDialog.value = true
}

async function saveTeacher() {
  if (!teacherForm.real_name || !teacherForm.teacher_no || (!editingTeacher.value && (!teacherForm.username || !teacherForm.password))) {
    ElMessage.warning('请填写教师账号、姓名和教工号')
    return
  }
  if (editingTeacher.value) {
    await updateTeacher(editingTeacher.value.id, {
      real_name: teacherForm.real_name,
      teacher_no: teacherForm.teacher_no,
      title: teacherForm.title,
      department: teacherForm.department,
      is_active: teacherForm.is_active
    })
  } else {
    await createTeacher({ ...teacherForm })
  }
  teacherDialog.value = false
  await loadAll()
}

async function handleDisable(userId: number) {
  await ElMessageBox.confirm('确认停用该账号？', '停用确认', { type: 'warning' })
  await disableUser(userId)
  await loadAll()
}

onMounted(loadAll)
</script>

