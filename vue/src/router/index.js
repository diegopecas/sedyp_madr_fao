import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import inicio from '../views/inicio.vue'
import newEvent from '../views/newEvent.vue'
import updateUser from '../views/updateUser.vue'
import seguimientoMal from '../views/seguimientoMal.vue'
import informesEvento from '../views/informesEvento.vue'
import informesGenerales from '../views/informesGenerales.vue'
import validateUser from '../views/validateUser.vue'
import roles from '../views/roles.vue'
import auditoria from '../views/auditoria.vue'
import gastosAgricolas from '../views/gastosAgricolas.vue'
import forgotPassword from '../views/forgotPassword.vue'

Vue.use(VueRouter)

var self = Vue.prototype

const routes = [
  {
    path: '/inicio',
    name: 'inicio',
    component: inicio
  },
  {
    path: '/home',
    name: 'listadoEventos',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/newEvento',
    name: 'nuevoEvento',
    component: newEvent,
    meta: { requiresAuth: true }
  },
  {
    path: '/newEvento/:evento',
    name: 'actualizarEvento',
    component: newEvent,
    meta: { requiresAuth: true }
  },
  {
    path: '/updateUser',
    name: 'editarUsuario',
    component: updateUser,
    meta: { requiresAuth: true }
  },
  {
    path: '/seguimientoMal/:evento',
    name: 'seguimientoMal',
    props: true,
    component: seguimientoMal,
    meta: { requiresAuth: true }
  },
  {
    path: '/informesEvento/:evento',
    name: 'informesEvento',
    props: true,
    component: informesEvento,
    meta: { requiresAuth: true }
  },
  {
    path: '/informesGenerales/',
    name: 'informesGenerales',
    props: true,
    component: informesGenerales,
    meta: { requiresAuth: true }
  },
  {
    path: '/validate/:code',
    name: 'validate',
    props: true,
    component: validateUser,
  },
  {
    path: '/forgotPassword/:code',
    name: 'forgotPassword',
    props: true,
    component: forgotPassword,
  },
  {
    path: '*',
    name: 'notRoute',
    redirect: '/home',
    meta: { requiresAuth: true }
  },
  {
    path: '/roles',
    name: 'roles',
    component: roles,
    meta: { requiresAuth: true }
  },
  {
    path: '/auditoria',
    name: 'auditoria',
    component: auditoria,
    meta: { requiresAuth: true }
  },
  {
    path: '/gastosAgricolas',
    name: 'gastosAgricolas',
    component: gastosAgricolas,
    meta: { requiresAuth: true }
  },
  {
    path: '/about',
    name: 'About',
    component: () => import(/* webpackChunkName: "about" */ '../views/About.vue')
  },
  {
    path: '/logout',
    name: 'logout',
    meta: { requiresAuth: false }
  }
]

const originalPush = VueRouter.prototype.push

VueRouter.prototype.push = function push(location) {

  return originalPush.call(this, location).catch(err => err)

}

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})
router.beforeEach((to, from, next) => {
  const loggedIn = self.$session.exists()
  console.log(loggedIn);
  if (loggedIn && to.matched.some(record => record.meta.requiresAuth)) {
    next()
  } else {
    if (loggedIn && !to.name === 'inicio') {
      self.$session.destroy()
      next('/inicio')
    } else if (!loggedIn && to.name === 'listadoEventos') {
      next('/inicio')
    } else if (loggedIn && to.name === 'inicio') {
      next('/home')
    } else if(!loggedIn && to.matched.some(record => record.meta.requiresAuth)) {
      next('/inicio')
    } else {
      next()
    }
  }
})

export default router
