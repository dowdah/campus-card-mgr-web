<template>
  <div class="transaction-editor">
    <form @submit.prevent="handleSubmit" class="editor-form">
      <div class="editor-row">
        <p>你正在修改ID为{{ transaction.id }}的交易备注。</p>
      </div>
      <div class="editor-row">
        <label for="comments">备注:</label>
        <textarea v-model="transactionData.comments" id="comments"></textarea>
      </div>
      <div class="editor-row">
        <button type="submit" class="btn-submit">保存</button>
        <button type="button" @click="handleCancel" class="btn-submit">取消</button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.transaction-editor {
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

.btn-submit {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  background-color: #007BFF;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-submit:hover {
  background-color: #0056b3;
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
</style>

<script>
export default {
  props: {
    transaction: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      transactionData: {
        comments: this.transaction.comments
      },
    };
  },
  methods: {
    handleSubmit() {
      this.$emit('save', this.transactionData, this.transaction.id);
    },
    handleCancel() {
      this.$emit('cancel');
    },
  }
};
</script>
