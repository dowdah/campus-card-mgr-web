<template>
  <transition name="renew">
    <div class="renew">
      <div class="renew-content">
        <p class="renew-title">延期一卡通</p>
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
          <label for="expected_expires_at">预计延期后过期时间:</label>
          <input :value="expectedExpiresTime" id="expected_expires_at" disabled/>
        </div>
        <hr/>
        <p class="renew-title">延期时长</p>
        <div class="editor-row">
          <label for="year">年:</label>
          <input v-model="inputs.year" id="year" type="number"
                 min="0" step="1"/>
        </div>
        <div class="editor-row">
          <label for="month">月:</label>
          <input v-model="inputs.month" id="month" type="number"
                 min="0" step="1"/>
        </div>
        <div class="editor-row">
          <label for="week">周:</label>
          <input v-model="inputs.week" id="week" type="number"
                 min="0" step="1"/>
        </div>
        <div class="editor-row">
          <label for="day">日:</label>
          <input v-model="inputs.day" id="day" type="number"
                 min="0" step="1"/>
        </div>
        <button class="btn-confirm" @click="confirm">确认</button>
        <button class="btn-close" @click="close">取消</button>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  props: {
    card: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      inputs: {
        year: 0,
        month: 0,
        week: 0,
        day: 0
      }
    };
  },
  computed: {
    expectedExpiresTime() {
      const parsedTime = new Date(this.card.expires_at);
      parsedTime.setFullYear(parsedTime.getFullYear() + parseInt(this.inputs.year));
      parsedTime.setMonth(parsedTime.getMonth() + parseInt(this.inputs.month));
      parsedTime.setDate(parsedTime.getDate() + parseInt(this.inputs.week) * 7 + parseInt(this.inputs.day));
      const year = parsedTime.getFullYear();
      const month = String(parsedTime.getMonth() + 1).padStart(2, '0'); // 月份从0开始，需要加1
      const day = String(parsedTime.getDate()).padStart(2, '0');
      const hours = String(parsedTime.getHours()).padStart(2, '0');
      const minutes = String(parsedTime.getMinutes()).padStart(2, '0');
      const seconds = String(parsedTime.getSeconds()).padStart(2, '0');
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    }
  },
  methods: {
    close() {
      this.$emit('close');
    },
    confirm() {
      this.$emit('confirm', this.inputs, this.card.id);
    },
    updateValue(event) {
      this.event.value = parseInt(event.target.value).toString()
    }
  }
};
</script>

<style scoped>
.renew-enter-active,
.renew-leave-active {
  transition: opacity 150ms ease;
}

.renew-enter-from,
.renew-leave-to {
  opacity: 0;
}

.renew {
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

.renew-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 300px;
  text-align: center;
}

.renew-text {
  text-align: left;
}

.renew-title {
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

input[type="number"] {
  padding: 5px;
  border-radius: 5px;
  border: 1px solid #ccc;
  width: 100px;
}

input[type="number"]:focus {
  border-color: #007bff;
  outline: none;
}

.editor-row label {
  width: 80px;
  text-align: right;

}

.editor-row {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  justify-content: center;
  align-items: center;
}
</style>
