<script setup>
import { nextTick, ref, watch } from 'vue'
import AppModal from '@/components/AppModal.vue'
import { api } from '@/api/client'

const props = defineProps({
  /** { country, region, city } o null */
  modelValue: { type: Object, default: null },
  label: { type: String, default: 'Ciudad' },
  placeholder: { type: String, default: 'Selecciona tu ciudad' },
  invalid: { type: Boolean, default: false },
  allowClear: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue'])

const open = ref(false)
const term = ref('')
const results = ref([])
const loading = ref(false)
const countries = ref([])
const country = ref(props.modelValue?.country || 'Colombia')
const searchInput = ref(null)
let timer = null

async function loadCountries() {
  if (countries.value.length) return
  try {
    const data = await api.countries()
    countries.value = data.items
    country.value = props.modelValue?.country || data.default
  } catch {
    countries.value = ['Colombia']
  }
}

async function search() {
  loading.value = true
  try {
    results.value = await api.searchCities(term.value, country.value)
  } catch {
    results.value = []
  } finally {
    loading.value = false
  }
}

watch(term, () => {
  clearTimeout(timer)
  timer = setTimeout(search, 220)
})

watch(country, search)

async function openPicker() {
  open.value = true
  term.value = ''
  await loadCountries()
  await search()
  await nextTick()
  searchInput.value?.focus()
}

function choose(option) {
  emit('update:modelValue', { country: option.country, region: option.region, city: option.city })
  open.value = false
}

function useTyped() {
  const city = term.value.trim()
  if (city.length < 2) return
  emit('update:modelValue', { country: country.value, region: null, city })
  open.value = false
}

function clear() {
  emit('update:modelValue', null)
}
</script>

<template>
  <div class="city-select">
    <button
      type="button"
      class="city-trigger"
      :class="{ 'is-invalid': invalid, 'is-empty': !modelValue }"
      @click="openPicker"
    >
      <span class="pin" aria-hidden="true">📍</span>
      <span class="value">
        <template v-if="modelValue">
          {{ modelValue.city }}<span v-if="modelValue.region" class="region">, {{ modelValue.region }}</span>
        </template>
        <template v-else>{{ placeholder }}</template>
      </span>
      <span class="chev" aria-hidden="true">▾</span>
    </button>

    <button v-if="allowClear && modelValue" type="button" class="btn btn-quiet btn-sm" @click="clear">
      Quitar filtro de ciudad
    </button>

    <AppModal v-if="open" :title="label" @close="open = false">
      <div class="field">
        <label class="label" for="city-search">Escribe el nombre de tu ciudad</label>
        <input
          id="city-search"
          ref="searchInput"
          v-model="term"
          class="input"
          type="search"
          autocomplete="off"
          placeholder="Ej.: Manizales"
        />
      </div>

      <div v-if="countries.length > 1" class="field">
        <label class="label" for="city-country">País</label>
        <select id="city-country" v-model="country" class="select">
          <option v-for="item in countries" :key="item" :value="item">{{ item }}</option>
        </select>
      </div>

      <p v-if="loading" class="text-muted">Buscando…</p>

      <ul v-else-if="results.length" class="results">
        <li v-for="option in results" :key="`${option.region}-${option.city}`">
          <button type="button" @click="choose(option)">
            <strong>{{ option.city }}</strong>
            <small>{{ option.region }}, {{ option.country }}</small>
          </button>
        </li>
      </ul>

      <div v-else class="no-results">
        <p class="text-soft">No encontramos esa ciudad en la lista.</p>
        <button
          v-if="term.trim().length >= 2"
          type="button"
          class="btn btn-primary btn-block"
          @click="useTyped"
        >
          Usar «{{ term.trim() }}»
        </button>
      </div>
    </AppModal>
  </div>
</template>

<style scoped>
.city-select { display: grid; gap: 6px; }

.city-trigger {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  min-height: var(--tap);
  padding: 12px 14px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius);
  background: var(--surface);
  font-size: 1rem;
  text-align: left;
  cursor: pointer;
  color: var(--text);
}

.city-trigger.is-empty .value { color: var(--text-muted); }
.city-trigger.is-invalid { border-color: var(--danger); box-shadow: 0 0 0 3px #fde3e1; }

.value { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-weight: 600; }
.region { font-weight: 400; color: var(--text-soft); }
.chev { color: var(--text-muted); }

.results {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 4px;
  /* `dvh` para que el listado no quede debajo del teclado del celular, que es
     lo que hacía imposible elegir la ciudad al escribirla. */
  max-height: 46vh;
  max-height: 46dvh;
  overflow-y: auto;
  overscroll-behavior: contain;
}

.results button {
  display: grid;
  gap: 1px;
  width: 100%;
  text-align: left;
  padding: 11px 12px;
  border: none;
  border-radius: var(--radius-sm);
  background: none;
  cursor: pointer;
  min-height: var(--tap);
}
.results button:hover { background: var(--brand-light); }
.results small { color: var(--text-soft); }

.no-results { display: grid; gap: 10px; }
</style>
