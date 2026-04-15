<template>
  <div>
    <h2 class="page-title">资产库</h2>
    <el-card class="page-card">
      <el-row :gutter="12" class="toolbar">
        <el-col :span="6"><el-input v-model="keyword" placeholder="搜索标题/内容" clearable /></el-col>
        <el-col :span="4">
          <el-select v-model="typeFilter" placeholder="资产类型" clearable style="width: 100%">
            <el-option label="话术" value="话术" />
            <el-option label="物料" value="物料" />
            <el-option label="SOP动作" value="SOP动作" />
          </el-select>
        </el-col>
        <el-col :span="4"><el-input v-model="stageFilter" placeholder="阶段筛选" clearable /></el-col>
        <el-col :span="10" style="text-align: right"><el-button type="primary" @click="openCreate">新增资产</el-button></el-col>
      </el-row>

      <el-table :data="filteredAssets">
        <el-table-column prop="asset_type" label="类型" width="100" />
        <el-table-column prop="title" label="标题" min-width="160" />
        <el-table-column prop="scene" label="场景" width="120" />
        <el-table-column prop="stage" label="阶段" width="100" />
        <el-table-column prop="direction" label="方向" width="120" />
        <el-table-column prop="content" label="内容" show-overflow-tooltip />
        <el-table-column label="操作" width="240">
          <template #default="{ row }">
            <el-button link @click="copyContent(row.content || '')">一键复制内容</el-button>
            <el-button link @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="removeAsset(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑资产' : '新增资产'" width="700px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="资产类型">
          <el-select v-model="form.asset_type" style="width: 100%">
            <el-option label="话术" value="话术" />
            <el-option label="物料" value="物料" />
            <el-option label="SOP动作" value="SOP动作" />
          </el-select>
        </el-form-item>
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="场景"><el-input v-model="form.scene" /></el-form-item>
        <el-form-item label="阶段"><el-input v-model="form.stage" /></el-form-item>
        <el-form-item label="方向"><el-input v-model="form.direction" /></el-form-item>
        <el-form-item label="内容"><el-input v-model="form.content" type="textarea" :rows="4" /></el-form-item>
        <el-form-item label="链接"><el-input v-model="form.link" /></el-form-item>
        <el-form-item label="说明"><el-input v-model="form.description" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveAsset">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { createAsset, deleteAsset, getAssets, updateAsset } from '@/api/assets'
import type { Asset } from '@/types'

const assets = ref<Asset[]>([])
const keyword = ref('')
const typeFilter = ref('')
const stageFilter = ref('')

const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref<number | null>(null)
const form = reactive<any>({ asset_type: '话术', title: '', scene: '', stage: '', direction: '', content: '', link: '', description: '' })

const load = async () => {
  assets.value = await getAssets()
}
onMounted(load)

const filteredAssets = computed(() =>
  assets.value.filter((a) => {
    const k = keyword.value.trim().toLowerCase()
    const hit = !k || `${a.title}${a.content || ''}`.toLowerCase().includes(k)
    return hit && (!typeFilter.value || a.asset_type === typeFilter.value) && (!stageFilter.value || a.stage?.includes(stageFilter.value))
  })
)

const resetForm = () => Object.assign(form, { asset_type: '话术', title: '', scene: '', stage: '', direction: '', content: '', link: '', description: '' })
const openCreate = () => {
  isEdit.value = false
  editingId.value = null
  resetForm()
  dialogVisible.value = true
}
const openEdit = (row: Asset) => {
  isEdit.value = true
  editingId.value = row.id
  Object.assign(form, row)
  dialogVisible.value = true
}

const saveAsset = async () => {
  if (!form.title) return ElMessage.warning('请填写标题')
  if (isEdit.value && editingId.value) {
    await updateAsset(editingId.value, form)
    ElMessage.success('更新成功')
  } else {
    await createAsset(form)
    ElMessage.success('新增成功')
  }
  dialogVisible.value = false
  await load()
}

const removeAsset = async (id: number) => {
  await deleteAsset(id)
  ElMessage.success('删除成功')
  await load()
}

const copyContent = async (content: string) => {
  await navigator.clipboard.writeText(content)
  ElMessage.success('已复制到剪贴板')
}
</script>

<style scoped>
.toolbar {
  margin-bottom: 12px;
}
</style>
