<template>
  <div class="user-editor">
    <form @submit.prevent="handleSubmit" class="editor-form">
      <p class="editor-title">创建新用户</p>
      <div class="editor-row">
        <label for="name">姓名:</label>
        <input v-model="userData.name" id="name" required/>
      </div>
      <div class="editor-row">
        <label for="student_id">学号:</label>
        <input v-model="userData.student_id" id="student_id" required/>
      </div>
      <div class="editor-row">
        <label for="email">邮箱:</label>
        <input v-model="userData.email" id="email" type="email" required/>
      </div>
      <div class="editor-row">
        <p>已验证邮箱:</p>
        <div class="radio-group">
          <label for="confirmed">是</label>
          <input v-model="userData.confirmed" id="confirmed" type="radio" value="true"/>
          <label for="unconfirmed">否</label>
          <input v-model="userData.confirmed" id="unconfirmed" type="radio" value="false"/>
        </div>
      </div>
      <div class="editor-row">
        <label for="comments">备注:</label>
        <textarea v-model="userData.comments" id="comments"></textarea>
      </div>
      <div class="editor-row">
        <button type="submit" class="btn-form" :disabled="notReadyForSubmit">提交</button>
        <button type="button" @click="handleCancel" class="btn-form">取消</button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.user-editor {
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

.editor-form {
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.editor-row {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  justify-content: center;
  align-items: center;
}

label {
  width: 80px;
  text-align: right;
}

input {
  padding: 5px;
  border-radius: 5px;
  border: 1px solid #ccc;
  width: 200px;
}

input:focus {
  border-color: #007bff;
  outline: none;
}

.btn-form {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  background-color: #007BFF;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-form:hover {
  background-color: #0056b3;
}

.btn-form:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.btn-form:disabled:hover {
  background-color: #ccc;
}

.radio-group {
  display: flex;
  align-items: center;
}

.radio-group label {
  margin-right: 5px;
  width: min-content;
}

.radio-group input {
  width: min-content;
}

#comments {
  width: 200px;
  height: 100px;
}

.editor-title {
  font-size: 20px;
  font-weight: bold;
  text-align: center;
}
</style>

<script>
export default {
  emits: ['submit', 'cancel'],
  data() {
    return {
      userData: {
        name: '',
        student_id: '',
        email: '',
        confirmed: true,
        comments: ''
      },
    };
  },
  methods: {
    handleSubmit() {
      if (this.notReadyForSubmit) {
        return;
      }
      if (typeof this.userData.confirmed === 'string') {
        this.userData.confirmed = this.userData.confirmed === 'true';
      }
      console.log(this.userData);
      this.$emit('submit', this.userData);
    },
    handleCancel() {
      this.$emit('cancel');
    },
  },
  computed: {
    notReadyForSubmit() {
      return this.userData.name === '' || this.userData.student_id === '' || this.userData.email === '';
    }
  }
};
</script>
