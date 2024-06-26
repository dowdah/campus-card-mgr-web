<template>
  <div class="card-editor">
    <form @submit.prevent="handleSubmit" class="editor-form">
      <p class="editor-title">修改卡片状态</p>
      <div class="editor-row">
        <label for="name">持卡者姓名:</label>
        <input :value="card.user.name" id="name" disabled/>
      </div>
      <div class="editor-row">
        <label for="student_id">持卡者学号:</label>
        <input :value="card.user.student_id" id="student_id" disabled/>
      </div>
      <div class="editor-row">
        <label for="id">卡号:</label>
        <input :value="card.id" id="id" disabled/>
      </div>
      <div class="editor-row">
        <label for="created_at">创建时间:</label>
        <input :value="card.created_at" id="created_at" disabled/>
      </div>
      <div class="editor-row">
        <label for="expires_at">过期时间:</label>
        <input :value="card.expires_at" id="expires_at" disabled/>
      </div>
      <div class="editor-row">
        <label for="balance">余额:</label>
        <input v-model="cardData.balance" id="balance" v-if="hasPermission('CHANGE_CARD_BALANCE')" type="number"
               min="0" step="0.01" @blur="formatBalance"/>
        <input :value="card.balance" id="balance" disabled v-else/>
      </div>
      <div class="editor-row">
        <p>是否挂失:</p>
        <div class="radio-group">
          <label for="lost">是</label>
          <input v-model="cardData.isLost" id="lost" type="radio" value="true"
                 v-if="hasPermission('CHANGE_CARD_STATUS')"/>
          <input :value="card.is_lost" id="lost" type="radio" disabled v-else/>
          <label for="not-lost">否</label>
          <input v-model="cardData.isLost" id="not-lost" type="radio" value="false"
                 v-if="hasPermission('CHANGE_CARD_STATUS')"/>
          <input :value="!card.is_lost" id="not-lost" type="radio" disabled v-else/>
        </div>
      </div>
      <div class="editor-row">
        <p>是否禁用:</p>
        <div class="radio-group">
          <label for="banned">是</label>
          <input v-model="cardData.isBanned" id="banned" type="radio" value="true"
                 v-if="hasPermission('CHANGE_CARD_STATUS')"/>
          <input :value="card.is_banned" id="banned" type="radio" disabled v-else/>
          <label for="not-banned">否</label>
          <input v-model="cardData.isBanned" id="not-banned" type="radio" value="false"
                 v-if="hasPermission('CHANGE_CARD_STATUS')"/>
          <input :value="!card.is_banned" id="not-banned" type="radio" disabled v-else/>
        </div>
      </div>
      <div class="editor-row">
        <button type="submit" class="btn-form">保存</button>
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
    card: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      cardData: {
        isBanned: this.card.is_banned,
        isLost: this.card.is_lost,
        balance: this.card.balance
      }
    };
  },
  computed: {
    ...mapGetters(['hasPermission']),
    postPayload() {
      let payload = {}
      if (this.hasPermission('CHANGE_CARD_STATUS')) {
        if (typeof this.cardData.isBanned === 'string') {
          payload.is_banned = this.cardData.isBanned === 'true'
        }
        if (typeof this.cardData.isLost === 'string') {
          payload.is_lost = this.cardData.isLost === 'true'
        }
      }
      if (this.hasPermission('CHANGE_CARD_BALANCE')) {
        payload.balance = parseFloat(this.cardData.balance)
      }
      return payload
    }
  },
  methods: {
    handleSubmit() {
      this.$emit('save', this.postPayload, this.card.id);
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
    }
  },
  created() {
    console.log(this.cardData)
  }
};
</script>
