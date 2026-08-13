/**
 * Redimensiona y comprime la foto en el navegador antes de subirla.
 * Así una foto de 6 MB tomada con el celular viaja como ~300 KB.
 */

const MAX_SIDE = 1600
const QUALITY = 0.82

function loadImage(file) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file)
    const img = new Image()
    img.onload = () => {
      URL.revokeObjectURL(url)
      resolve(img)
    }
    img.onerror = () => {
      URL.revokeObjectURL(url)
      reject(new Error('No pudimos leer la imagen.'))
    }
    img.src = url
  })
}

export async function compressImage(file) {
  // Los formatos que el canvas no sabe decodificar (por ejemplo HEIC en algunos
  // navegadores) se envían tal cual y los procesa el servidor.
  if (!/^image\/(jpeg|jpg|png|webp)$/i.test(file.type)) return file

  let img
  try {
    img = await loadImage(file)
  } catch {
    return file
  }

  const scale = Math.min(1, MAX_SIDE / Math.max(img.width, img.height))
  if (scale === 1 && file.size < 900 * 1024) return file

  const canvas = document.createElement('canvas')
  canvas.width = Math.round(img.width * scale)
  canvas.height = Math.round(img.height * scale)

  const ctx = canvas.getContext('2d')
  ctx.drawImage(img, 0, 0, canvas.width, canvas.height)

  const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', QUALITY))
  if (!blob || blob.size >= file.size) return file

  return new File([blob], file.name.replace(/\.[^.]+$/, '') + '.jpg', {
    type: 'image/jpeg',
    lastModified: Date.now(),
  })
}
