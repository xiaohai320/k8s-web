import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [

  {
    path: '/pod',
    name: 'pod',
    component: () => import('../views/pod.vue')
  },
  {
    path: '/deployment',
    name: 'deployment',
    component: () => import('../views/deployment.vue')
  },
  {
    path: '/node',
    name: 'ndoe',
    component: () => import('../views/Node.vue')
  },
  {
    path: '/log',
    name: 'about',
    component: () => import('../views/Log.vue')
  }, {
    path: '/yidong',
    name: 'about',
    component: () => import('../views/Yidong.vue')
  }
  , {
    path: '/setting',
    name: 'about',
    component: () => import('../views/setting.vue')
  }, {
    path: '/views',
    name: 'about',
    component: () => import('../views/Views.vue')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
