<template>
  <div>
    <h2 class="page-title">首页看板</h2>

    <el-row :gutter="16" class="mb16">
      <el-col :span="4" v-for="card in cards" :key="card.label">
        <StatCard :label="card.label" :value="card.value" />
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="12">
        <el-card>
          <template #header>最近跟进学员</template>
          <el-table :data="summary.recent_followed_students" size="small">
            <el-table-column prop="name" label="学员" />
            <el-table-column prop="current_stage" label="阶段" width="100" />
            <el-table-column prop="owner" label="负责人" width="100" />
            <el-table-column prop="last_interaction_at" label="最近互动" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>待跟进学员</template>
          <el-table :data="summary.pending_follow_students" size="small">
            <el-table-column prop="name" label="学员" />
            <el-table-column prop="current_stage" label="阶段" width="100" />
            <el-table-column prop="intent_level" label="意向" width="80" />
            <el-table-column prop="next_follow_time" label="下次跟进" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive } from 'vue'
import { getDashboardSummary, type DashboardSummary } from '@/api/dashboard'
import StatCard from '@/components/StatCard.vue'

const summary = reactive<DashboardSummary>({
  total_students: 0,
  high_intent_count: 0,
  pending_follow_count: 0,
  closed_deals_count: 0,
  weekly_new_followups: 0,
  recent_followed_students: [],
  pending_follow_students: []
})

const cards = computed(() => [
  { label: '学员总数', value: summary.total_students },
  { label: '高意向人数', value: summary.high_intent_count },
  { label: '待跟进人数', value: summary.pending_follow_count },
  { label: '已成交人数', value: summary.closed_deals_count },
  { label: '本周新增跟进数', value: summary.weekly_new_followups }
])

const load = async () => {
  const data = await getDashboardSummary()
  Object.assign(summary, data)
}

onMounted(load)
</script>

<style scoped>
.mb16 {
  margin-bottom: 16px;
}
</style>
