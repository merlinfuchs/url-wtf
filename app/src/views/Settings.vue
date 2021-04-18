<template>
    <div class="grid my-20 justify-items-center items-center px-3">
        <div class="w-full md:w-176">
            <div class="bg-gray-darker p-5 rounded-lg">
                <h3 class="text-3xl align-middle mb-3">
                    <span class="text-2xl"><i class="fas fa-signature"/></span>
                    <span class="ml-4">Custom Domains</span>
                </h3>
                <div class="md:p-1 text-lg">
                    <div class="font-thin">
                        <p class="mb-2">You can add custom domains to <span class="font-normal">url.wtf</span> to
                            customize
                            your links.
                            Instead of <span class="font-normal">url.wtf/name</span>
                            you will have <span class="font-normal">your-domain.com/name</span>.</p>
                        <p class="hidden">You can even share your domain with other people on <span class="font-normal">url.wtf</span>
                            and contribute it to the community.</p>
                    </div>

                    <div class="mt-5" v-if="$store.state.user">
                        <div v-for="scope in $store.state.scopes" :key="scope.name">
                            <div v-if="scope.owner_id === $store.state.user.id"
                                 class="bg-gray-darkest rounded-lg px-5 py-4 mb-5">
                                <div class="flex">
                                    <span class="text-xl flex-auto">
                                        <span>{{scope.name}}</span>
                                        <span class="text-sm ml-2">
                                            <span v-if="!scope.verified" class="text-yellow-500">
                                                <i class="fas fa-exclamation-triangle"/>
                                            </span>
                                            <span v-else class="text-green-500">
                                                <i class="fas fa-check-circle"/>
                                            </span>
                                        </span>
                                    </span>
                                    <button class="flex-initial text-red-500 bg-gray-dark rounded-full w-8 h-8 text-sm"
                                            @click="() => deleteDomain(scope.name)">
                                        <i class="fas fa-trash"/>
                                    </button>
                                </div>
                                <div v-if="!scope.verified" class="mt-3">
                                    <p class="font-thin">
                                        This domain hasn't been setup yet, please create the following DNS records.
                                    </p>
                                    <div class="flex mt-4">
                                        <div class="flex-initial mr-2 md:mr-3">
                                            <div class="font-bold mb-2">Type</div>
                                            <div class="bg-gray-darker p-1 md:px-2 rounded-lg mb-2">
                                                CNAME
                                            </div>
                                            <div class="bg-gray-darker p-1 md:px-2 rounded-lg">
                                                TXT
                                            </div>
                                        </div>
                                        <div class="flex-grow mr-2 md:mr-3">
                                            <div class="font-bold mb-2">Name</div>
                                            <div class="bg-gray-darker p-1 md:px-2 rounded-lg mb-2 break-all">
                                                {{scope.name}}
                                            </div>
                                            <div class="bg-gray-darker p-1 md:px-2 rounded-lg break-all">
                                                {{scope.name}}
                                            </div>
                                        </div>
                                        <div class="flex-grow">
                                            <div class="font-bold mb-2">Content</div>
                                            <div class="bg-gray-darker p-1 md:px-2 rounded-lg mb-2 break-all">
                                                custom.url.wtf
                                            </div>
                                            <div class="bg-gray-darker p-1 md:px-2 rounded-lg break-all">
                                                url.wtf={{$store.state.user.id}}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="flex">
                            <input type="text" v-model="newDomain"
                                   class="w-5 bg-gray-darkest flex-auto px-3 py-2 rounded-lg placeholder-gray-500"
                                   placeholder="your-domain.com">
                            <button class="bg-gray-dark flex-initial ml-4 rounded-lg px-3 py-2" @click="addDomain">
                                Add<span class="hidden md:inline"> Domain</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="bg-gray-darker p-5 rounded-lg mt-10">
                <h3 class="text-3xl align-middle">
                    <span class="text-2xl"><i class="fas fa-code"/></span>
                    <span class="ml-4">API Access</span>
                </h3>
                <div class="mt-3 md:p-1">
                    <p class="font-thin">
                        To be able to use your custom domains with the API,
                        you have to include the token in your requests.
                        <router-link class="font-normal" to="/api">Read more</router-link>
                    </p>
                    <div class="mt-5">
                        <div class="flex">
                            <textarea rows="4" v-model="token" ref="tokenInput"
                                      class="w-5 bg-gray-darkest flex-auto px-3 py-2 rounded-lg placeholder-gray-500"
                            />
                            <div>
                                <button class="block bg-gray-dark flex-initial ml-4 rounded-lg px-3 py-2"
                                        @click="copyToken">
                                    Copy<span class="hidden md:inline"> Token</span>
                                </button>
                                <button class="block bg-gray-dark flex-initial ml-4 rounded-lg px-3 py-2 mt-2"
                                        @click="resetToken">
                                    Reset<span class="hidden md:inline"> Token</span>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="bg-gray-darker p-5 rounded-lg mt-10">
                <h3 class="text-3xl align-middle">
                    <span class="text-2xl"><i class="fas fa-exclamation-triangle"/></span>
                    <span class="ml-4">Danger Zone</span>
                </h3>
                <div class="mt-3 md:p-1">
                    <p class="font-thin">
                        Deleting your account will also delete all your links, image, pastes and custom domains.
                        <span class="font-normal">This can not be undone!</span>
                    </p>
                    <div class="mt-5">
                        <div class="flex">
                            <input class="w-5 bg-gray-darkest flex-auto px-3 py-2 rounded-lg placeholder-gray-500"
                                   placeholder="Repeat your Email" type="email" v-model="repeatEmail"/>
                            <button class="block bg-red-700 flex-initial ml-4 rounded-lg px-3 py-2"
                                    @click="deleteAccount">
                                Delete Account
                            </button>
                        </div>
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
                newDomain: '',
                repeatEmail: ''
            }
        },
        methods: {
            addDomain() {
                const name = this.newDomain.trim()
                if (!name) return
                this.$store.dispatch('createScope', {name})
                    .then(() => this.$store.dispatch('refreshScopes'))
            },
            deleteDomain(name) {
                this.$store.dispatch('deleteScope', {name})
                    .then(() => this.$store.dispatch('refreshScopes'))
            },
            resetToken() {
                this.$store.dispatch('resetToken')
            },
            copyToken() {
                this.$refs.tokenInput.select()
                document.execCommand('copy')
            },
            deleteAccount() {
                if (this.repeatEmail.trim() !== this.$store.state.user.email) {
                    this.$store.dispatch('notify', {
                        text: 'The email does not match the email of your account.',
                        type: 'error'
                    })
                    return
                }

                this.$store.dispatch('deleteAccount')
                    .then(() => this.$router.push('/'))
            }
        },
        computed: {
            token: {
                set() {
                    // Disallow change
                    this.$forceUpdate()
                },
                get() {
                    return this.$store.state.token
                }
            }
        }
    }
</script>