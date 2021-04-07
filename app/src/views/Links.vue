<template>
    <div>
        <div class="w-full text-gray-100">
            <div class="grid mt-40 mb-0 justify-items-center items-center px-5 md:px-10">
                <div class="w-full md:w-176 text-md md:text-xl">
                    <div class="text-center mb-20">
                        <h2 class="text-5xl md:text-6xl text-gray-200 font-bold tracking-tight">Make your links shorter.</h2>
                        <h5 class="text-lg md:text-xl mt-3 text-gray-400 font-thin">
                            Use <span class="font-semibold tracking-wider">url.wtf</span> or
                            <router-link to="/settings" class="hover:text-red-300">add your <span class="font-semibold">own domain</span>
                            </router-link>
                        </h5>
                    </div>
                    <div class="flex">
                        <input type="url" class="w-5 flex-1 bg-gray-darker py-4 px-6 rounded-l-md placeholder-gray-600"
                               v-model="urlText" placeholder="https://twitter.com" ref="urlInput">
                        <button type="button" class="flex-grow-0 flex-shrink bg-gray-dark py-4 px-6 rounded-r-md" v-if="!shortened"
                                @click="createURL">Shorten
                        </button>
                        <button type="button" class="flex-grow-0 flex-shrink bg-gray-dark py-4 px-6 rounded-r-md" v-if="shortened"
                                @click="copyURL">Copy
                        </button>
                    </div>
                    <div class="mt-6">
                        <div class="grid grid-cols-6 mb-3 overflow-hidden transition-all duration-500 ease-in-out"
                             :class="{'max-h-96': optionsVisible, 'max-h-0': !optionsVisible, 'mb-8': optionsVisible}">
                            <div class="col-span-6 md:col-span-3 px-2">
                                <div class="mb-2 tracking-wider">
                                    <label>Domain</label>
                                    <button class="w-6 h-6 bg-gray-dark rounded-full text-sm ml-2"
                                            @click="$router.push('/settings')">
                                        <i class="fas fa-plus"/>
                                    </button>
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
                                            class="rounded-l-lg bg-gray-dark text-gray-300 py-2 px-2 flex-auto"
                                            :class="{'rounded-r-lg': linkType !== 'custom'}">
                                        <option value="default">Default</option>
                                        <option value="invisible">Invisible</option>
                                        <option value="custom">Custom</option>
                                    </select>
                                    <input type="text" v-if="linkType === 'custom'" v-model="linkName"
                                           class="rounded-r-lg py-2 px-2 bg-gray-darker flex-auto">
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
        <div class="bg-gray-darker pb-96 w-full">
        </div>
        <div class="bg-gray-darker pb-96 w-full">
        </div>
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

                links: []
            }
        },
        methods: {
            createURL() {
                this.$store.dispatch('createURL', {
                    scope: this.scope,
                    target: this.urlText,
                    type: this.linkType,
                    name: this.linkName
                })
                    .then(data => {
                        this.urlText = data.url
                        this.shortened = true
                    })
            },
            copyURL() {
                this.$refs.urlInput.select()
                document.execCommand('copy')

                setTimeout(() => {
                    this.shortened = false;
                    this.urlText = ''
                }, 1000)
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
