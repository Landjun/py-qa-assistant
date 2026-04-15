import { defineStore } from 'pinia'

export const stageOptions = ['刚结课', '已激活', '已联系', '有兴趣', '明确需求', '高意向', '已成交', '沉默', '流失']
export const intentOptions = ['高', '中', '低']
export const directionOptions = ['内容增长', '私域运营', '转化成交', '就业提升', '其他']

export const useAppStore = defineStore('app', {
  state: () => ({
    collapsed: false
  }),
  actions: {
    toggleCollapsed() {
      this.collapsed = !this.collapsed
    }
  }
})
