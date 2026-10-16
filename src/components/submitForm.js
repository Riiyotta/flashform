// Spec §7.4: original POSTs FormData to https://formspree.io/f/xyyvopzy (mode: 'no-cors').
// That endpoint belongs to the original site's owner, so the clone does NOT send to it by default.
// Set FORM_ENDPOINT to your own endpoint to enable real submission.
export const FORM_ENDPOINT = null

export const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export async function submitForm(fields, { setAppLoading, pushToast }) {
  setAppLoading(true)
  let ok = true
  try {
    if (FORM_ENDPOINT) {
      const fd = new FormData()
      fd.append('From:', 'Flashform Website')
      Object.entries(fields).forEach(([k, v]) => fd.append(k, v))
      await fetch(FORM_ENDPOINT, { method: 'POST', mode: 'no-cors', body: fd })
    }
  } catch (e) {
    ok = false
  }
  // Spinner hides 400ms after the request finishes.
  await new Promise((r) => setTimeout(r, 400))
  setAppLoading(false)
  pushToast(ok ? 'You have successfully registered for the beta' : 'An error has occurred:(', ok ? 'success' : 'danger')
  return ok
}
