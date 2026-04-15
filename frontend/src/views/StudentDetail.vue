<template>
  <div>
    <el-page-header @back="router.push('/students')" content="学员详情" />
    <h2 class="page-title">{{ student?.name || '学员详情' }}</h2>

    <el-card class="page-card">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="基础信息" name="base">
          <el-form :model="studentForm" label-width="120px" style="max-width: 900px">
            <el-row :gutter="12">
              <el-col :span="12"><el-form-item label="姓名"><el-input v-model="studentForm.name" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="微信"><el-input v-model="studentForm.wechat" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="手机号"><el-input v-model="studentForm.phone" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="课程"><el-input v-model="studentForm.course_name" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="班级"><el-input v-model="studentForm.class_name" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="当前方向"><el-input v-model="studentForm.current_direction" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="生命周期阶段"><el-select v-model="studentForm.current_stage" style="width: 100%"><el-option v-for="s in stageOptions" :key="s" :label="s" :value="s" /></el-select></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="意向等级"><el-select v-model="studentForm.intent_level" style="width: 100%"><el-option v-for="s in intentOptions" :key="s" :label="s" :value="s" /></el-select></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="下次跟进时间"><el-date-picker v-model="studentForm.next_follow_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%" /></el-form-item></el-col>
            </el-row>
            <el-form-item label="备注"><el-input v-model="studentForm.remark" type="textarea" /></el-form-item>
            <el-space>
              <el-button type="primary" @click="saveStudent">保存基础信息</el-button>
              <el-button @click="changeStage">修改生命周期阶段</el-button>
            </el-space>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="用户画像" name="profile">
          <el-form :model="profileForm" label-width="120px" style="max-width: 900px">
            <el-form-item label="画像摘要"><el-input v-model="profileForm.summary" type="textarea" /></el-form-item>
            <el-form-item label="用户类型"><el-input v-model="profileForm.user_type" /></el-form-item>
            <el-form-item label="主要目标"><el-input v-model="profileForm.main_goal" /></el-form-item>
            <el-form-item label="核心顾虑"><el-input v-model="profileForm.main_concerns" /></el-form-item>
            <el-form-item label="兴趣方向"><el-input v-model="profileForm.interest_direction" /></el-form-item>
            <el-form-item label="推荐动作"><el-input v-model="profileForm.recommended_action" /></el-form-item>
            <el-button type="primary" @click="saveProfileInfo">保存画像</el-button>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="聊天记录" name="chat">
          <el-form inline>
            <el-form-item label="来源"><el-input v-model="chatForm.source" placeholder="如：企业微信/手工粘贴" /></el-form-item>
          </el-form>
          <el-input v-model="chatForm.content" type="textarea" :rows="6" placeholder="粘贴聊天记录后点击保存" />
          <div style="margin: 12px 0">
            <el-button type="primary" @click="saveChat">保存聊天记录</el-button>
          </div>
          <el-table :data="chatRecords" size="small">
            <el-table-column prop="created_at" label="时间" width="180" />
            <el-table-column prop="source" label="来源" width="120" />
            <el-table-column prop="content" label="内容" show-overflow-tooltip />
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button link type="danger" @click="removeChat(row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="AI分析结果" name="analysis">
          <el-form inline>
            <el-form-item label="选择聊天记录">
              <el-select v-model="selectedChatId" style="width: 300px" clearable>
                <el-option v-for="item in chatRecords" :key="item.id" :label="`${item.id} - ${item.content.slice(0, 20)}`" :value="item.id" />
              </el-select>
            </el-form-item>
            <el-button type="primary" @click="runAnalysis">点击分析</el-button>
          </el-form>

          <el-table :data="analyses" style="margin-top: 12px">
            <el-table-column prop="created_at" label="分析时间" width="180" />
            <el-table-column prop="stage" label="阶段建议" width="100" />
            <el-table-column prop="main_need" label="主要需求" min-width="150" />
            <el-table-column prop="core_concerns" label="核心顾虑" min-width="150" />
            <el-table-column prop="recommended_action" label="推荐动作" min-width="160" />
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button link @click="saveAnalysis(row)">保存分析结果</el-button>
                <el-button link type="primary" @click="syncToProfile(row)">一键同步到画像</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="跟进记录" name="followup">
          <el-form :model="followForm" label-width="110px" style="max-width: 900px">
            <el-row :gutter="12">
              <el-col :span="12"><el-form-item label="跟进时间"><el-date-picker v-model="followForm.follow_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="跟进方式"><el-input v-model="followForm.follow_method" /></el-form-item></el-col>
            </el-row>
            <el-form-item label="跟进内容"><el-input v-model="followForm.content" type="textarea" /></el-form-item>
            <el-form-item label="学员反馈"><el-input v-model="followForm.student_feedback" /></el-form-item>
            <el-form-item label="下一步动作"><el-input v-model="followForm.next_action" /></el-form-item>
            <el-form-item label="下次跟进时间"><el-date-picker v-model="followForm.next_follow_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%" /></el-form-item>
            <el-button type="primary" @click="saveFollowup">新增跟进记录</el-button>
          </el-form>

          <el-table :data="followups" style="margin-top: 12px" size="small">
            <el-table-column prop="follow_time" label="跟进时间" width="180" />
            <el-table-column prop="follow_method" label="方式" width="100" />
            <el-table-column prop="content" label="内容" min-width="160" />
            <el-table-column prop="student_feedback" label="反馈" min-width="120" />
            <el-table-column prop="next_action" label="下一步动作" min-width="130" />
            <el-table-column prop="next_follow_time" label="下次跟进" width="180" />
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { getStudent, updateStudent, updateStudentStage } from '@/api/students'
import { getProfile, saveProfile } from '@/api/profiles'
import { createChatRecord, deleteChatRecord, getChatRecords } from '@/api/chat'
import { getAIAnalyses, syncAnalysisToProfile, triggerAIAnalysis } from '@/api/ai'
import { createFollowup, getFollowups } from '@/api/followups'
import { intentOptions, stageOptions } from '@/stores/app'
import type { AIAnalysis, ChatRecord, FollowUp, Profile, Student } from '@/types'

