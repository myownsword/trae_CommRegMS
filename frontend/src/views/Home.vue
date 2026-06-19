<template>
  <div>
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon stat-icon-blue">📊</div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.total_activities }}</div>
          <div class="stat-label">总活动数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-icon-green">✅</div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.open_activities }}</div>
          <div class="stat-label">可报名活动</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-icon-orange">👥</div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.total_registrations }}</div>
          <div class="stat-label">总报名人数</div>
        </div>
      </div>
    </div>

    <div class="card filters-card">
      <div class="filter-row">
        <div class="filter-label">状态筛选：</div>
        <div class="filter-buttons">
          <button
            v-for="f in filters"
            :key="f.value"
            class="filter-btn"
            :class="{ active: currentFilter === f.value }"
            @click="currentFilter = f.value"
          >
            {{ f.label }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <div>加载中...</div>
    </div>

    <div v-else-if="activities.length === 0" class="empty-state">
      <div style="font-size: 48px; margin-bottom: 1rem;">📭</div>
      <p>暂无活动数据</p>
      <router-link to="/activities/new" class="btn btn-primary" style="margin-top: 1rem;">
        + 发布第一个活动
      </router-link>
    </div>

    <div v-else class="activity-grid">
      <router-link
        v-for="activity in activities"
        :key="activity.id"
        :to="`/activities/${activity.id}`"
        class="activity-card"
      >
        <div class="activity-header">
          <h3 class="activity-title">{{ activity.title }}</h3>
          <span :class="['badge', statusBadgeClass(activity.status)]">
            {{ statusLabel(activity.status) }}
          </span>
        </div>

        <div class="activity-meta">
          <div class="meta-item">
            <span class="meta-icon">📍</span>
            <span class="meta-text">{{ activity.location }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-icon">🕐</span>
            <span class="meta-text">{{ formatDateTime(activity.start_time) }}</span>
          </div>
        </div>

        <p v-if="activity.description" class="activity-desc">
          {{ truncateText(activity.description, 80) }}
        </p>

        <div class="activity-footer">
          <div class="progress-section">
            <div class="progress-bar">
              <div
                class="progress-fill"
                :class="progressClass(activity)"
                :style="{ width: progressPercent(activity) + '%' }"
              ></div>
            </div>
            <div class="progress-text">
              <span class="progress-current">{{ activity.current_participants }}</span>
              <span class="progress-sep">/</span>
              <span class="progress-max">{{ activity.max_participants }}</span>
              <span class="progress-label">人已报名</span>
              <span
                v-if="activity.remaining_slots > 0 && activity.status === 'open'"
                class="remaining"
              >
                剩 {{ activity.remaining_slots }} 名
              </span>
              <span
                v-else-if="activity.remaining_slots === 0 && activity.status === 'open'"
                class="remaining full"
              >
                已满员
              </span>
            </div>
          </div>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { getStatistics, getActivities } from '@/api'

const statistics = ref({
  total_activities: 0,
  open_activities: 0,
  total_registrations: 0,
})

const activities = ref([])
const loading = ref(false)
const currentFilter = ref('')

const filters = [
  { label: '全部', value: '' },
  { label: '报名中', value: 'open' },
  { label: '草稿', value: 'draft' },
  { label: '已结束', value: 'closed' },
  { label: '已取消', value: 'cancelled' },
]

const statusLabel = (status) => {
  const map = {
    open: '报名中',
    draft: '草稿',
    closed: '已结束',
    cancelled: '已取消',
  }
  return map[status] || status
}

const statusBadgeClass = (status) => {
  const map = {
    open: 'badge-success',
    draft: 'badge-info',
    closed: 'badge-gray',
    cancelled: 'badge-danger',
  }
  return map[status] || 'badge-gray'
}

const formatDateTime = (dt) => {
  if (!dt) return ''
  const d = new Date(dt)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

const truncateText = (text, max) => {
  if (!text) return ''
  return text.length > max ? text.slice(0, max) + '...' : text
}

const progressPercent = (a) => {
  if (!a.max_participants) return 0
  return Math.min(100, (a.current_participants / a.max_participants) * 100)
}

const progressClass = (a) => {
  const p = progressPercent(a)
  if (p >= 100) return 'progress-danger'
  if (p >= 80) return 'progress-warning'
  return 'progress-success'
}

const fetchAll = async () => {
  loading.value = true
  try {
    const [stats, acts] = await Promise.all([
      getStatistics(),
      getActivities(currentFilter.value ? { status: currentFilter.value } : {}),
    ])
    statistics.value = stats
    activities.value = acts
  } catch (e) {
    alert(e.message)
  } finally {
    loading.value = false
  }
}

watch(currentFilter, () => fetchAll())

onMounted(() => fetchAll())
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.75rem;
  flex-shrink: 0;
}

.stat-icon-blue {
  background-color: #dbeafe;
}

.stat-icon-green {
  background-color: #d1fae5;
}

.stat-icon-orange {
  background-color: #fed7aa;
}

.stat-value {
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--gray-900);
  line-height: 1.2;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--gray-500);
  margin-top: 0.125rem;
}

.filters-card {
  margin-bottom: 1.5rem;
}

.filter-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.filter-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--gray-700);
}

.filter-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.filter-btn {
  padding: 0.375rem 1rem;
  font-size: 0.8125rem;
  border: 1px solid var(--gray-200);
  background: white;
  color: var(--gray-600);
  border-radius: 9999px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.filter-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.filter-btn.active {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
}

.activity-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1rem;
}

.activity-card {
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: 1.5rem;
  text-decoration: none;
  color: inherit;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
}

.activity-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
}

.activity-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--gray-900);
  line-height: 1.4;
  margin: 0;
  flex: 1;
}

.activity-meta {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  color: var(--gray-500);
}

.meta-icon {
  font-size: 0.875rem;
}

.activity-desc {
  font-size: 0.8125rem;
  color: var(--gray-600);
  line-height: 1.6;
  margin: 0;
}

.activity-footer {
  margin-top: auto;
}

.progress-section {
  width: 100%;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background-color: var(--gray-100);
  border-radius: 9999px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.3s ease;
}

.progress-success {
  background-color: var(--success);
}

.progress-warning {
  background-color: var(--warning);
}

.progress-danger {
  background-color: var(--danger);
}

.progress-text {
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: var(--gray-500);
}

.progress-current {
  font-size: 1rem;
  font-weight: 700;
  color: var(--gray-900);
}

.progress-max {
  font-weight: 500;
  color: var(--gray-600);
}

.progress-label {
  margin-left: 0.25rem;
}

.remaining {
  margin-left: auto;
  color: var(--success);
  font-weight: 500;
}

.remaining.full {
  color: var(--danger);
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .activity-grid {
    grid-template-columns: 1fr;
  }
}
</style>
