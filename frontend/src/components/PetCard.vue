<script setup>
import { computed } from 'vue'
import StatusBadge from '@/components/StatusBadge.vue'
import { formatShortDate, speciesEmoji, typeMeta } from '@/lib/format'

const props = defineProps({
  post: { type: Object, required: true },
})

const meta = computed(() => typeMeta(props.post.type))
const title = computed(
  () => props.post.pet_name || `${props.post.species_label} ${meta.value.label.toLowerCase()}`,
)
const location = computed(() =>
  [props.post.city, props.post.neighborhood].filter(Boolean).join(' · '),
)
</script>

<template>
  <article class="pet-card card" :class="{ 'is-resolved': post.is_resolved }">
    <router-link :to="post.url" class="photo-link" :aria-label="`Ver la publicación de ${title}`">
      <div class="photo">
        <img
          v-if="post.photo_url"
          :src="post.photo_url"
          :alt="`Foto de ${title}`"
          loading="lazy"
          decoding="async"
        />
        <div v-else class="photo-fallback" aria-hidden="true">🐾</div>
        <span class="type-tag" :class="`badge-${meta.color}`">{{ meta.emoji }} {{ post.type_label }}</span>
      </div>
    </router-link>

    <div class="card-body">
      <h3 class="title">
        <span aria-hidden="true">{{ speciesEmoji(post.species) }}</span>
        <router-link :to="post.url">{{ title }}</router-link>
      </h3>

      <StatusBadge :post="post" />

      <ul class="facts">
        <li><span aria-hidden="true">📍</span> {{ location }}</li>
        <li><span aria-hidden="true">📅</span> {{ formatShortDate(post.event_date) }}</li>
      </ul>

      <router-link class="btn btn-ghost btn-sm btn-block" :to="post.url">Ver publicación</router-link>
    </div>
  </article>
</template>

<style scoped>
.pet-card {
  display: flex;
  flex-direction: column;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.pet-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

.photo-link { display: block; }

.photo {
  position: relative;
  aspect-ratio: 4 / 3;
  background: var(--surface-2);
  overflow: hidden;
}

.photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-fallback {
  display: grid;
  place-items: center;
  height: 100%;
  font-size: 2.5rem;
  opacity: 0.4;
}

.type-tag {
  position: absolute;
  top: 10px;
  left: 10px;
  padding: 4px 10px;
  border-radius: var(--radius-pill);
  font-size: 0.78rem;
  font-weight: 700;
  box-shadow: var(--shadow-sm);
}

.is-resolved .photo img { filter: saturate(0.55); }

.card-body {
  display: grid;
  gap: 8px;
  align-content: start;
  flex: 1;
}

.title {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0;
  font-size: 1.05rem;
}
.title a { color: var(--text); }

.facts {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 3px;
  color: var(--text-soft);
  font-size: 0.9rem;
}

.facts li {
  display: flex;
  gap: 6px;
  align-items: center;
}

.btn-block { margin-top: 4px; }
</style>
