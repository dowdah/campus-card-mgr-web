<template>
  <transition name="alert">
    <div v-if="showAlert" class="alert-window">
      <div class="alert-content">
        <p class="alert-title" v-if="title">{{ title }}</p>
        <p class="alert-text"><slot></slot></p>
        <button class="btn-confirm" @click="confirm">{{ confirmBtnText }}</button>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  props: {
    showAlert: {
      type: Boolean,
      required: true
    },
    title: {
      type: String,
      default: null
    },
    confirmBtnText: {
      type: String,
      default: '确定'
    }
  },
  methods: {
    confirm() {
      this.$emit('confirm');
    }
  }
};
</script>

<style scoped>
.alert-enter-active,
.alert-leave-active {
  transition: opacity 150ms ease;
}

.alert-enter-from,
.alert-leave-to {
  opacity: 0;
}

.alert-window {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1001;
}

.alert-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 300px;
  text-align: center;
}

.alert-text {
  text-align: left;
}

.alert-title {
  text-align: center;
  font-size: 20px;
  margin-bottom: 10px;
  font-weight: bold;
}

.btn-confirm {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  background-color: #007BFF;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s;
  margin: 10px 10px 0 10px;
}

.btn-confirm:hover {
  background-color: #0056b3;
}
</style>
