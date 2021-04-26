<template>
    <div>
        <div class="w-full text-gray-100">
            <div class="grid mt-20 sm:mt-40 mb-0 justify-items-center items-center px-5 md:px-10">
                <div class="w-full md:w-176 text-md md:text-xl">
                    <div class="text-center mb-20">
                        <h2 class="text-5xl md:text-6xl text-gray-200 font-bold tracking-tight">Make your links
                            shorter.</h2>
                        <h5 class="text-lg md:text-xl mt-3 text-gray-400 font-thin">
                            Use <span class="font-semibold tracking-wider">url.wtf</span> or
                            <router-link to="/settings" class="hover:text-red-300">add your <span class="font-semibold">own domain</span>
                            </router-link>
                        </h5>
                    </div>
                    <div class="flex">
                        <input type="url" class="w-5 flex-1 bg-gray-darker py-4 px-6 rounded-l-md placeholder-gray-600"
                               v-model="urlText" placeholder="https://twitter.com" ref="urlInput">
                        <button type="button" class="flex-grow-0 flex-shrink bg-gray-dark py-4 px-6 rounded-r-md"
                                v-if="!shortened"
                                @click="createURL">Shorten
                        </button>
                        <button type="button" class="flex-grow-0 flex-shrink bg-gray-dark py-4 px-6 rounded-r-md"
                                v-if="shortened"
                                @click="copyURL">Copy
                        </button>
                    </div>
                    <div class="mt-6">
                        <div class="grid grid-cols-6 mb-3 overflow-hidden transition-all duration-500 ease-in-out"
                             :class="{'max-h-96': optionsVisible, 'max-h-0': !optionsVisible, 'mb-8': optionsVisible}">
                            <div class="col-span-6 md:col-span-3 px-2">
                                <div class="mb-2 tracking-wider">
                                    <label>Domain</label>
                                    <router-link to="/settings" class="ml-2">
                                        <button class="w-6 h-6 bg-gray-dark rounded-full text-sm">
                                            <i class="fas fa-plus"/>
                                        </button>
                                    </router-link>
                                </div>
                                <select v-model="scope"
                                        class="rounded-lg bg-gray-dark text-gray-300 py-2 px-2 w-full">
                                    <option :value="scope.name" :key="scope.name" v-for="scope in verifiedScopes">
                                        {{scope.name}}
                                    </option>
                                </select>
                            </div>
                            <div class="col-span-6 md:col-span-3 px-2 mt-4 md:mt-0">
                                <div class="mb-2 tracking-wider">
                                    <label>Name</label>
                                </div>
                                <div class="flex w-full">
                                    <select v-model="linkType"
                                            class="rounded-l-lg bg-gray-dark text-gray-300 py-2 px-2"
                                            :class="{'rounded-r-lg': linkType !== 'custom',
                                            'flex-shrink': linkType === 'custom', 'flex-auto': linkType !== 'custom'}">
                                        <option value="default">Default</option>
                                        <option value="invisible">Invisible</option>
                                        <option value="custom">Custom</option>
                                    </select>
                                    <input type="text" v-if="linkType === 'custom'" v-model="linkName"
                                           class="rounded-r-lg py-2 px-2 w-5 bg-gray-darker flex-auto">
                                </div>
                            </div>
                        </div>

                        <div class="text-center">
                            <button class="text-gray-500 bg-gray-dark rounded-full w-12 h-12"
                                    @click="optionsVisible = !optionsVisible" v-if="!optionsVisible">
                                <span><i class="fas fa-angle-double-down"/></span>
                            </button>
                            <button class="text-gray-500 bg-gray-dark rounded-full w-12 h-12"
                                    @click="optionsVisible = !optionsVisible" v-else>
                                <span><i class="fas fa-angle-double-up"/></span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 100 1440 320"
             class="fill-current text-gray-darkest bg-gray-darker">
            <path fill="current" fill-opacity="1"
                  d="M0,128L120,154.7C240,181,480,235,720,261.3C960,288,1200,288,1320,288L1440,288L1440,0L1320,0C1200,0,960,0,720,0C480,0,240,0,120,0L0,0Z"/>
        </svg>
        <div v-if="!$store.state.token"
             class="grid bg-gray-darker pt-16 md:pt-5 pb-32 sm:pb-40 lg:pb-60 lg:pt-20 w-full justify-items-center text-center">
            <div class="w-full md:w-176 px-3">
                <div class="text-4xl sm:text-5xl font-thin">Login to see your links</div>
                <div class="text-6xl sm:text-8xl mt-10 sm:mt-16">
                    <a href="/api/auth/discord" class="mr-20 hover:text-gray-300">
                        <i class="fab fa-discord"/>
                    </a>
                    <a href="/api/auth/github" class="hover:text-gray-300">
                        <i class="fab fa-github"/>
                    </a>
                </div>
            </div>
        </div>
        <div v-else class="grid bg-gray-darker pt-16 md:pt-0 pb-40 justify-items-center">
            <div class="w-full md:w-176 px-3">
                <div v-if="urls.length === 0" class="text-4xl text-center">
                    <div>You don't have any links yet ...</div>
                </div>
                <transition-group v-else name="fade">
                    <div v-for="url in urls" :key="url.id" class="bg-gray-dark p-5 rounded-lg mb-5">
                        <div class="flex">
                            <div class="grid grid-cols-2 flex-auto">
                                <div class="text-xl font-thin col-span-2 md:col-span-1  mb-2 md:mb-0">
                                    <a :href="`https://${url.scope}/${url.name}`"
                                       target="_blank">{{url.scope}}/{{url.name}}</a>
                                </div>
                                <div class="text-xl font-thin text-blue-200 col-span-2 md:col-span-1">
                                    <a :href="url.target" target="_blank">{{url.target}}</a>
                                </div>
                            </div>
                            <div class="flex-initial">
                                <router-link :to="`/stats/${url.id}`" class="mr-2">
                                    <button class="text-blue-500 bg-gray-darker rounded-full w-8 h-8 text-sm">
                                        <i class="fas fa-chart-bar"/>
                                    </button>
                                </router-link>
                                <button class="text-red-500 bg-gray-darker rounded-full w-8 h-8 text-sm"
                                        @click="() => deleteURL(url.id)">
                                    <i class="fas fa-trash"/>
                                </button>
                            </div>
                        </div>
                    </div>
                </transition-group>
            </div>
        </div>

        <!-- <div class="bg-gray-darker pb-40 w-full px-3 sm:px-10">
            <div class="grid justify-items-center items-center">
                <div class="grid grid-cols-2 w-full xl:w-304 justify-items-center">
                    <div class="col-span-2 lg:col-span-1">
                        <img src="https://discord.com/assets/c01c644bc9fa2a28678ae2f44969d248.svg" alt="" loading="lazy">
                    </div>
                    <div class="col-span-2 lg:col-span-1 justify-self-end px-10 sm:px-20 lg:pr-0 xl:pl-40 xl:pr-20">
                        <h2 class="text-2xl sm:text-4xl font-bold tracking-wider leading-snug mb-8 mt-10">
                            Login to see all your previously created links
                        </h2>
                        <p class="font-thin text-lg sm:text-xl">
                            Discord servers are organized into topic-based channels where you can collaborate, share,
                            and just talk about your day without clogging up a group chat.
                        </p>
                    </div>
                </div>
            </div>
        </div>
        <div class="bg-gray-darkest py-40 w-full px-3 sm:px-10">
            <div class="grid justify-items-center items-center">
                <div class="grid grid-cols-2 w-full xl:w-304 justify-items-center">
                    <div class="col-span-2 lg:col-span-1 lg:row-start-1 lg:col-start-2">
                        <img src="https://discord.com/assets/98c9edf635a98377ec579aaa19ed47be.svg" alt="" loading="lazy">
                    </div>
                    <div class="col-span-2 lg:col-span-1 px-10 sm:px-20 lg:pl-0 xl:pr-40 xl:pl-20 lg:row-start-1 lg:col-start-1">
                        <h2 class="text-2xl sm:text-4xl font-bold tracking-wider leading-snug mb-8 mt-10">
                            Upload your images and share them with your friends
                        </h2>
                        <p class="font-thin text-lg sm:text-xl">
                            Discord servers are organized into topic-based channels where you can collaborate, share,
                            and just talk about your day without clogging up a group chat.
                        </p>
                    </div>
                </div>
            </div>
        </div>
        <div class="bg-gray-darker py-40 w-full px-3 sm:px-10">
            <div class="grid justify-items-center items-center">
                <div class="grid grid-cols-2 w-full xl:w-304 justify-items-center">
                    <div class="col-span-2 lg:col-span-1">
                        <img src="https://discord.com/assets/9184fcadc2e3c84650dd4b075850d3d6.svg" alt="" loading="lazy">
                    </div>
                    <div class="col-span-2 lg:col-span-1 justify-self-end px-10 sm:px-20 lg:pr-0 xl:pl-40 xl:pr-20">
                        <h2 class="text-2xl sm:text-4xl font-bold tracking-wider leading-snug mb-8 mt-10">
                            Add your own domain to customize your links
                        </h2>
                        <p class="font-thin text-lg sm:text-xl">
                            Discord servers are organized into topic-based channels where you can collaborate, share,
                            and just talk about your day without clogging up a group chat.
                        </p>
                    </div>
                </div>
            </div>
        </div> -->
    </div>
