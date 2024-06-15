<template>
  <modal-window :show-modal="lostCardData.showModalWindow" @close="clearLostCardData"
                @confirm="reportLost(lostCardData.card.id)">
    确定要报告此卡(卡号: {{ lostCardData.card.id }})丢失吗？
  </modal-window>
  <div class="cards">
    <h2>我的一卡通及交易</h2>
    <div v-if="isLoading" class="alert alert-info">加载中...</div>
    <div v-else-if="error" class="alert alert-danger">{{ error.message }}</div>
    <div v-else>
      <div v-for="(card, index) in cards" :key="index" class="card">
        <CardInfo :card="card" @toggleCardDetails="toggleCardDetails"
                  :showDetails="collapsedCardIds.includes(card.id)"
                  @reportLost="showLostModal(card)"
        ></CardInfo>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cards {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  align-items: stretch;
  max-width: 700px;
  margin: 0 auto;
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

.modal-button {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  background-color: #007BFF;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s;
  margin: 10px 10px 0 10px;
}

.modal-button:hover {
  background-color: #0056b3;
}

.v-enter-active,
.v-leave-active {
  transition: opacity 150ms ease;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
}
</style>

<script>
import CardInfo from '../components/CardInfo.vue';
import ModalWindow from "../components/ModalWindow.vue";
import {mapGetters, mapActions, mapState, mapMutations} from 'vuex';
import {BASE_API_URL} from '@/config/constants';
import axios from 'axios';

export default {
  name: 'Cards',
  components: {ModalWindow, CardInfo},
  data() {
    return {
      loading: false,
      error: null,
      collapsedCardIds: [],
      lostCardData: {
        card: null,
        responseData: null,
        failed: false,
        showModalWindow: false
      }
    };
  },
  computed: {
    ...mapState(['isLoading']),
    ...mapGetters(['cards'])
  },
  methods: {
    ...mapActions(['setLoading', 'init']),
    ...mapMutations(['setCardLost']),
    async reportLost(cardId) {
      this.clearLostCardData()
      this.setLoading(true)
      try {
        const response = await axios.get(`${BASE_API_URL}/card/my/lost/${cardId}`);
        this.setCardLost(cardId);
        this.lostCardData.responseData = response.data;
        this.lostCardData.failed = false;
      } catch (error) {
        this.error = error.response.data;
        this.lostCardData.failed = true;
      } finally {
        this.setLoading(false)
      }
    },
    async toggleCardDetails(cardId) {
      if (this.collapsedCardIds.includes(cardId)) {
        this.collapsedCardIds = this.collapsedCardIds.filter(id => id !== cardId);
      } else {
        this.collapsedCardIds.push(cardId);
      }
    },
    showLostModal(card) {
      this.lostCardData.card = card;
      this.lostCardData.showModalWindow = true;
    },
    clearLostCardData() {
      this.lostCardData.card = null;
      this.lostCardData.showModalWindow = false;
    }
  }
};
</script>
