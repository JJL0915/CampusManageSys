<template>
  <section class="stat-card">
    <div class="stat-icon">
      <el-icon><component :is="icon" /></el-icon>
    </div>
    <div>
      <p>{{ label }}</p>
      <strong>{{ value }}</strong>
      <span>{{ trend }}</span>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  value: number | string
  trend: string
  icon: object
}>()
</script>

