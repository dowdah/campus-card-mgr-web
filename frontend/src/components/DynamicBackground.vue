<template>
  <div class="dynamic-background"></div>
</template>

<script>
export default {
  name: 'DynamicBackground'
}
</script>

<style scoped>
.dynamic-background {
  position: fixed;
  left: 0;
  top: 0;
  width: 100%;
  height: 100vh; /* 可根据需要调整高度 */
  background: linear-gradient(270deg, #87CEEB, #00CED1, #1E90FF);
  background-size: 600% 600%;
  animation: AnimationName 30s ease infinite;
  z-index: -1;
}

@keyframes AnimationName {
  0%{background-position:0% 50%}
  50%{background-position:100% 50%}
  100%{background-position:0% 50%}
}
</style>