const route = useRoute()
const router = useRouter()
const studentId = Number(route.params.id)

const activeTab = ref('base')
const student = ref<Student | null>(null)
const studentForm = reactive<any>({})
const profileForm = reactive<Partial<Profile>>({})
const chatForm = reactive({ content: '', source: '手工粘贴' })
const followForm = reactive<any>({
  follow_time: new Date().toISOString().slice(0, 19),
  follow_method: '微信',
  content: '',
  student_feedback: '',
  judgment: '',
  next_action: '',
  next_follow_time: ''
})

const chatRecords = ref<ChatRecord[]>([])
const analyses = ref<AIAnalysis[]>([])
const followups = ref<FollowUp[]>([])
const selectedChatId = ref<number | null>(null)

const loadAll = async () => {
  const s = await getStudent(studentId)
  student.value = s
  Object.assign(studentForm, s)

  const p = await getProfile(studentId)
  if (p) Object.assign(profileForm, p)

  chatRecords.value = await getChatRecords(studentId)
  analyses.value = await getAIAnalyses(studentId)
  followups.value = await getFollowups(studentId)
}

onMounted(loadAll)

const saveStudent = async () => {
  await updateStudent(studentId, studentForm)
  ElMessage.success('基础信息已保存')
  await loadAll()
}

const changeStage = async () => {
  await updateStudentStage(studentId, studentForm.current_stage, '前端手工调整')
  ElMessage.success('生命周期阶段已更新')
}

const saveProfileInfo = async () => {
  await saveProfile(studentId, profileForm)
  ElMessage.success('画像保存成功')
}

const saveChat = async () => {
  if (!chatForm.content.trim()) return ElMessage.warning('请输入聊天内容')
  await createChatRecord({ student_id: studentId, content: chatForm.content, source: chatForm.source })
  chatForm.content = ''
  ElMessage.success('聊天记录已保存')
  chatRecords.value = await getChatRecords(studentId)
}

const removeChat = async (id: number) => {
  await deleteChatRecord(id)
  ElMessage.success('删除成功')
  chatRecords.value = await getChatRecords(studentId)
}

const runAnalysis = async () => {
  // 当前后端按学员分析最近聊天记录，预留选中聊天记录UI
  if (selectedChatId.value) {
    ElMessage.info('已选择聊天记录，当前版本由后端分析最近一条记录。')
  }
  await triggerAIAnalysis(studentId, { chat_record_id: selectedChatId.value || undefined })
  ElMessage.success('已完成 AI 分析')
  analyses.value = await getAIAnalyses(studentId)
}

const saveAnalysis = (_row: AIAnalysis) => {
  ElMessage.success('分析结果已保存（已落库）')
}

const syncToProfile = async (row: AIAnalysis) => {
  await syncAnalysisToProfile(row.id)
  Object.assign(profileForm, {
    summary: row.summary,
    main_goal: row.main_need,
    main_concerns: row.core_concerns,
    interest_direction: row.interest_direction,
    recommended_action: row.recommended_action,
    recommended_course: row.recommended_course,
    risk_tags: row.risk_points
  })
  ElMessage.success('已同步到画像')
}

const saveFollowup = async () => {
  if (!followForm.content) return ElMessage.warning('请填写跟进内容')
  await createFollowup({ student_id: studentId, ...followForm })
  ElMessage.success('跟进记录已新增')
  followups.value = await getFollowups(studentId)
}
</script>
