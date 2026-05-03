<template>
  <div class="interest-selector">
    <div class="is-selected">
      <span
        v-for="interest in selected"
        :key="interest"
        class="tag is-tag"
        @click="remove(interest)"
        title="Click to remove"
      >{{ interest }} ✕</span>
    </div>
    <div class="is-input-row">
      <input
        v-model="inputVal"
        type="text"
        placeholder="Type an interest and press Enter or +"
        @keydown.enter.prevent="add"
        @keydown.comma.prevent="add"
      />
      <button type="button" class="btn btn-primary btn-sm" @click="add">+</button>
    </div>
    <div v-if="suggestions.length" class="is-suggestions">
      <span
        v-for="s in suggestions"
        :key="s"
        class="tag is-suggest"
        @click="selectSuggestion(s)"
      >{{ s }}</span>
    </div>
    <p class="form-error" v-if="selected.length < 3">Select at least 3 interests</p>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({ modelValue: { type: Array, default: () => [] } })
const emit = defineEmits(['update:modelValue'])

const COMMON_INTERESTS = [
  'hiking','photography','gaming','cooking','travel','music','reading',
  'fitness','art','movies','dancing','yoga','cycling','surfing','coffee',
  'pets','fashion','sports','meditation','foodie'
]

const inputVal = ref('')
const selected = computed(() => props.modelValue)

const suggestions = computed(() => {
  if (!inputVal.value) return []
  const q = inputVal.value.toLowerCase()
  return COMMON_INTERESTS.filter(i => i.includes(q) && !selected.value.includes(i)).slice(0, 6)
})

function add() {
  const val = inputVal.value.trim().toLowerCase()
  if (val && !selected.value.includes(val)) {
    emit('update:modelValue', [...selected.value, val])
  }
  inputVal.value = ''
}

function remove(interest) {
  emit('update:modelValue', selected.value.filter(i => i !== interest))
}

function selectSuggestion(s) {
  if (!selected.value.includes(s)) {
    emit('update:modelValue', [...selected.value, s])
  }
  inputVal.value = ''
}
</script>

<style scoped>
.interest-selector { display: flex; flex-direction: column; gap: 10px; }
.is-selected { display: flex; flex-wrap: wrap; gap: 6px; min-height: 32px; }
.is-tag { cursor: pointer; background: var(--primary); color: #fff; }
.is-tag:hover { background: var(--danger); }
.is-input-row { display: flex; gap: 8px; }
.is-input-row input { flex: 1; }
.is-suggestions { display: flex; flex-wrap: wrap; gap: 6px; }
.is-suggest { cursor: pointer; }
.is-suggest:hover { background: var(--primary); color: #fff; }
</style>
