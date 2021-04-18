<template>
    <div class="grid justify-items-center mt-20">
        <div class="grid grid-cols-2 w-full xl:w-256 px-5 xl:px-0 gap-5">
            <div class="bg-gray-dark col-span-2 p-5">
                <div class="text-3xl font-thin text-center">
                    <span class="font-normal">5</span>
                    total clicks in the last 24 hours
                </div>
                <div class="-mb-12">
                    <canvas ref="clicksCanvas"/>
                </div>
            </div>
            <div class="bg-gray-dark p-5 rounded-lg col-span-2 md:col-span-1">
                <div class="text-4xl text-center font-thin">Browser</div>
                <div class="-mb-12">
                    <canvas ref="browserCanvas"/>
                </div>
            </div>
            <div class="bg-gray-dark p-5 rounded-lg col-span-2 md:col-span-1">
                <div class="text-4xl text-center font-thin">Operating System</div>
                <div class="-mb-12">
                    <canvas ref="osCanvas"/>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import Chart from 'chart.js/auto';

    const chartColors = ['#009fb7', '#ff7c43', '#f95d6a', '#d45087', '#a05195']

    export default {
        data() {
            return {
                browser: null,
                os: null,
                clicks: null
            }
        },
        created() {
            this.$store.dispatch('getStats', {id: this.$route.params.id, period: 'day'})
                .then(data => {
                    this.browser = data.browser
                    this.os = data.os

                    this.updateCharts()
                })
        },
        methods: {
            updateCharts() {
                new Chart(this.$refs.browserCanvas, {
                    type: 'doughnut',
                    data: {
                        labels: Object.keys(this.browser),
                        datasets: [
                            {
                                label: 'Dataset 1',
                                data: Object.values(this.browser),
                                borderColor: '#1c1c2f',
                                backgroundColor: chartColors
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'left',
                                labels: {
                                    color: '#fff',
                                    font: {
                                        size: 14
                                    }
                                }
                            }
                        }
                    }
                })

                new Chart(this.$refs.osCanvas, {
                    type: 'doughnut',
                    data: {
                        labels: Object.keys(this.os),
                        datasets: [
                            {
                                label: 'Dataset 1',
                                data: Object.values(this.os),
                                borderColor: '#1c1c2f',
                                backgroundColor: chartColors,
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'left',
                                labels: {
                                    color: '#fff',
                                    font: {
                                        size: 14
                                    }
                                }
                            }
                        }
                    }
                })
            }
        }
    }
</script>