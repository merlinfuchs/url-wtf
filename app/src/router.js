import Vue from 'vue'
import VueRouter from 'vue-router'
import Links from './views/Links.vue'
import store from './store.js'

Vue.use(VueRouter)

const routes = [
    {
        path: '/',
        name: 'Links',
        component: Links
    },
    {
        path: '/images',
        name: 'Images',
        component: () => import(/* webpackChunkName: "images" */ './views/Images.vue'),
        meta: {requiresLogin: true}
    },
    {
        path: '/pastes',
        name: 'Pastes',
        component: () => import(/* webpackChunkName: "pastes" */ './views/Pastes.vue'),
        meta: {requiresLogin: true}
    },
    {
        path: '/api',
        name: 'Pastes',
        component: () => import(/* webpackChunkName: "api" */ './views/API.vue')
    },
    {
        path: '/settings',
        name: 'Settings',
        component: () => import(/* webpackChunkName: "settings" */ './views/Settings.vue'),
        meta: {requiresLogin: true}
    },
    {
        path: '/stats/:id',
        name: 'Stats',
        component: () => import(/* webpackChunkName: "stats" */ './views/Stats.vue'),
        meta: {requiresLogin: true}
    },
    {
        path: '/login',
        name: 'Login',
        component: () => import(/* webpackChunkName: "login" */ './views/Login.vue')
    },
    {
        path: '/login/callback/:platform',
        name: 'Login',
        component: () => import(/* webpackChunkName: "login_callback" */ './views/LoginCallback.vue')
    },
    {
        path: '/terms',
        name: 'Terms',
        component: () => import(/* webpackChunkName: "terms" */ './views/Terms.vue')
    },
    {
        path: '/privacy',
        name: 'Privacy',
        component: () => import(/* webpackChunkName: "privacy" */ './views/Privacy.vue')
    }
]

const router = new VueRouter({
    mode: 'history',
    base: process.env.BASE_URL,
    routes
})

router.beforeEach((to, from, next) => {
    if (to.matched.some(record => record.meta.requiresLogin) && !store.state.token) {
        next("/login")
    } else {
        next()
    }
})

export default router
