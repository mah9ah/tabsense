import { contextBridge, ipcRenderer } from 'electron'

// Expose a minimal, typed API to the renderer — never expose ipcRenderer directly
contextBridge.exposeInMainWorld('tabsense', {
  showNotification: (title: string, body: string) =>
    ipcRenderer.invoke('show-notification', title, body),
  getBackendUrl: () =>
    ipcRenderer.invoke('get-backend-url'),
})
