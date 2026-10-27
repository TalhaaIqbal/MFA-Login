// Development-only logging utility
const isDev = import.meta.env.DEV

const logger = {
  log: (...args) => {
    if (isDev) {
      console.log(...args)
    }
  },
  error: (...args) => {
    if (isDev) {
      console.error(...args)
    }
  },
  warn: (...args) => {
    if (isDev) {
      console.warn(...args)
    }
  }
}

export default logger
