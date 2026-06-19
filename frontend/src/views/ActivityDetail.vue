<template>
  <div>
    <div class="page-header">
      <div>
        <router-link to="/" class="back-link">← 返回活动列表</router-link>
      </div>
      <div class="header-actions" v-if="activity">
        <router-link
          v-if="activity.status !== 'cancelled'"
          :to="`/activities/${activity.id}/edit`"
          class="btn btn-outline btn-sm"
        >
          ✏️ 编辑
        </router-link>
        <button
          v-if="activity.status !== 'cancelled'"
          class="btn btn-danger btn-sm"
          @click="showCancelActivity = true"
          :disabled="cancelling"
        >
          🚫 {{ cancelling ? '取消中...' : '取消活动' }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <div>加载中...</div>
    </div>

    <div v-else-if="activity">
      <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>
      <div v-if="errorMsg" class="alert alert-error">{{ errorMsg }}</div>

      <div class="card detail-header-card">
        <div class="detail-top">
          <h1 class="detail-title">{{ activity.title }}</h1>
          <span :class="['badge', statusBadgeClass(activity.status)]" style="font-size: 0.875rem;">
            {{ statusLabel(activity.status) }}
          </span>
        </div>

        <div class="detail-meta-grid">
          <div class="detail-meta">
            <div class="meta-icon-lg">📍</div>
            <div>
              <div class="meta-label">活动地点</div>
              <div class="meta-value">{{ activity.location }}</div>
            </div>
          </div>
          <div class="detail-meta">
            <div class="meta-icon-lg">🕐</div>
            <div>
              <div class="meta-label">开始时间</div>
              <div class="meta-value">{{ formatDateTime(activity.start_time) }}</div>
            </div>
          </div>
          <div class="detail-meta">
            <div class="meta-icon-lg">👥</div>
            <div>
              <div class="meta-label">报名情况</div>
              <div class="meta-value">
                <strong style="font-size: 1.25rem; color: var(--primary);">
                  {{ activity.current_participants }}
                </strong>
                / {{ activity.max_participants }} 人
                <span
                  v-if="activity.status === 'open' && activity.remaining_slots > 0"
                  class="meta-sub success"
                >
                  剩余 {{ activity.remaining_slots }} 名
                </span>
                <span
                  v-else-if="activity.status === 'open' && activity.remaining_slots === 0"
                  class="meta-sub danger"
                >
                  已满员
                </span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="activity.description" class="detail-desc">
          <div class="desc-label">活动说明</div>
          <p class="desc-content">{{ activity.description }}</p>
        </div>
      </div>

      <div class="detail-actions-row">
        <button
          v-if="canRegister"
          class="btn btn-success btn-lg action-btn"
          @click="openRegisterModal"
        >
          📝 我要报名
        </button>
        <button
          v-if="canCancelRegistration"
          class="btn btn-outline btn-lg action-btn"
          @click="openCancelModal"
        >
          ❌ 取消报名
        </button>
        <div v-if="activity.status === 'cancelled'" class="status-banner banner-danger">
          此活动已取消，无法报名
        </div>
        <div v-else-if="activity.status === 'closed'" class="status-banner banner-gray">
          此活动已结束
        </div>
        <div v-else-if="activity.status === 'draft'" class="status-banner banner-info">
          此活动为草稿状态，暂未开放报名
        </div>
        <div
          v-else-if="activity.status === 'open' && activity.remaining_slots === 0"
          class="status-banner banner-warning"
        >
          活动名额已满
        </div>
      </div>

      <div class="card">
        <h2 class="section-title">报名名单（{{ activity.current_participants }}人）</h2>
        <div v-if="activeRegistrations.length === 0" class="empty-state" style="padding: 2rem 1rem;">
          <div style="font-size: 36px; margin-bottom: 0.5rem;">📋</div>
          <p>暂无报名记录</p>
        </div>
        <div v-else class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>姓名</th>
                <th>手机号</th>
                <th>备注</th>
                <th>报名时间</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(reg, idx) in activity.registrations" :key="reg.id">
                <td>{{ idx + 1 }}</td>
                <td>{{ reg.name }}</td>
                <td>{{ maskPhone(reg.phone) }}</td>
                <td>{{ reg.remark || '-' }}</td>
                <td>{{ formatDateTime(reg.created_at) }}</td>
                <td>
                  <span
                    :class="[
                      'badge',
                      reg.status === 'active' ? 'badge-success' : 'badge-gray',
                    ]"
                  >
                    {{ reg.status === 'active' ? '已报名' : '已取消' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-if="showRegister" class="modal-overlay" @click.self="showRegister = false">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">活动报名 - {{ activity?.title }}</h3>
          <button class="modal-close" @click="showRegister = false">×</button>
        </div>
        <div class="modal-body">
          <div v-if="registerError" class="alert alert-error">{{ registerError }}</div>

          <div class="form-group">
            <label class="form-label">姓名 <span class="required">*</span></label>
            <input
              v-model="regForm.name"
              type="text"
              class="form-control"
              :class="{ 'has-error': regErrors.name }"
              placeholder="请输入您的姓名"
            />
            <div v-if="regErrors.name" class="form-error">{{ regErrors.name }}</div>
          </div>

          <div class="form-group">
            <label class="form-label">手机号 <span class="required">*</span></label>
            <input
              v-model="regForm.phone"
              type="tel"
              class="form-control"
              :class="{ 'has-error': regErrors.phone }"
              placeholder="请输入11位手机号"
              maxlength="11"
            />
            <div v-if="regErrors.phone" class="form-error">{{ regErrors.phone }}</div>
          </div>

          <div class="form-group">
            <label class="form-label">备注</label>
            <textarea
              v-model="regForm.remark"
              class="form-control"
              rows="3"
              placeholder="选填，如特殊需求等"
              maxlength="500"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showRegister = false">取消</button>
          <button class="btn btn-primary" @click="submitRegistration" :disabled="regSubmitting">
            {{ regSubmitting ? '提交中...' : '确认报名' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="showCancelReg" class="modal-overlay" @click.self="showCancelReg = false">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">取消报名</h3>
          <button class="modal-close" @click="showCancelReg = false">×</button>
        </div>
        <div class="modal-body">
          <div v-if="cancelRegError" class="alert alert-error">{{ cancelRegError }}</div>

          <p style="margin-bottom: 1rem; color: var(--gray-600); font-size: 0.875rem;">
            请输入报名时使用的手机号以取消您的报名：
          </p>

          <div class="form-group">
            <label class="form-label">手机号 <span class="required">*</span></label>
            <input
              v-model="cancelRegForm.phone"
              type="tel"
              class="form-control"
              :class="{ 'has-error': cancelRegErrors.phone }"
              placeholder="请输入11位手机号"
              maxlength="11"
            />
            <div v-if="cancelRegErrors.phone" class="form-error">{{ cancelRegErrors.phone }}</div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showCancelReg = false">取消</button>
          <button
            class="btn btn-danger"
            @click="submitCancelRegistration"
            :disabled="cancelRegSubmitting"
          >
            {{ cancelRegSubmitting ? '处理中...' : '确认取消报名' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="showCancelActivity" class="modal-overlay" @click.self="showCancelActivity = false">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">确认取消活动</h3>
          <button class="modal-close" @click="showCancelActivity = false">×</button>
        </div>
        <div class="modal-body">
          <div class="alert alert-warning">
            取消活动后，用户将无法继续报名此活动。已报名用户的名额记录仍保留。
          </div>
          <p style="margin-top: 1rem; font-size: 0.875rem; color: var(--gray-700);">
            确定要取消活动
            <strong style="color: var(--danger);">"{{ activity?.title }}"</strong>
            吗？
          </p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showCancelActivity = false">再想想</button>
          <button class="btn btn-danger" @click="confirmCancelActivity" :disabled="cancelling">
            {{ cancelling ? '处理中...' : '确认取消' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  getActivity,
  registerActivity,
  cancelRegistration,
  cancelActivity as cancelActivityApi,
} from '@/api'

const route = useRoute()

const loading = ref(false)
const activity = ref(null)
const errorMsg = ref('')
const successMsg = ref('')

const showRegister = ref(false)
const regSubmitting = ref(false)
const registerError = ref('')
const regForm = reactive({ name: '', phone: '', remark: '' })
const regErrors = reactive({ name: '', phone: '' })

const showCancelReg = ref(false)
const cancelRegSubmitting = ref(false)
const cancelRegError = ref('')
const cancelRegForm = reactive({ phone: '' })
const cancelRegErrors = reactive({ phone: '' })

const showCancelActivity = ref(false)
const cancelling = ref(false)

const statusLabel = (status) => {
  const map = { open: '报名中', draft: '草稿', closed: '已结束', cancelled: '已取消' }
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

const maskPhone = (phone) => {
  if (!phone || phone.length < 7) return phone
  return phone.slice(0, 3) + '****' + phone.slice(-4)
}

const canRegister = computed(() => {
  return activity.value?.status === 'open' && activity.value?.remaining_slots > 0
})

const canCancelRegistration = computed(() => {
  return activity.value?.status !== 'cancelled' && activity.value?.current_participants > 0
})

const activeRegistrations = computed(() => {
  return (activity.value?.registrations || []).filter((r) => r.status === 'active')
})

const loadActivity = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    activity.value = await getActivity(route.params.id)
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    loading.value = false
  }
}

const openRegisterModal = () => {
  registerError.value = ''
  Object.keys(regErrors).forEach((k) => (regErrors[k] = ''))
  regForm.name = ''
  regForm.phone = ''
  regForm.remark = ''
  showRegister.value = true
}

const openCancelModal = () => {
  cancelRegError.value = ''
  cancelRegErrors.phone = ''
  cancelRegForm.phone = ''
  showCancelReg.value = true
}

const validatePhone = (phone) => /^1[3-9]\d{9}$/.test(phone)

const submitRegistration = async () => {
  registerError.value = ''
  let ok = true
  regErrors.name = ''
  regErrors.phone = ''

  if (!regForm.name.trim()) {
    regErrors.name = '请输入姓名'
    ok = false
  }
  if (!regForm.phone.trim()) {
    regErrors.phone = '请输入手机号'
    ok = false
  } else if (!validatePhone(regForm.phone.trim())) {
    regErrors.phone = '手机号格式不正确（以1开头的11位数字）'
    ok = false
  }
  if (!ok) return

  regSubmitting.value = true
  try {
    await registerActivity(activity.value.id, {
      name: regForm.name.trim(),
      phone: regForm.phone.trim(),
      remark: regForm.remark.trim() || null,
    })
    showRegister.value = false
    successMsg.value = '🎉 报名成功！'
    setTimeout(() => (successMsg.value = ''), 4000)
    await loadActivity()
  } catch (e) {
    registerError.value = e.message
  } finally {
    regSubmitting.value = false
  }
}

const submitCancelRegistration = async () => {
  cancelRegError.value = ''
  cancelRegErrors.phone = ''

  if (!cancelRegForm.phone.trim()) {
    cancelRegErrors.phone = '请输入手机号'
    return
  }
  if (!validatePhone(cancelRegForm.phone.trim())) {
    cancelRegErrors.phone = '手机号格式不正确'
    return
  }

  cancelRegSubmitting.value = true
  try {
    await cancelRegistration(activity.value.id, {
      phone: cancelRegForm.phone.trim(),
    })
    showCancelReg.value = false
    successMsg.value = '✅ 已取消报名，名额已释放'
    setTimeout(() => (successMsg.value = ''), 4000)
    await loadActivity()
  } catch (e) {
    cancelRegError.value = e.message
  } finally {
    cancelRegSubmitting.value = false
  }
}

const confirmCancelActivity = async () => {
  cancelling.value = true
  errorMsg.value = ''
  try {
    await cancelActivityApi(activity.value.id)
    showCancelActivity.value = false
    successMsg.value = '活动已取消'
    setTimeout(() => (successMsg.value = ''), 4000)
    await loadActivity()
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    cancelling.value = false
  }
}

onMounted(() => loadActivity())
</script>

<style scoped>
.required {
  color: var(--danger);
}

.has-error {
  border-color: var(--danger) !important;
}

.back-link {
  font-size: 0.875rem;
  color: var(--gray-500);
  text-decoration: none;
}

.back-link:hover {
  color: var(--primary);
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.detail-header-card {
  margin-bottom: 1.5rem;
}

.detail-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.detail-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--gray-900);
  margin: 0;
  line-height: 1.3;
  flex: 1;
  min-width: 200px;
}

.detail-meta-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.detail-meta {
  display: flex;
  gap: 0.875rem;
  align-items: flex-start;
  padding: 0.875rem;
  background-color: var(--gray-50);
  border-radius: var(--radius);
}

.meta-icon-lg {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.meta-label {
  font-size: 0.75rem;
  color: var(--gray-500);
  margin-bottom: 0.125rem;
}

.meta-value {
  font-size: 0.9375rem;
  color: var(--gray-800);
  font-weight: 500;
}

.meta-sub {
  font-size: 0.75rem;
  margin-left: 0.5rem;
}

.meta-sub.success {
  color: var(--success);
}

.meta-sub.danger {
  color: var(--danger);
}

.detail-desc {
  padding-top: 1.25rem;
  border-top: 1px solid var(--gray-100);
}

.desc-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--gray-700);
  margin-bottom: 0.5rem;
}

.desc-content {
  font-size: 0.9375rem;
  color: var(--gray-600);
  line-height: 1.75;
  margin: 0;
  white-space: pre-wrap;
}

.detail-actions-row {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  align-items: center;
}

.action-btn {
  min-width: 140px;
}

.status-banner {
  padding: 0.625rem 1rem;
  border-radius: var(--radius);
  font-size: 0.875rem;
  font-weight: 500;
  flex: 1;
}

.banner-danger {
  background-color: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.banner-gray {
  background-color: var(--gray-100);
  color: var(--gray-700);
  border: 1px solid var(--gray-200);
}

.banner-info {
  background-color: #ecfeff;
  color: #155e75;
  border: 1px solid #a5f3fc;
}

.banner-warning {
  background-color: #fffbeb;
  color: #92400e;
  border: 1px solid #fde68a;
}

.section-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--gray-900);
  margin: 0 0 1rem 0;
}

.table-wrapper {
  overflow-x: auto;
  margin: 0 -1.5rem;
  padding: 0 1.5rem;
}

@media (max-width: 768px) {
  .detail-meta-grid {
    grid-template-columns: 1fr;
  }

  .detail-title {
    font-size: 1.25rem;
  }
}
</style>
