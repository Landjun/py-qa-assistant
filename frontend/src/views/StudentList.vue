<template>
  <div>
    <h2 class="page-title">学员中心</h2>

    <el-card class="page-card">
      <el-row :gutter="12" class="toolbar">
        <el-col :span="6">
          <el-input v-model="filters.keyword" placeholder="搜索姓名/微信/手机号" clearable />
        </el-col>
        <el-col :span="4">
          <el-select v-model="filters.stage" placeholder="按阶段筛选" clearable style="width: 100%">
            <el-option v-for="item in stageOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filters.intent" placeholder="按意向筛选" clearable style="width: 100%">
            <el-option v-for="item in intentOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filters.direction" placeholder="按方向筛选" clearable style="width: 100%">
            <el-option v-for="item in directionOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-col>
        <el-col :span="6" style="text-align: right">
          <el-button type="primary" @click="openCreate">新增学员</el-button>
        </el-col>
      </el-row>

      <el-table :data="filteredStudents" @row-dblclick="goDetail" style="width: 100%">
        <el-table-column prop="name" label="姓名" min-width="100" />
        <el-table-column prop="wechat" label="微信" min-width="120" />
        <el-table-column prop="phone" label="手机号" min-width="120" />
        <el-table-column prop="course_name" label="课程" min-width="140" />
        <el-table-column prop="current_stage" label="阶段" width="100" />
        <el-table-column prop="intent_level" label="意向" width="80" />
        <el-table-column prop="current_direction" label="方向" min-width="120" />
        <el-table-column prop="owner" label="负责人" width="100" />
        <el-table-column label="操作" width="170">
          <template #default="{ row }">
            <el-button link type="primary" @click="goDetail(row)">详情</el-button>
            <el-button link @click="openEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? '新增学员' : '编辑学员'" width="720px">
      <el-form :model="form" label-width="120px">
        <el-row :gutter="12">
          <el-col :span="12"><el-form-item label="姓名"><el-input v-model="form.name" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="微信"><el-input v-model="form.wechat" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="手机号"><el-input v-model="form.phone" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="课程名"><el-input v-model="form.course_name" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="班级"><el-input v-model="form.class_name" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="毕业日期"><el-date-picker v-model="form.graduation_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="当前方向"><el-input v-model="form.current_direction" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="当前阶段"><el-select v-model="form.current_stage" style="width: 100%"><el-option v-for="s in stageOptions" :key="s" :label="s" :value="s" /></el-select></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="意向等级"><el-select v-model="form.intent_level" style="width: 100%"><el-option v-for="s in intentOptions" :key="s" :label="s" :value="s" /></el-select></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="负责人"><el-input v-model="form.owner" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { createStudent, getStudents, updateStudent } from '@/api/students'
import { directionOptions, intentOptions, stageOptions } from '@/stores/app'
import type { Student } from '@/types'

const router = useRouter()
const students = ref<Student[]>([])

const filters = reactive({ keyword: '', stage: '', intent: '', direction: '' })

const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const editingId = ref<number | null>(null)
const form = reactive<any>({
  name: '',
  wechat: '',
  phone: '',
  course_name: '',
  class_name: '',
  graduation_date: '',
  current_direction: '',
  current_stage: '刚结课',
  intent_level: '中',
  owner: '',
  remark: ''
})

const load = async () => {
  students.value = await getStudents()
}

onMounted(load)

const filteredStudents = computed(() =>
  students.value.filter((s) => {
    const keyword = filters.keyword.trim()
    const inKeyword =
      !keyword ||
      [s.name, s.wechat, s.phone].filter(Boolean).join('|').toLowerCase().includes(keyword.toLowerCase())
    return (
      inKeyword &&
      (!filters.stage || s.current_stage === filters.stage) &&
      (!filters.intent || s.intent_level === filters.intent) &&
      (!filters.direction || s.current_direction === filters.direction)
    )
  })
)

const resetForm = () => {
  Object.assign(form, {
    name: '', wechat: '', phone: '', course_name: '', class_name: '', graduation_date: '', current_direction: '',
    current_stage: '刚结课', intent_level: '中', owner: '', remark: ''
  })
}

const openCreate = () => {
  dialogMode.value = 'create'
  editingId.value = null
  resetForm()
  dialogVisible.value = true
}

const openEdit = (row: Student) => {
  dialogMode.value = 'edit'
  editingId.value = row.id
  Object.assign(form, row)
  dialogVisible.value = true
}

const submitForm = async () => {
  if (!form.name) return ElMessage.warning('请填写姓名')
  if (dialogMode.value === 'create') {
    await createStudent(form)
    ElMessage.success('新增成功')
  } else if (editingId.value) {
    await updateStudent(editingId.value, form)
    ElMessage.success('更新成功')
  }
  dialogVisible.value = false
  await load()
}

const goDetail = (row: Student) => {
  router.push(`/students/${row.id}`)
}
</script>

<style scoped>
.toolbar {
  margin-bottom: 12px;
}
</style>
