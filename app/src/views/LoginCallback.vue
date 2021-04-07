<template>
    <div></div>
</template>

<script>
    export default {
        created() {
            const code = this.$route.query.code
            const platform = this.$route.params.platform
            if (!code) {
                this.$router.push('/login')
            }

            if (platform === 'discord') {
                this.$store.dispatch('loginWithDiscord', {code: code})
                    .then(() => {
                        setTimeout(() => this.$router.push('/settings'), 2000)
                    })
            } else {
                this.$router.push('/login')
            }
        }
    }
</script>