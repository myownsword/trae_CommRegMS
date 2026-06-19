import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.message ||
      '请求失败，请稍后重试'
    return Promise.reject(new Error(message))
  }
)

export const getStatistics = () => api.get('/statistics').then((r) => r.data)

export const getActivities = (params) =>
  api.get('/activities', { params }).then((r) => r.data)

export const getActivity = (id) =>
  api.get(`/activities/${id}`).then((r) => r.data)

export const createActivity = (data) =>
  api.post('/activities', data).then((r) => r.data)

export const updateActivity = (id, data) =>
  api.put(`/activities/${id}`, data).then((r) => r.data)

export const cancelActivity = (id) =>
  api.post(`/activities/${id}/cancel`).then((r) => r.data)

export const registerActivity = (id, data) =>
  api.post(`/activities/${id}/registrations`, data).then((r) => r.data)

export const cancelRegistration = (id, data) =>
  api.post(`/activities/${id}/registrations/cancel`, data).then((r) => r.data)

export default api
