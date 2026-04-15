<template>
  <div>
    <h2 class="page-title">AI分析</h2>
    <el-card class="page-card">
      <el-row :gutter="12" class="mb12">
        <el-col :span="6">
          <el-select v-model="selectedStudentId" placeholder="请选择学员" style="width: 100%" @change="onStudentChange">
            <el-option v-for="item in students" :key="item.id" :label="`${item.name}（${item.current_stage}）`" :value="item.id" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-select v-model="selectedChatId" placeholder="请选择聊天记录" style="width: 100%" :disabled="!selectedStudentId">
            <el-option
              v-for="item in chatRecords"
              :key="item.id"
              :label="`${item.id} - ${item.content.slice(0, 24)}`"
              :value="item.id"
            />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" :disabled="!selectedStudentId" @click="runAI">发起AI分析</el-button>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-card>
            <template #header>该学员聊天记录</template>
            <el-table :data="chatRecords" size="small" max-height="420">
              <el-table-column prop="created_at" label="时间" width="160" />
              <el-table-column prop="source" label="来源" width="100" />
              <el-table-column prop="content" label="内容" show-overflow-tooltip />
            </el-table>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header>结构化分析结果</template>
            <el-table :data="analyses" size="small" max-height="420">
              <el-table-column prop="created_at" label="时间" width="160" />
              <el-table-column prop="stage" label="阶段" width="90" />
              <el-table-column prop="main_need" label="主要需求" />
              <el-table-column prop="core_concerns" label="核心顾虑" />
              <el-table-column label="标签" width="140">
                <template #default="{ row }">
                  <el-tag v-for="tag in row.tags || []" :key="tag" size="small" style="margin-right: 4px">{{ tag }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="140">
                <template #default="{ row }">
                  <el-button link @click="saveAnalysis">保存</el-button>
                  <el-button link type="primary" @click="syncProfile(row.id)">同步画像</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getStudents } from '@/api/students'
import { getChatRecords } from '@/api/chat'
import { getAIAnalyses, syncAnalysisToProfile, triggerAIAnalysis } from '@/api/ai'
import type { AIAnalysis, ChatRecord, Student } from '@/types'

const students = ref<Student[]>([])
const selectedStudentId = ref<number>()
const selectedChatId = ref<number>()
const chatRecords = ref<ChatRecord[]>([])
const analyses = ref<AIAnalysis[]>([])

const loadStudents = async () => {
  students.value = await getStudents()
}

onMounted(loadStudents)

const onStudentChange = async (id: number) => {
  selectedChatId.value = undefined
  chatRecords.value = await getChatRecords(id)
  analyses.value = await getAIAnalyses(id)
}

const runAI = async () => {
  if (!selectedStudentId.value) return
  await triggerAIAnalysis(selectedStudentId.value, {
    chat_record_id: selectedChatId.value
  })
  analyses.value = await getAIAnalyses(selectedStudentId.value)
  ElMessage.success('AI分析完成')
}

const saveAnalysis = () => ElMessage.success('分析结果已保存（后端已落库）')

const syncProfile = async (analysisId: number) => {
  await syncAnalysisToProfile(analysisId)
  ElMessage.success('已同步到画像')
}
</script>

<style scoped>
.mb12 {
  margin-bottom: 12px;
}
</style>
