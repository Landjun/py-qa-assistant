<template>
  <el-container class="layout-container">
    <el-aside width="220px" class="sidebar">
      <div class="logo">教学运营售后 CRM</div>
      <el-menu router :default-active="$route.path" class="menu">
        <el-menu-item index="/dashboard">首页看板</el-menu-item>
        <el-menu-item index="/students">学员中心</el-menu-item>
        <el-menu-item index="/ai-analysis">AI分析</el-menu-item>
        <el-menu-item index="/assets">资产库</el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div>欢迎你，{{ auth.username || '运营同学' }}</div>
        <el-button link type="danger" @click="onLogout">退出登录</el-button>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

const onLogout = () => {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
}
.sidebar {
  border-right: 1px solid #e5e7eb;
  background: #fff;
}
.logo {
  padding: 16px;
  font-weight: 700;
  border-bottom: 1px solid #eef0f3;
}
.menu {
  border-right: none;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eef0f3;
  background: #fff;
}
.main-content {
  background: #f5f7fa;
}
</style>
