<template>
  <div class="card-editor">
    <form @submit.prevent="handleSubmit" class="editor-form">
      <p class="editor-title">创建一卡通</p>
      <div class="editor-row">
        <label for="user_id">持卡者ID:</label>
        <input :value="user.id" id="user_id" disabled/>
      </div>
      <div class="editor-row">
        <label for="student_id">持卡者学号:</label>
        <input :value="user.student_id" id="student_id" disabled/>
      </div>
      <div class="editor-row">
        <label for="name">持卡者姓名:</label>
        <input :value="user.name" id="name" disabled/>
      </div>
      <div class="editor-row">
        <label for="expires_at">过期时间:</label>
        <input type="date" id="expires_at" v-model="cardData.strings.expiresAt" :min="getToday()" max="2099-12-31"
               class="form-control no-input" :disabled="!hasPermission('RENEW_CARD')">
      </div>
      <div class="editor-row">
        <label for="balance">余额:</label>
        <input v-model="cardData.floats.balance" id="balance"
               :disabled="!hasPermission('CHANGE_CARD_BALANCE')" type="number" min="0" step="0.01"
               @blur="formatBalance"/>
      </div>
      <div class="editor-row">
        <p>是否挂失:</p>
        <div class="radio-group">
          <label for="lost">是</label>
          <input v-model="cardData.booleans.isLost" id="lost" type="radio" value="true"
                 :disabled="!hasPermission('CHANGE_CARD_STATUS')"/>
          <label for="not-lost">否</label>
          <input v-model="cardData.booleans.isLost" id="not-lost" type="radio" value="false"
                 :disabled="!hasPermission('CHANGE_CARD_STATUS')"/>
        </div>
      </div>
      <div class="editor-row">
        <p>是否禁用:</p>
        <div class="radio-group">
          <label for="banned">是</label>
          <input v-model="cardData.booleans.isBanned" id="banned" type="radio" value="true"
                 :disabled="!hasPermission('CHANGE_CARD_STATUS')"/>
          <label for="not-banned">否</label>
          <input v-model="cardData.booleans.isBanned" id="not-banned" type="radio" value="false"
                 :disabled="!hasPermission('CHANGE_CARD_STATUS')"/>
        </div>
      </div>
      <div class="editor-row">
        <button type="submit" class="btn-form">提交</button>
        <button type="button" @click="handleCancel" class="btn-form">取消</button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.card-editor {
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

.editor-title {
  font-size: 20px;
  font-weight: bold;
  text-align: center;
}
</style>

<script>
import {mapGetters} from 'vuex';

export default {
  props: {
    user: {
      type: Object,
      required: true,
    }
  },
  data() {
    return {
      cardData: {
        booleans: {
          isBanned: false,
          isLost: false
        },
        floats: {
          balance: 0.0
        },
        strings: {
          expiresAt: this.getDefaultExpiresAt()
        }
      }
    };
  },
  computed: {
    ...mapGetters(['hasPermission']),
    postPayload() {
      let data = {};
      for (let key in this.cardData.strings) {
        if (this.cardData.strings[key] !== null) {
          data[this.camelToSnake(key)] = this.cardData.strings[key]
        }
      }
      for (let key in this.cardData.booleans) {
        if (this.cardData.booleans[key] !== '') {
          data[this.camelToSnake(key)] = this.cardData.booleans[key] === 'true'
        }
      }
      for (let key in this.cardData.floats) {
        if (this.cardData.floats[key] !== '') {
          data[this.camelToSnake(key)] = parseFloat(this.cardData.floats[key])
        }
      }
      return data;
    }
  },
  methods: {
    handleSubmit() {
      this.$emit('save', this.postPayload, this.user.id);
    },
    handleCancel() {
      this.$emit('cancel');
    },
    formatBalance() {
      // 使用toFixed方法将金额格式化为两位小数
      if (this.cardData.balance < 0) {
        this.cardData.balance = 0;
      }
      this.cardData.balance = parseFloat(this.cardData.balance).toFixed(2);
    },
    camelToSnake(str) {
      return str.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);
    },
    getDefaultExpiresAt() {
      const currentDate = new Date();
      const futureDate = new Date(currentDate.setFullYear(currentDate.getFullYear() + 4));
      const year = futureDate.getFullYear();
      const month = String(futureDate.getMonth() + 1).padStart(2, '0');
      const day = String(futureDate.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    getToday() {
      const today = new Date();
      const year = today.getFullYear();
      const month = today.getMonth() + 1;
      const day = today.getDate() + 1;
      return `${year}-${month < 10 ? '0' + month : month}-${day < 10 ? '0' + day : day}`;
    }
  }
};
</script>
