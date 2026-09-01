import { defineStore } from 'pinia'
import { createClient } from '@supabase/supabase-js'
import axios from 'axios'
import { ref, computed } from 'vue'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const useAuthStore = defineStore('auth', () => {
  const supabase = createClient(supabaseUrl, supabaseKey)
  const user = ref(null)
  const token = ref(localStorage.getItem('contapp_token') || null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value)

  async function register(email, password, fullName) {
    loading.value = true
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: { data: { full_name: fullName } },
      })
      if (error) throw error
      // Supabase may require email confirmation, so a session is not always available.
      // If a session exists, sync it; otherwise signal that confirmation is needed.
      if (data.session) {
        return await syncSession(data.session)
      }
      return { confirmationRequired: true }
    } finally {
      loading.value = false
    }
  }

  async function login(email, password) {
    loading.value = true
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })
      if (error) throw error
      return await syncSession(data.session)
    } finally {
      loading.value = false
    }
  }

  async function syncSession(session) {
    if (!session) throw new Error('No session available')
    const accessToken = session.access_token
    setToken(accessToken)
    const { data } = await axios.post('/api/auth/profile', {}, {
      headers: { Authorization: `Bearer ${accessToken}` },
    })
    user.value = data
    return data
  }

  async function logout() {
    await supabase.auth.signOut()
    clearSession()
  }

  function setToken(accessToken) {
    token.value = accessToken
    localStorage.setItem('contapp_token', accessToken)
    axios.defaults.headers.common.Authorization = `Bearer ${accessToken}`
  }

  function clearSession() {
    token.value = null
    user.value = null
    localStorage.removeItem('contapp_token')
    delete axios.defaults.headers.common.Authorization
  }

  async function init() {
    const savedToken = localStorage.getItem('contapp_token')
    if (savedToken) {
      token.value = savedToken
      axios.defaults.headers.common.Authorization = `Bearer ${savedToken}`
      try {
        const { data } = await axios.get('/api/auth/me')
        user.value = data
      } catch {
        clearSession()
      }
    }
  }

  return {
    supabase,
    user,
    token,
    loading,
    isAuthenticated,
    register,
    login,
    logout,
    init,
  }
})
