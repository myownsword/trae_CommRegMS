import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import ActivityDetail from '@/views/ActivityDetail.vue'
import ActivityForm from '@/views/ActivityForm.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
  },
  {
    path: '/activities/new',
    name: 'ActivityCreate',
    component: ActivityForm,
  },
  {
    path: '/activities/:id/edit',
    name: 'ActivityEdit',
    component: ActivityForm,
    props: true,
  },
  {
    path: '/activities/:id',
    name: 'ActivityDetail',
    component: ActivityDetail,
    props: true,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
