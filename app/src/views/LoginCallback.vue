<template>
    <div class="my-20 sm:mt-32 px-3">
        <div class="text-center">
            <div v-if="success">
                <div class="text-5xl mb-3">You are now logged in!</div>
                <div class="font-thin tracking-wider text-lg mb-10">You will be redirected to the settings page</div>
                <div class="text-8xl text-gray-400">
                    <i class="far fa-check-circle"/>
                </div>
            </div>
            <div v-else-if="error">
                <div class="text-5xl mb-3">Something went wrong ...</div>
                <div class="font-thin tracking-wider text-lg mb-10">You will be redirected back to the login page</div>
                <div class="text-8xl text-gray-400">
                    <i class="far fa-times-circle"/>
                </div>
            </div>
            <div v-else>
                <div class="text-5xl mb-3">Logging you in ...</div>
                <div class="font-thin tracking-wider text-lg mb-10">This shouldn't take longer than a few seconds</div>
                <div class="text-8xl animate-spin-slow text-gray-400">
                    <i class="fas fa-spinner"/>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                success: false,
                error: false,
            }
        },
        created() {
            const code = this.$route.query.code
            const platform = this.$route.params.platform
            if (!code) {
                this.$router.push('/login')
            }

            this.$store.dispatch('loginWithCode', {code: code, platform: platform})
                .then(() => {
                    this.success = true
                    setTimeout(() => this.$router.push('/settings'), 2000)
                })
                .catch(() => {
                    this.error = true
                    setTimeout(() => this.$router.push('/login'), 2000)
                })
        }
    }
</script>