<template>
  <transition name="modal">
    <div v-if="showModal" class="modal">
      <div class="modal-content">
        <p class="modal-title" v-if="title">{{ title }}</p>
        <p class="modal-text"><slot></slot></p>
        <button class="btn-confirm" @click="confirm">{{ confirmBtnText }}</button>
        <button class="btn-close" @click="close">{{ closeBtnText }}</button>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  props: {
    showModal: {
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
    },
    closeBtnText: {
      type: String,
      default: '取消'
    }
  },
  methods: {
    close() {
      this.$emit('close');
    },
    confirm() {
      this.$emit('confirm');
    }
  }
};
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 150ms ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal {
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

.modal-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 300px;
  text-align: center;
}

.modal-text {
  text-align: left;
}

.modal-title {
  text-align: center;
  font-size: 20px;
  margin-bottom: 10px;
  font-weight: bold;
}

button {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  background-color: #007BFF;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s;
  margin: 10px 10px 0 10px;
}

button:hover {
  background-color: #0056b3;
}

.btn-confirm {
  background-color: #dc3545;
}

.btn-confirm:hover {
  background-color: #c82333;
}
</style>