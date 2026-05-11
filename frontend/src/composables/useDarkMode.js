import { ref } from 'vue'

const STORAGE_KEY = 'driftdater-theme'

// Module-level state shared across all component instances
const _isDark = ref(false)

function _apply(dark) {
  _isDark.value = dark
  document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light')
}

function _init() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      _apply(saved === 'dark')
    } else {
      _apply(window.matchMedia('(prefers-color-scheme: dark)').matches)
    }
  } catch {
    _apply(false)
  }
}

// Run once when the module is first imported
_init()

export function useDarkMode() {
  function toggle() {
    const next = !_isDark.value
    _apply(next)
    try { localStorage.setItem(STORAGE_KEY, next ? 'dark' : 'light') } catch {}
  }

  function setTheme(theme) {
    _apply(theme === 'dark')
    try { localStorage.setItem(STORAGE_KEY, theme) } catch {}
  }

  // Return isDark as a readonly alias so components can't accidentally reassign it
  return { isDark: _isDark, toggle, setTheme }
}