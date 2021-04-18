import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
    state: {
        notifications: [],

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
        notify({state}, {text, type = 'info', delta = 3000}) {
            const notification = {text, type}
            state.notifications.push(notification)
            setTimeout(() => {
                const index = state.notifications.indexOf(notification)
                if (index > -1) {
                    state.notifications.splice(index, 1)
                }
            }, delta)
        },
        apiRequest({commit, state, dispatch}, {method, path, data}) {
            const headers = {'Authorization': state.token}
            if (data && !(data instanceof FormData)) {
                data = JSON.stringify(data)
                headers['Content-Type'] = 'application/json'
            }

            return fetch(`https://url.wtf/api${path}`, {
                method: method ?? 'GET',
                body: data,
                headers: headers
            })
                .then(resp => {
                    if (resp.status < 300 && resp.status >= 200) {
                        return resp.json()
                    }
                    if (resp.status === 401) {
                        if (state.token) {
                            dispatch('notify', {type: 'error', text: 'You have been logged out.'})
                        } else {
                            dispatch('notify', {type: 'error', text: 'You need to be logged in.'})
                        }
                        commit('logout')
                        return Promise.reject()
                    }

                    // show notification
                    resp.json()
                        .then(data => dispatch('notify', {type: 'error', text: data.text}))
                        .catch(() => dispatch('notify', {type: 'error', text: `Unexpected Error (${resp.status})`}))
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
        loginWithCode({dispatch, commit}, {code, platform}) {
            return dispatch('apiRequest', {method: 'POST', path: `/auth/${platform}`, data: {code: code}})
                .then(data => {
                    commit('login', data.token)
                    return dispatch('refresh')
                })
        },
        deleteAccount({dispatch, commit}) {
            return dispatch('apiRequest', {method: 'DELETE', path: '/auth/user'})
                .then(() => commit('logout'))
        },
        createURL({dispatch}, data) {
            return dispatch('apiRequest', {method: 'POST', path: '/urls', data: data})
        },
        getURLs({dispatch}) {
            return dispatch('apiRequest', {method: 'GET', path: '/urls'})
        },
        deleteURL({dispatch}, {id}) {
            return dispatch('apiRequest', {method: 'DELETE', path: `/urls/${id}`})
        },
        createScope({dispatch}, {name}) {
            return dispatch('apiRequest', {method: 'POST', path: '/scopes', data: {name: name}})
        },
        deleteScope({dispatch}, {name}) {
            return dispatch('apiRequest', {method: 'DELETE', path: `/scopes/${name}`})
        },
        uploadImage({dispatch}, data) {
            const file = data.file
            delete data.file

            const form = new FormData();
            form.append('json', JSON.stringify(data))
            form.append('file', file)

            return dispatch('apiRequest', {method: 'POST', path: '/images', data: form})
        },
        getStats({dispatch}, {id, period}) {
            return dispatch('apiRequest', {method: 'GET', path: `/stats/${id}/${period}`})
        }
    }
})
