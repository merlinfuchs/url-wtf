<template>
    <div class="grid my-20 justify-items-center items-center px-3 sm:px-5">
        <div class="w-full md:w-176 text-xl">
            <div class="grid grid-cols-6 overflow-hidden transition-all duration-500 ease-in-out gap-3 mb-4">
                <div class="col-span-6 md:col-span-3">
                    <div class="mb-2 tracking-wider">
                        <label>Domain</label>
                        <button class="w-6 h-6 bg-gray-dark rounded-full text-sm ml-2"
                                @click="$router.push('/settings')">
                            <i class="fas fa-plus"/>
                        </button>
                    </div>
                    <select v-model="scope"
                            class="rounded-lg bg-gray-darker text-gray-300 py-2 px-2 w-full">
                        <option :value="scope.name" :key="scope.name" v-for="scope in verifiedScopes">
                            {{scope.name}}
                        </option>
                    </select>
                </div>
                <div class="col-span-6 md:col-span-3 mt-4 md:mt-0">
                    <div class="mb-2 tracking-wider">
                        <label>Name</label>
                    </div>
                    <div class="flex w-full">
                        <select v-model="linkType"
                                class="rounded-l-lg bg-gray-darker text-gray-300 py-2 px-2 flex-auto"
                                :class="{'rounded-r-lg': linkType !== 'custom'}">
                            <option value="default">Default</option>
                            <option value="invisible">Invisible</option>
                            <option value="custom">Custom</option>
                        </select>
                        <input type="text" v-if="linkType === 'custom'" v-model="linkName"
                               class="rounded-r-lg py-2 px-2 bg-gray-dark flex-auto">
                    </div>
                </div>
            </div>
            <textarea rows="20" class="w-full flex-1 bg-gray-darker py-4 px-6 rounded-md placeholder-gray-600 mb-3 text-base"
                      v-model="text" placeholder="I like trains" ref="urlInput"/>
            <div class="text-right" v-if="!createdURL">
                <button class="bg-gray-dark px-3 py-2 rounded-md">Create Paste</button>
            </div>
            <div class="flex" v-else>
                <input type="text" class="bg-gray-darker w-5 flex-auto rounded-l-md px-3 py-2" v-model="createdURL">
                <button class="bg-gray-dark px-3 py-2 rounded-r-md flex-initial">Copy</button>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                scope: 'url.wtf',
                linkType: 'default',
                linkName: '',
                text: '',

                createdURL: null
            }
        },
        computed: {
            verifiedScopes() {
                return this.$store.state.scopes.filter(scope => scope.verified || scope.default)
            }
        }
    }
</script>