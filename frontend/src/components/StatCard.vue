<template>
  <el-card>
    <div class="label">{{ label }}</div>
    <div class="value">{{ value }}</div>
  </el-card>
</template>

<script setup lang="ts">
defineProps<{ label: string; value: number | string }>()
</script>

<style scoped>
.label {
  color: #64748b;
  font-size: 13px;
}
.value {
  margin-top: 8px;
  font-size: 28px;
  font-weight: 700;
}
</style>
