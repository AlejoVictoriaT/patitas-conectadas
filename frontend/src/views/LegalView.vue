<script setup>
import { computed, onMounted } from 'vue'
import { setPageTitle } from '@/lib/head'

const props = defineProps({
  doc: { type: String, default: 'privacidad' },
})

const esPrivacidad = computed(() => props.doc === 'privacidad')

onMounted(() => setPageTitle(esPrivacidad.value ? 'Política de privacidad' : 'Términos y condiciones'))
</script>

<template>
  <div class="container section legal">
    <!-- ================================ PRIVACIDAD ================================ -->
    <article v-if="esPrivacidad">
      <h1>Política de privacidad</h1>
      <p class="text-muted">Última actualización: agosto de 2026</p>

      <h2>Qué información recogemos</h2>
      <p>
        Para publicar una mascota necesitamos una foto, el tipo de publicación, la ciudad, la fecha
        del evento, la especie, una descripción breve y al menos un medio de contacto. Todo lo demás
        es opcional.
      </p>
      <p>
        Si creas una cuenta guardamos tu nombre, tu correo y el método con el que ingresas
        (contraseña o Google). Nunca almacenamos tu contraseña en texto plano.
      </p>

      <h2>Qué se muestra públicamente</h2>
      <p>
        En la publicación se muestran las fotos, los datos de la mascota, la ciudad, el barrio o
        sector, las fechas y los medios de contacto que decidiste incluir.
      </p>
      <p>
        <strong>La dirección exacta nunca se muestra públicamente.</strong> Solo la ve quien
        administra la publicación. Recomendamos no incluir datos personales innecesarios en la
        descripción.
      </p>

      <h2>Publicaciones como invitado</h2>
      <p>
        Puedes publicar sin cuenta. En ese caso generamos un enlace privado de administración. Ese
        enlace es la única forma de editar la publicación: quien lo tenga puede administrarla, así
        que no lo compartas.
      </p>

      <h2>Cookies y almacenamiento local</h2>
      <p>
        Usamos el almacenamiento del navegador para recordar tu sesión, la ciudad que elegiste y las
        publicaciones que creaste como invitado en ese dispositivo. No usamos cookies publicitarias.
      </p>

      <h2>Tus derechos</h2>
      <p>
        Puedes editar o eliminar tus publicaciones en cualquier momento desde «Mis publicaciones» o
        con tu enlace privado. Si quieres eliminar tu cuenta y los datos asociados, escríbenos desde
        el correo con el que te registraste.
      </p>

      <h2>Seguridad</h2>
      <p>
        Aplicamos validación de formularios, límites de publicación por dispositivo, revisión de
        reportes y ocultamiento automático de publicaciones con múltiples reportes.
      </p>
    </article>

    <!-- ================================= TÉRMINOS ================================= -->
    <article v-else>
      <h1>Términos y condiciones</h1>
      <p class="text-muted">Última actualización: agosto de 2026</p>

      <h2>Qué es esta plataforma</h2>
      <p>
        Patitas Conectadas es un espacio comunitario para publicar y buscar mascotas perdidas,
        encontradas y disponibles para adopción. Es una herramienta de difusión: no intervenimos en
        los acuerdos entre las personas ni garantizamos resultados.
      </p>

      <h2>Uso responsable</h2>
      <p>Al publicar te comprometes a:</p>
      <ul>
        <li>Publicar información veraz y fotos reales de la mascota.</li>
        <li>No usar la plataforma para vender animales.</li>
        <li>No publicar contenido ofensivo, violento o ajeno al propósito del sitio.</li>
        <li>Mantener actualizado el estado de tu publicación cuando el caso se resuelva.</li>
        <li>Respetar la privacidad de las demás personas.</li>
      </ul>

      <h2>Contenido de terceros</h2>
      <p>
        Cada persona es responsable de lo que publica. Cualquier visitante puede reportar una
        publicación; las publicaciones con varios reportes se ocultan automáticamente mientras el
        equipo las revisa, y podemos desactivar o eliminar contenido que incumpla estos términos.
      </p>

      <h2>Adopciones y entregas</h2>
      <p>
        Antes de entregar o recibir una mascota, verifica la identidad de la otra persona y solicita
        pruebas razonables (fotos previas, carné de vacunación, documentos veterinarios). Prefiere
        lugares públicos para los encuentros.
      </p>

      <h2>Disponibilidad del servicio</h2>
      <p>
        Trabajamos para que la plataforma esté siempre disponible, pero puede haber interrupciones
        por mantenimiento o causas técnicas. El servicio se ofrece «tal cual», sin garantías.
      </p>

      <h2>Cambios</h2>
      <p>
        Podemos actualizar estos términos. Publicaremos la nueva versión en esta misma página con su
        fecha de actualización.
      </p>
    </article>
  </div>
</template>

<style scoped>
.legal { max-width: 760px; }
.legal h2 { font-size: 1.15rem; margin-top: 26px; }
.legal ul { padding-left: 20px; color: var(--text-soft); }
.legal li { margin-bottom: 6px; }
.legal p { color: var(--text-soft); }
</style>
