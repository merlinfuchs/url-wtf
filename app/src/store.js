import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
    state: {
        token: localStorage.getItem('token') ?? null,
        user: null,
        scopes: []
    },
    mutations: {
        login(state, token) {
            localStorage.setItem('token', token)
            state.token = token
        },
        logout(state) {
            localStorage.removeItem('token')
            state.token = null
            state.user = null
        }
    },
    actions: {
        apiRequest({commit, state}, {method, path, data}) {
            return fetch(`http://localhost:8000/api${path}`, {
                method: method ?? 'GET',
                body: data ? JSON.stringify(data) : null,
                headers: {'Authorization': state.token, 'Content-Type': 'application/json'}
            })
                .then(resp => {
                    if (resp.status < 300 && resp.status >= 200) {
                        return resp.json()
                    }
                    if (resp.status === 401) {
                        commit('logout')
                        return Promise.reject()
                    }

                    // show notification
                    return Promise.reject()
                })
        },
        refreshUser({dispatch, state}) {
            if (state.token) {
                dispatch('apiRequest', {method: 'GET', path: '/auth/user'})
                    .then(data => state.user = data)
            } else {
                state.user = null
            }
        },
        refreshScopes({dispatch, state}) {
            dispatch('apiRequest', {method: 'GET', path: '/scopes'})
                .then(data => state.scopes = data)
        },
        refresh({dispatch}) {
            dispatch('refreshUser')
            dispatch('refreshScopes')
        },
        resetToken({dispatch, commit}) {
            return dispatch('apiRequest', {method: 'DELETE', path: '/auth/user/token'})
                .then(data => commit('login', data.token))
        },
        loginWithDiscord({dispatch, commit}, {code}) {
            dispatch('apiRequest', {method: 'POST', path: '/auth/discord', data: {code: code}})
                .then(data => {
                    commit('login', data.token)
                    return dispatch('refresh')
                })
        },
        createURL({dispatch}, data) {
            return dispatch('apiRequest', {method: 'POST', path: '/urls', data: data})
        },
        createScope({dispatch}, {name}) {
            return dispatch('apiRequest', {method: 'POST', path: '/scopes', data: {name: name}})
        },
        deleteScope({dispatch}, {name}) {
            return dispatch('apiRequest', {method: 'DELETE', path: `/scopes/${name}`})
        }
    }
})
