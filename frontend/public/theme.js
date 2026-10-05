// Executado antes da renderização para evitar um clarão ao abrir no tema escuro.
(() => {
  let preference = 'system';
  try {
    const saved = localStorage.getItem('codetrack.theme');
    if (saved === 'light' || saved === 'dark') preference = saved;
  } catch { /* A interface também funciona com armazenamento bloqueado. */ }
  const dark = preference === 'dark' || (preference === 'system' && matchMedia('(prefers-color-scheme: dark)').matches);
  document.documentElement.dataset.theme = dark ? 'dark' : 'light';
  document.documentElement.style.colorScheme = dark ? 'dark' : 'light';
  document.documentElement.dataset.themePreference = preference;
})();
