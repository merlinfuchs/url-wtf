<template>
    <div class="grid my-20 sm:mt-40 justify-items-center items-center px-3 sm:px-5">
        <div class="w-full md:w-176 text-xl">
            <div class="text-center mb-20">
                <h2 class="text-5xl md:text-6xl text-gray-200 font-bold tracking-tight">Share your images.</h2>
                <h5 class="text-lg md:text-xl mt-3 text-gray-400 font-thin">
                    Use <span class="font-semibold tracking-wider">url.wtf</span> or
                    <router-link to="/settings" class="hover:text-red-300">add your <span class="font-semibold">own domain</span>
                    </router-link>
                </h5>
            </div>
            <div class="flex" v-if="!urlText">
                <input type="file" class="w-5 flex-1 bg-gray-darker py-4 px-6 rounded-l-md placeholder-gray-600"
                       ref="fileInput" accept="image/*">
                <button type="button" class="flex-grow-0 flex-shrink bg-gray-dark py-4 px-6 rounded-r-md"
                        @click="uploadImage">Upload
                </button>
            </div>
            <div v-else>
                <div class="flex">
                    <input type="text" class="w-5 flex-1 bg-gray-darker py-4 px-6 rounded-l-md placeholder-gray-600"
                           ref="urlInput" accept="image/*" v-model="urlText">
                    <button type="button" class="flex-grow-0 flex-shrink bg-gray-dark py-4 px-6 rounded-r-md"
                            @click="copyURL">Copy
                    </button>
                </div>
                <div class="bg-gray-dark mt-5 rounded-md p-3">
                    <img :src="urlText" alt="Uploaded image" class="w-full">
                </div>
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
                                    class="rounded-l-lg bg-gray-dark text-gray-300 py-2 px-2 flex-shrink"
                                    :class="{'rounded-r-lg': linkType !== 'custom',
                                    'flex-shrink': linkType === 'custom', 'flex-auto': linkType !== 'custom'}">
                                <option value="default">Default</option>
                                <option value="invisible">Invisible</option>
                                <option value="custom">Custom</option>
                            </select>
                            <input type="text" v-if="linkType === 'custom'" v-model="linkName"
                                   class="rounded-r-lg py-2 px-2 bg-gray-darker w-5 flex-auto">
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
</template>

<script>
    export default {
        data() {
            return {
                optionsVisible: false,

                scope: 'url.wtf',
                linkType: 'default',
                linkName: '',

                urlText: null
            }
        },
        methods: {
            uploadImage() {
                const files = this.$refs.fileInput.files
                if (files.length === 0) return
                const file = files[0]
                this.$store.dispatch('uploadImage', {
                    file: file,
                    scope: this.scope,
                    type: this.linkType,
                    name: this.linkName.trim() !== '' ? this.linkName : null
                })
                    .then(data => {
                        this.urlText = data.url
                    })
            },
            copyURL() {
                this.$refs.urlInput.select()
                document.execCommand('copy')

                setTimeout(() => {
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
