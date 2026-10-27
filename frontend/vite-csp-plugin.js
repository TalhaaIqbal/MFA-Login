import crypto from 'crypto';

/**
 * Vite plugin to implement Content Security Policy with nonces
 * This plugin:
 * 1. Generates a random nonce for each build
 * 2. Replaces %VITE_CSP_NONCE% placeholder in index.html CSP meta tag
 * 3. Replaces %VITE_CSP_NONCE% placeholder in script nonce attributes
 */
export function cspNoncePlugin() {
  return {
    name: 'csp-nonce-plugin',
    config() {
      // Generate a random nonce for this build
      const nonce = crypto.randomBytes(16).toString('base64');

      return {
        define: {
          __CSP_NONCE__: JSON.stringify(nonce),
        },
      };
    },
    transformIndexHtml(html) {
      // Generate a new nonce for this request/build
      const nonce = crypto.randomBytes(16).toString('base64');

      // Replace CSP nonce placeholder in meta tag
      html = html.replace(/%VITE_CSP_NONCE%/g, nonce);

      return html;
    },
  };
}
