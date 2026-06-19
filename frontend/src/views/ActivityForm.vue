<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">{{ isEdit ? '编辑活动' : '发布新活动' }}</h1>
      <router-link to="/" class="btn btn-secondary btn-sm">← 返回列表</router-link>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <div>加载中...</div>
    </div>

    <div v-else class="card">
      <div v-if="errorMsg" class="alert alert-error">{{ errorMsg }}</div>

      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label class="form-label">活动标题 <span class="required">*</span></label>
          <input
            v-model="form.title"
            type="text"
            class="form-control"
            :class="{ 'has-error': errors.title }"
            placeholder="请输入活动标题"
            maxlength="200"
          />
          <div v-if="errors.title" class="form-error">{{ errors.title }}</div>
        </div>

        <div class="form-row">
          <div class="form-group form-col">
            <label class="form-label">活动地点 <span class="required">*</span></label>
            <input
              v-model="form.location"
              type="text"
              class="form-control"
              :class="{ 'has-error': errors.location }"
              placeholder="请输入活动地点"
              maxlength="300"
            />
            <div v-if="errors.location" class="form-error">{{ errors.location }}</div>
          </div>

          <div class="form-group form-col">
            <label class="form-label">人数上限 <span class="required">*</span></label>
            <input
              v-model.number="form.max_participants"
              type="number"
              min="1"
              class="form-control"
              :class="{ 'has-error': errors.max_participants }"
              placeholder="请输入人数上限"
            />
            <div v-if="errors.max_participants" class="form-error">
              {{ errors.max_participants }}
            </div>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group form-col">
            <label class="form-label">开始时间 <span class="required">*</span></label>
            <input
              v-model="form.start_time"
              type="datetime-local"
              class="form-control"
              :class="{ 'has-error': errors.start_time }"
            />
            <div v-if="errors.start_time" class="form-error">{{ errors.start_time }}</div>
          </div>

          <div class="form-group form-col">
            <label class="form-label">活动状态</label>
            <select v-model="form.status" class="form-control">
              <option value="open">报名中</option>
              <option value="draft">草稿</option>
              <option value="closed">已结束</option>
              <option value="cancelled">已取消</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">活动说明</label>
          <textarea
            v-model="form.description"
            class="form-control"
            rows="5"
            placeholder="请输入活动详细说明..."
          ></textarea>
        </div>

        <div class="form-actions">
          <button
            type="submit"
            class="btn btn-primary btn-lg"
            :disabled="submitting"
          >
            {{ submitting ? '提交中...' : isEdit ? '保存修改' : '发布活动' }}
          </button>
          <router-link to="/" class="btn btn-secondary btn-lg">取消</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getActivity, createActivity, updateActivity } from '@/api'

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => !!route.params.id)

const loading = ref(false)
const submitting = ref(false)
const errorMsg = ref('')

const form = reactive({
  title: '',
  location: '',
  start_time: '',
  max_participants: 10,
  description: '',
  status: 'open',
})

const errors = reactive({
  title: '',
  location: '',
  start_time: '',
  max_participants: '',
})

const toLocalInputValue = (isoStr) => {
  if (!isoStr) return ''
  return isoStr.slice(0, 16)
}

const toISO = (localVal) => {
  if (!localVal) return null
  return localVal.length === 16 ? localVal + ':00' : localVal
}

const validate = () => {
  let ok = true
  Object.keys(errors).forEach((k) => (errors[k] = ''))

  if (!form.title.trim()) {
    errors.title = '请输入活动标题'
    ok = false
  } else if (form.title.trim().length > 200) {
    errors.title = '标题不能超过200个字符'
    ok = false
  }

  if (!form.location.trim()) {
    errors.location = '请输入活动地点'
    ok = false
  } else if (form.location.trim().length > 300) {
    errors.location = '地点不能超过300个字符'
    ok = false
  }

  if (!form.start_time) {
    errors.start_time = '请选择开始时间'
    ok = false
  }

  if (!form.max_participants || form.max_participants < 1) {
    errors.max_participants = '人数上限必须是大于0的正整数'
    ok = false
  } else if (!Number.isInteger(Number(form.max_participants))) {
    errors.max_participants = '人数上限必须是整数'
    ok = false
  }

  return ok
}

const handleSubmit = async () => {
  errorMsg.value = ''
  if (!validate()) return

  submitting.value = true
  try {
    const payload = {
      title: form.title.trim(),
      location: form.location.trim(),
      start_time: toISO(form.start_time),
      max_participants: Number(form.max_participants),
      description: form.description.trim() || null,
      status: form.status,
    }

    let result
    if (isEdit.value) {
      result = await updateActivity(route.params.id, payload)
    } else {
      result = await createActivity(payload)
    }
    router.push(`/activities/${result.id}`)
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    submitting.value = false
  }
}

const loadActivity = async () => {
  if (!isEdit.value) return
  loading.value = true
  try {
    const data = await getActivity(route.params.id)
    form.title = data.title
    form.location = data.location
    form.start_time = toLocalInputValue(data.start_time)
    form.max_participants = data.max_participants
    form.description = data.description || ''
    form.status = data.status
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    loading.value = false
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-col {
  margin-bottom: 1rem;
}

.form-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--gray-100);
}

@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
    gap: 0;
  }
}
</style>
