<template>
  <div class="container">
    <div class="dice-section">
      <h2>Dice</h2>
      <div class="dice">
        <template v-if="isRolling">
          <div class="rolling">Rolling</div>
        </template>
        <template v-else>
          <div v-for="(die, index) in dice" :key="index" class="die">
            <template v-if="die === -1">
              <span class="question-mark">?</span>
            </template>
            <template v-else>
              <img :src="getDiceImage(die)" :alt="`Dice showing ${die}`" />
            </template>
          </div>
        </template>
      </div>
    </div>
    <div class="bottom-section">
      <div class="prices-section">
        <h3>Prices</h3>
        <ul>
          <li :class="{ highlight: result === 'Pair' }">Pair <span>x2</span></li>
          <li :class="{ highlight: result === 'Full house' }">Full house <span>x3</span></li>
          <li :class="{ highlight: result === 'Balut' }">Balut <span>x4</span></li>
          <li :class="{ highlight: result === 'Straight' }">Straight <span>x5</span></li>
          <li :class="{ highlight: result === 'Other' }">Other <span>x0</span></li>
        </ul>
      </div>
      <div class="betting-section">
        <div class="bet-section">
          <h3>Bet</h3>
          <div class="bet-amount">
            <input type="number" v-model.number="bet" min="1" :max="balance" :disabled="isRolling || isProcessing">
            <button class="roll-btn" @click="rollDice"
              :disabled="isRolling || isProcessing || insufficientFunds">ROLL</button>
          </div>
          <div v-if="insufficientFunds" class="warning-message">
            {{ warningMessage }}
          </div>
        </div>
        <div class="balance-section">
          <h3>Your balance</h3>
          <p>{{ balance }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import dice1 from '@/assets/dice-1.svg';
import dice2 from '@/assets/dice-2.svg';
import dice3 from '@/assets/dice-3.svg';
import dice4 from '@/assets/dice-4.svg';
import dice5 from '@/assets/dice-5.svg';
import dice6 from '@/assets/dice-6.svg';

export default {
  name: 'DiceGame',
  setup() {
    const dice = ref([-1, -1, -1, -1, -1]);
    const bet = ref(30);
    const balance = ref(0);
    const isRolling = ref(false);
    const isProcessing = ref(false);
    const result = ref('');

    const diceImages = {
      1: dice1,
      2: dice2,
      3: dice3,
      4: dice4,
      5: dice5,
      6: dice6,
    };

    const insufficientFunds = computed(() => {
      return balance.value <= 0 || bet.value > balance.value;
    });

    const warningMessage = computed(() => {
      if (balance.value <= 0) {
        return "Insufficient funds. To play, fund your account.";
      } else if (bet.value > balance.value) {
        return `Insufficient funds. Maximum bet: ${balance.value}`;
      }
      return "";
    });

    const getDiceImage = (dieValue) => {
      return diceImages[dieValue];
    };

    const determineResult = (diceValues) => {
      const counts = diceValues.reduce((acc, val) => {
        acc[val] = (acc[val] || 0) + 1;
        return acc;
      }, {});

      const uniqueValues = Object.keys(counts).length;
      const maxCount = Math.max(...Object.values(counts));

      if (uniqueValues === 1) return 'Balut';
      if (uniqueValues === 5 && (!counts[1] || !counts[6])) return 'Straight';
      if (uniqueValues === 2 && (maxCount === 3 || maxCount === 2)) return 'Full house';
      if (maxCount === 2) return 'Pair';
      return 'Other';
    };

    const getMultiplier = (result) => {
      const multipliers = {
        'Pair': 2,
        'Full house': 3,
        'Balut': 4,
        'Straight': 5,
        'Other': 0
      };
      return multipliers[result] || 0;
    };

    const sendTransaction = async (amount, transactionType) => {
      try {
        const response = await axios.post('http://localhost:8000/transactions/', {
          amount,
          transaction_type: transactionType
        });
      } catch (error) {
        console.error(`Error sending ${transactionType} transaction:`, error);
        throw error;
      }
    };

    const fetchBalance = async () => {
      try {
        const response = await axios.get('http://localhost:8000/balance/');
        balance.value = response.data.balance;
      } catch (error) {
        console.error('Error fetching balance:', error);
        throw error;
      }
    };

    const rollDice = async () => {
      if (insufficientFunds.value) return;

      isRolling.value = true;
      isProcessing.value = true;
      result.value = '';

      try {
        await sendTransaction(-bet.value, 'bet');
        await fetchBalance();
        await new Promise(resolve => setTimeout(resolve, 2000));

        dice.value = dice.value.map(() => Math.floor(Math.random() * 6) + 1);
        result.value = determineResult(dice.value);

        const multiplier = getMultiplier(result.value);
        const winnings = bet.value * multiplier;

        await sendTransaction(winnings, 'win');

        await fetchBalance();

      } catch (error) {
        console.error('Error during dice roll:', error);
      } finally {
        isRolling.value = false;
        isProcessing.value = false;
      }
    };

    onMounted(async () => {
      isProcessing.value = true;
      try {
        await fetchBalance();
      } catch (error) {
        console.error('Error fetching initial balance:', error);
      } finally {
        isProcessing.value = false;
      }
    });

    return {
      dice,
      bet,
      balance,
      isRolling,
      isProcessing,
      result,
      rollDice,
      getDiceImage,
      insufficientFunds,
      warningMessage
    };
  },
};
</script>