</template>

<script>
    export default {
        name: 'Home',
        components: {},
        data() {
            return {
                optionsVisible: false,

                scope: 'url.wtf',
                linkType: 'default',
                linkName: '',
                shortened: false,
                urlText: '',

                urls: []
            }
        },
        created() {
            this.reloadURLs()
        },
        methods: {
            reloadURLs() {
                if (this.$store.state.token) {
                    this.$store.dispatch('getURLs')
                        .then(data => this.urls = data)
                }
            },
            createURL() {
                this.$store.dispatch('createURL', {
                    scope: this.scope,
                    target: this.urlText,
                    type: this.linkType,
                    name: this.linkName.trim() !== '' ? this.linkName : null
                })
                    .then(data => {
                        this.urlText = data.url
                        this.shortened = true
                        this.urls.push(data)
                    })
            },
            copyURL() {
                this.$refs.urlInput.select()
                document.execCommand('copy')

                setTimeout(() => {
                    this.shortened = false;
                    this.urlText = ''
                }, 1000)
            },
            deleteURL(id) {
                this.$store.dispatch('deleteURL', {id: id})
                    .then(() => {
                        for (let i in this.urls) {
                            const url = this.urls[i]
                            if (url.id === id) {
                                this.urls.splice(i, 1)
                                break
                            }
                        }
                    })
            }
        },
        computed: {
            verifiedScopes() {
                return this.$store.state.scopes.filter(scope => scope.verified || scope.default)
            }
        }
    }
</script>

<style>
    select::-ms-expand {
        display: none;
    }

    select {
        -webkit-appearance: none;
        -moz-appearance: none;
        text-indent: 1px;
        text-overflow: '';
    }
</style>
