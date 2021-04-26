<template>
    <div id="app" class="bg-gray-darkest w-screen overflow-hidden text-gray-100 m-0">
        <div class="fixed top-0 right-0 grid justify-items-end">
            <div class="w-full sm:w-128 px-5 pt-5">
                <div v-for="(notification, i) in $store.state.notifications" :key="`notification-${i}`"
                     class="px-5 py-4 rounded-lg mb-3 opacity-95 font-semibold tracking-wide"
                     :class="{'bg-red-500': notification.type === 'error', 'bg-blue-500': notification.type === 'info',
                     'bg-green-500': notification.type === 'success'}">
                    {{notification.text}}
                </div>
            </div>
        </div>

        <div class="min-h-screen">
            <nav class="flex items-center justify-between w-full flex-wrap px-8 py-5 bg-gray-darker md:bg-transparent">
                <router-link to="/" class="mr-7">
                    <div class="flex items-center flex-shrink-0">
                    <span class="font-normal text-2xl pr-1 mr-2">
                        <i class="fas fa-link"/>
                    </span>
                        <span class="font-bold text-2xl tracking-light">url.wtf</span>
                    </div>
                </router-link>
                <button class="block md:hidden flex items-center px-3 py-2 rounded" @click="menuVisible = !menuVisible">
                    <i class="fas fa-bars"/>
                </button>
                <div class="w-full flex-grow md:flex md:items-center md:w-auto"
                     :class="{hidden: !menuVisible, block: menuVisible}">
                    <div class="text-md md:flex-grow font-bold leading-tight">
                        <router-link to="/"
                                     class="block mt-6 mb-4 md:my-0 md:inline-block md:mt-0 hover:text-red-300 mr-4"
                                     active-class="text-red-300" exact>Links
                        </router-link>
                        <router-link to="/images"
                                     class="block mb-4 md:my-0 md:inline-block md:mt-0 hover:text-red-300 mr-5"
                                     active-class="text-red-300">Images
                        </router-link>
                        <!-- <router-link to="/pastes"
                                     class="block mb-4 md:my-0 md:inline-block md:mt-0 hover:text-red-300 mr-5"
                                     active-class="text-red-300">Pastes
                        </router-link> -->
                        <router-link to="/api"
                                     class="block mb-4 md:my-0 md:inline-block md:mt-0 hover:text-red-300 mr-5"
                                     active-class="text-red-300">API
                        </router-link>
                        <span class="mt-4 md:mt-0 md:inline-flex flex flex-row">
                        <a href="/discord" class="mr-4 block md:inline-block hover:text-red-300" target="_blank">
                            <i class="fab fa-discord"/>
                        </a>
                    </span>
                    </div>
                    <div class="mt-6 md:my-0">
                        <router-link to="/login"
                                     class="inline-block bg-gray-dark hover:bg-gray-800 py-3 px-4 rounded-lg"
                                     v-if="!$store.state.user">
                            <i class="fas fa-sign-in-alt"/>
                            <span class="ml-1">Login</span>
                        </router-link>
                        <div v-else class="group">
                            <button class="bg-gray-dark py-3 px-4 rounded-md">
                                {{$store.state.user.name}}
                                <span class="text-sm ml-2"><i class="fas fa-chevron-down"/></span>
                            </button>
                            <div class="absolute hidden group-hover:block pt-2">
                                <div class="px-4 py-3 bg-gray-dark rounded-md">
                                    <router-link to="/settings" class="cursor-pointer block">
                                        <i class="fas fa-cog"/>
                                        <span class="ml-2">Settings</span>
                                    </router-link>
                                    <button @click="logout" class="cursor-pointer block text-red-500 pt-2">
                                        <i class="fas fa-sign-out-alt"/>
                                        <span class="ml-2">Logout</span>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </nav>
            <transition name="fade" mode="out-in">
                <router-view/>
            </transition>
            <div class="h-52"></div>
        </div>

        <div class="h-52 -mt-52 grid justify-items-center items-center"
             :class="{'bg-gray-darker': !$route.name || !['Links'].includes($route.name.toString())}">
            <div class="w-full px-10 text-xl flex flex-wrap overflow-hidden">
                <div class="flex-none mb-5 md:mb-0 md:px-10 w-full md:w-1/2 md:text-right">
                    <div class="text-xl">Copyright <span class="font-bold">©</span> 2021 <span
                            class="font-bold">url.wtf</span></div>
                    <div class="mt-2 text-red-300">
                        <a href="mailto:contact@url.wtf" target="_blank">Contact & Takedown</a>
                    </div>
                </div>
                <div class="flex-none w-full md:w-1/2">
                    <div class="text-blue-200">
                        <router-link to="/terms" class="mr-3">Terms of Service</router-link>
                        <router-link to="/privacy">Privacy Policy</router-link>
                    </div>
                    <div class="mt-2">
                        <a href="/discord" class="mr-4 block md:inline-block hover:text-blue-200" target="_blank">
                            <i class="fab fa-discord"/>
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                menuVisible: false,
                contactVisible: false,
            }
        },
        created() {
            this.$store.dispatch('refresh')
        },
        methods: {
            logout() {
                this.$store.commit('logout')
                this.$store.dispatch('refresh')
                    .then(() => this.$router.push('/'))
            }
        }
    }
</script>