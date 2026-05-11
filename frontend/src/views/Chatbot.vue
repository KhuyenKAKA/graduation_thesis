<template>
  <div class="chatbot-wrapper">
    <Header />

    <div class="chatbot-layout">
      <!-- Sidebar -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <span class="sidebar-title">Chat History</span>
          <button class="btn-new-chat" @click="startNewChat" title="New chat">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
          </button>
        </div>

        <div class="history-list">
          <div
            v-for="(session, i) in chatHistory"
            :key="session.id"
            :class="['history-item', { active: activeSessionId === session.id }]"
            @click="switchSession(session)"
          >
            <svg class="history-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
            <span class="history-text">{{ session.title }}</span>
            <button class="btn-del-session" @click="deleteSession(session, $event)" title="Delete">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
          <div v-if="chatHistory.length === 0" class="history-empty">No chat history yet</div>
        </div>
      </aside>

      <!-- Main Chat Area -->
      <div class="chat-main">
        <!-- Chat header -->
        <div class="chat-topbar">
          <div class="chat-topbar-left">
            <img src="/assets/bot_avatar.jpg" class="topbar-avatar" alt="Bot" />
            <div>
              <div class="topbar-name">UniCompare Assistant</div>
              <div class="topbar-status">
                <span class="status-dot"></span>
                Active now
              </div>
            </div>
          </div>
          <button class="btn-clear" @click="clearChat" title="Clear conversation">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
              <path d="M10 11v6M14 11v6"/>
              <path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
            </svg>
            Clear
          </button>
        </div>

        <!-- Messages -->
        <div class="messages-area" ref="messagesArea">
          <!-- Welcome state -->
          <div v-if="messages.length === 0" class="welcome-state">
            <img src="/assets/bot_avatar.jpg" class="welcome-avatar" alt="Bot" />
            <h2 class="welcome-title">Hello! I'm UniCompare Assistant</h2>
            <p class="welcome-sub">Ask me anything about universities, admission requirements, scholarships and more.</p>
            <div class="suggestion-chips">
              <button
                v-for="s in suggestions"
                :key="s"
                class="chip"
                @click="sendSuggestion(s)"
              >{{ s }}</button>
            </div>
          </div>

          <!-- Message bubbles -->
          <template v-else>
            <div
              v-for="msg in messages"
              :key="msg.id"
              :class="['message-row', msg.role === 'user' ? 'user-row' : 'bot-row']"
            >
              <img
                v-if="msg.role === 'bot'"
                src="/assets/bot_avatar.jpg"
                class="msg-avatar"
                alt="Bot"
              />
              <div :class="['bubble', msg.role === 'user' ? 'bubble-user' : 'bubble-bot']">
                <span class="bubble-text" v-html="formatText(msg.content)"></span>
                <span class="bubble-time">{{ msg.time }}</span>
                <!-- Search Online button — shown when DB data is insufficient -->
                <button
                  v-if="msg.showSearchBtn"
                  class="btn-search-online"
                  @click="performOnlineSearch(msg)"
                >
                  🔍 Search Online
                </button>
              </div>
            </div>

            <!-- Typing indicator — only shown while waiting for first chunk -->
            <div v-if="isTyping && !isStreaming" class="message-row bot-row">
              <img src="/assets/bot_avatar.jpg" class="msg-avatar" alt="Bot" />
              <div class="bubble bubble-bot typing-bubble">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
              </div>
            </div>
          </template>
        </div>

        <!-- Input area -->
        <div class="input-area">
          <div class="input-wrap">
            <textarea
              ref="inputRef"
              v-model="inputText"
              class="chat-input"
              placeholder="Type your message..."
              rows="1"
              @keydown.enter.exact.prevent="sendMessage"
              @keydown.enter.shift.exact="() => {}"
              @input="autoResize"
            />
            <button
              class="btn-send"
              :disabled="!inputText.trim() || isTyping"
              @click="sendMessage"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                <line x1="22" y1="2" x2="11" y2="13"/>
                <polygon points="22 2 15 22 11 13 2 9 22 2"/>
              </svg>
            </button>
          </div>
          <div class="input-hint">Press <kbd>Enter</kbd> to send · <kbd>Shift+Enter</kbd> for new line</div>
        </div>
      </div>
    </div>

    <Footer />
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import { chatbotAPI } from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const API_BASE_URL = 'http://localhost:8000/api'

// ── State ──────────────────────────────────────────────
const messages        = ref([])
const inputText       = ref('')
const isTyping        = ref(false)
const isStreaming     = ref(false)   // true once first SSE chunk arrives
const messagesArea    = ref(null)
const inputRef        = ref(null)
const chatHistory     = ref([])
const activeSessionId = ref(null)

let msgIdCounter = 1

const SESSION_KEY = 'chatbot_session_id'

const suggestions = [
  'Top 10 universities in the United States?',
  'What is the IELTS requirement for MIT?',
  'Compare Harvard vs Oxford',
  'Entry requirements for universities in Australia',
  'What scholarships does Stanford offer?'
]

// ── Helpers ─────────────────────────────────────────────
const now = () => {
  const d = new Date()
  return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesArea.value) {
    messagesArea.value.scrollTop = messagesArea.value.scrollHeight
  }
}

const autoResize = () => {
  const el = inputRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 140) + 'px'
}

const formatText = (text) => {
  if (!text) return ''
  // Escape HTML first, then apply markdown
  let escaped = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  // Stash Unicode box-drawing blocks (tables + ═══/─── dividers) so their
  // internal newlines are NOT converted to <br/> and alignment is preserved.
  const preBlocks = []
  escaped = escaped.replace(
    /((?:[ \t]*[\u250c\u2502\u251c\u2514\u2550\u2500\u2510\u2518\u2524\u252c\u253c][^\n]*(?:\n|$))+)/g,
    (match) => {
      preBlocks.push(`<pre class="box-table">${match.trimEnd()}</pre>`)
      return `\x00PRE${preBlocks.length - 1}\x00`
    }
  )

  // Markdown: pipe tables (fallback — only if AI still outputs them)
  escaped = escaped.replace(
    /\|(.+)\|\n\|[-| :]+\|\n((?:\|.+\|\n?)+)/g,
    (_, header, body) => {
      const headers = header.split('|').filter(h => h.trim()).map(h => `<th>${h.trim()}</th>`).join('')
      const rows = body.trim().split('\n').map(row => {
        const cells = row.split('|').filter(c => c.trim()).map(c => `<td>${c.trim()}</td>`).join('')
        return `<tr>${cells}</tr>`
      }).join('')
      return `<table class="chat-table"><thead><tr>${headers}</tr></thead><tbody>${rows}</tbody></table>`
    }
  )
  // Bold
  escaped = escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  // Inline code
  escaped = escaped.replace(/`([^`]+)`/g, '<code>$1</code>')
  // Bullet points
  escaped = escaped.replace(/^[•\-*] (.+)$/gm, '<li>$1</li>')
  escaped = escaped.replace(/(<li>.*<\/li>(\n|$))+/g, m => `<ul>${m}</ul>`)
  // Line breaks (safe: pre placeholders contain no \n at this point)
  escaped = escaped.replace(/\n/g, '<br/>')
  // Restore box-drawing pre blocks
  escaped = escaped.replace(/\x00PRE(\d+)\x00/g, (_, i) => preBlocks[parseInt(i)])
  return escaped
}

// ── SSE parser ───────────────────────────────────────────
/**
 * Parse a raw SSE buffer into discrete events.
 * Port of the Tkinter chunk-writing loop from /chatbot/engine/chat_engine.py.
 */
function parseSSEEvents(buffer) {
  const events = []
  const blocks = buffer.split('\n\n')
  for (const block of blocks) {
    if (!block.trim()) continue
    let type = 'message'
    let data = ''
    for (const line of block.split('\n')) {
      if (line.startsWith('event: ')) type = line.slice(7).trim()
      else if (line.startsWith('data: '))  data = line.slice(6)
    }
    if (data) events.push({ type, data })
  }
  return events
}

// ── API helpers ──────────────────────────────────────────
const getCurrentUserId = () => authStore.user?.id || authStore.user?.uid || null

const getStoredSessionId = () => localStorage.getItem(SESSION_KEY)
const storeSessionId     = (id) => localStorage.setItem(SESSION_KEY, id)
const clearStoredSession = () => localStorage.removeItem(SESSION_KEY)

// ── Load sessions (sidebar) ──────────────────────────────
const loadSessions = async () => {
  const userId = getCurrentUserId()
  if (!userId) return
  try {
    const { data } = await chatbotAPI.getSessions(userId)
    chatHistory.value = data.map(s => ({ id: s.id, title: s.title }))
  } catch (e) {
    console.error('Failed to load sessions', e)
  }
}

// ── Load messages for a session ──────────────────────────
const loadMessages = async (sessionId) => {
  try {
    const { data } = await chatbotAPI.getMessages(sessionId)
    messages.value = data.map(m => ({
      id: msgIdCounter++,
      role: m.role === 'assistant' ? 'bot' : 'user',
      content: m.content,
      time: now()
    }))
    await scrollToBottom()
  } catch (e) {
    console.error('Failed to load messages', e)
  }
}

// ── Send message (SSE streaming) ─────────────────────────
/**
 * Port of /chatbot/chatbot.py ChatbotTab._send_message() + chunk-writing loop.
 * Replaces the old axios single-response call with real SSE streaming.
 */
const sendMessage = async () => {
  const text = inputText.value.trim()
  if (!text || isTyping.value) return

  messages.value.push({ id: msgIdCounter++, role: 'user', content: text, time: now() })
  inputText.value = ''
  if (inputRef.value) inputRef.value.style.height = 'auto'
  await scrollToBottom()

  isTyping.value   = true
  isStreaming.value = false

  const botMsgId = msgIdCounter++

  try {
    const token   = localStorage.getItem('access_token')
    const payload = {
      message:    text,
      session_id: activeSessionId.value || getStoredSessionId() || null,
      user_id:    getCurrentUserId()
    }

    const response = await fetch(`${API_BASE_URL}/chatbot/chat/stream`, {
      method:  'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      body: JSON.stringify(payload)
    })

    if (!response.ok) throw new Error(`HTTP ${response.status}`)

    const reader  = response.body.getReader()
    const decoder = new TextDecoder()
    let   buffer  = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })

      // Only process complete SSE events (end in \n\n)
      const lastDN = buffer.lastIndexOf('\n\n')
      if (lastDN === -1) continue
      const complete = buffer.slice(0, lastDN + 2)
      buffer = buffer.slice(lastDN + 2)

      for (const evt of parseSSEEvents(complete)) {
        try {
          const data = JSON.parse(evt.data)

          if (evt.type === 'message' && data.chunk !== undefined) {
            // First chunk: push the bot message placeholder
            if (!isStreaming.value) {
              isStreaming.value = true
              messages.value.push({
                id: botMsgId, role: 'bot', content: '',
                time: now(), showSearchBtn: false, searchQuery: ''
              })
            }
            const botMsg = messages.value.find(m => m.id === botMsgId)
            if (botMsg) botMsg.content += data.chunk
            await scrollToBottom()

          } else if (evt.type === 'online_search') {
            // Port of <<SHOW_WEB_SEARCH_BUTTON>> signal from old chatbot
            const botMsg = messages.value.find(m => m.id === botMsgId)
            if (botMsg) {
              botMsg.showSearchBtn = true
              botMsg.searchQuery   = data.query || text
            }

          } else if (evt.type === 'done') {
            // Persist session in sidebar
            if (data.session_id && data.session_id !== activeSessionId.value) {
              activeSessionId.value = data.session_id
              storeSessionId(data.session_id)
              if (!chatHistory.value.find(s => s.id === data.session_id)) {
                const title = text.length > 40 ? text.slice(0, 40) + '…' : text
                chatHistory.value.unshift({ id: data.session_id, title })
              }
            }
          }
        } catch (e) { /* skip unparseable events */ }
      }
    }
  } catch (err) {
    const errMsg = err.message?.includes('503')
      ? 'The AI service is temporarily unavailable. Please try again in a moment.'
      : 'Something went wrong. Please check your connection and try again.'
    // If streaming hadn't started yet, push a fresh error bubble
    if (!isStreaming.value) {
      messages.value.push({ id: botMsgId, role: 'bot', content: errMsg, time: now(), showSearchBtn: false, searchQuery: '' })
    } else {
      const botMsg = messages.value.find(m => m.id === botMsgId)
      if (botMsg) botMsg.content += `\n\n❌ ${errMsg}`
    }
  } finally {
    isTyping.value    = false
    isStreaming.value = false
    await scrollToBottom()
  }
}

// ── Search Online (port of perform_online_search) ─────────
/**
 * Triggered when user clicks the 'Search Online' button.
 * Port of /chatbot/engine/chat_engine.py perform_online_search().
 */
const performOnlineSearch = async (msg) => {
  msg.showSearchBtn = false
  isTyping.value    = true
  isStreaming.value = false

  const searchMsgId = msgIdCounter++

  try {
    const token   = localStorage.getItem('access_token')
    const payload = {
      message:     msg.searchQuery,
      session_id:  activeSessionId.value || null,
      search_hint: ''
    }

    const response = await fetch(`${API_BASE_URL}/chatbot/chat/search-online`, {
      method:  'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      body: JSON.stringify(payload)
    })

    if (!response.ok) throw new Error(`HTTP ${response.status}`)

    const reader  = response.body.getReader()
    const decoder = new TextDecoder()
    let   buffer  = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lastDN = buffer.lastIndexOf('\n\n')
      if (lastDN === -1) continue
      const complete = buffer.slice(0, lastDN + 2)
      buffer = buffer.slice(lastDN + 2)

      for (const evt of parseSSEEvents(complete)) {
        try {
          const data = JSON.parse(evt.data)
          if (evt.type === 'message' && data.chunk !== undefined) {
            if (!isStreaming.value) {
              isStreaming.value = true
              messages.value.push({
                id: searchMsgId, role: 'bot',
                content: '', time: now(),
                showSearchBtn: false, searchQuery: ''
              })
            }
            const searchMsg = messages.value.find(m => m.id === searchMsgId)
            if (searchMsg) searchMsg.content += data.chunk
            await scrollToBottom()
          }
        } catch (e) { /* skip */ }
      }
    }
  } catch (err) {
    messages.value.push({
      id: searchMsgId, role: 'bot',
      content: '❌ Online search failed. Please try again.',
      time: now(), showSearchBtn: false, searchQuery: ''
    })
  } finally {
    isTyping.value    = false
    isStreaming.value = false
    await scrollToBottom()
  }
}

const sendSuggestion = (text) => {
  inputText.value = text
  sendMessage()
}

// ── Session management ───────────────────────────────────
const clearChat = () => {
  messages.value = []
  inputText.value = ''
}

const startNewChat = () => {
  activeSessionId.value = null
  clearStoredSession()
  clearChat()
  messages.value.push({
    id: msgIdCounter++,
    role: 'bot',
    content: "Hello! I'm UniCompare Assistant. Ask me about university rankings, entry requirements, scholarships, or comparisons — all from our database.",
    time: now()
  })
}

const switchSession = async (session) => {
  activeSessionId.value = session.id
  storeSessionId(session.id)
  await loadMessages(session.id)
}

const deleteSession = async (session, event) => {
  event.stopPropagation()
  try {
    await chatbotAPI.deleteSession(session.id)
    chatHistory.value = chatHistory.value.filter(s => s.id !== session.id)
    if (activeSessionId.value === session.id) {
      startNewChat()
    }
  } catch (e) {
    console.error('Failed to delete session', e)
  }
}

// ── Init ─────────────────────────────────────────────────
onMounted(async () => {
  await loadSessions()

  const storedId = getStoredSessionId()
  if (storedId) {
    activeSessionId.value = storedId
    await loadMessages(storedId)
    if (!messages.value.length) {
      // Session gone or empty
      startNewChat()
    }
  } else {
    startNewChat()
  }
})
</script>

<style scoped>
.chatbot-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #f0f4f8;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* ── Layout ─────────────────────────────────────────── */
.chatbot-layout {
  flex: 1;
  display: flex;
  max-width: 1280px;
  width: 100%;
  margin: 28px auto;
  padding: 0 24px;
  gap: 20px;
  min-height: 0;
}

/* ── Sidebar ─────────────────────────────────────────── */
.sidebar {
  width: 240px;
  flex-shrink: 0;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e0e7f1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.sidebar-title {
  font-size: 13px;
  font-weight: 700;
  color: #1a1a2e;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.btn-new-chat {
  width: 28px; height: 28px;
  border-radius: 6px;
  border: 1px solid #d1d5db;
  background: #fff;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  color: #555;
  transition: background 0.15s, color 0.15s;
}
.btn-new-chat:hover { background: #e8f0fe; color: #1a73e8; border-color: #1a73e8; }

.history-list { flex: 1; overflow-y: auto; padding: 8px; }

.history-item {
  display: flex; align-items: center; gap: 8px;
  padding: 9px 10px;
  border-radius: 7px;
  cursor: pointer;
  font-size: 13px;
  color: #444;
  transition: background 0.15s;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.history-item:hover { background: #f3f4f6; }
.history-item.active { background: #e8f0fe; color: #1a73e8; font-weight: 600; }

.history-icon { flex-shrink: 0; color: inherit; }
.history-text { overflow: hidden; text-overflow: ellipsis; }
.history-empty { font-size: 12px; color: #bbb; text-align: center; padding: 24px 0; }

/* ── Chat Main ──────────────────────────────────────── */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e0e7f1;
  overflow: hidden;
  min-height: 600px;
}

/* Topbar */
.chat-topbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 20px;
  border-bottom: 1px solid #f0f0f0;
  background: #fff;
}
.chat-topbar-left { display: flex; align-items: center; gap: 12px; }
.topbar-avatar {
  width: 40px; height: 40px; border-radius: 50%;
  object-fit: cover; border: 2px solid #e0e7f1;
}
.topbar-name { font-size: 15px; font-weight: 700; color: #1a1a2e; }
.topbar-status { display: flex; align-items: center; gap: 5px; font-size: 12px; color: #22c55e; margin-top: 1px; }
.status-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: #22c55e; display: inline-block;
}

.btn-clear {
  display: flex; align-items: center; gap: 5px;
  background: none; border: 1px solid #e5e7eb;
  border-radius: 6px; padding: 6px 12px;
  font-size: 12px; color: #888; cursor: pointer;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}
.btn-clear:hover { background: #fce8e8; color: #d32f2f; border-color: #f9a8a8; }

/* Messages */
.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 24px 24px 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  scroll-behavior: smooth;
}

/* Welcome */
.welcome-state {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center;
  flex: 1;
  text-align: center;
  padding: 40px 20px;
}
.welcome-avatar {
  width: 80px; height: 80px; border-radius: 50%;
  object-fit: cover; border: 3px solid #e0e7f1;
  margin-bottom: 16px;
}
.welcome-title { font-size: 20px; font-weight: 700; color: #1a1a2e; margin: 0 0 8px; }
.welcome-sub { font-size: 14px; color: #777; max-width: 420px; line-height: 1.6; margin: 0 0 24px; }

.suggestion-chips { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; max-width: 600px; }
.chip {
  padding: 8px 14px;
  border: 1px solid #d0d5dd;
  border-radius: 20px;
  background: #f9fafb;
  font-size: 13px; color: #374151;
  cursor: pointer;
  transition: all 0.15s;
}
.chip:hover { background: #e8f0fe; border-color: #1a73e8; color: #1a73e8; }

/* Bubbles */
.message-row {
  display: flex;
  align-items: flex-end;
  gap: 10px;
}
.user-row { flex-direction: row-reverse; }

.msg-avatar {
  width: 32px; height: 32px; border-radius: 50%;
  object-fit: cover; flex-shrink: 0;
  border: 1px solid #e0e7f1;
}

.bubble {
  max-width: 68%;
  padding: 11px 15px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.6;
  position: relative;
}
.bubble-bot {
  background: #f3f4f6;
  color: #222;
  border-bottom-left-radius: 4px;
}
.bubble-user {
  background: #1f3ab0;
  color: #fff;
  border-bottom-right-radius: 4px;
}
.bubble-text { display: block; }
.bubble-time {
  display: block;
  font-size: 10px;
  color: rgba(0,0,0,0.35);
  margin-top: 4px;
  text-align: right;
}
.bubble-user .bubble-time { color: rgba(255,255,255,0.55); }

/* Typing animation */
.typing-bubble {
  display: flex; align-items: center; gap: 5px;
  padding: 14px 18px;
}
.dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #888;
  animation: bounce 1.2s infinite ease-in-out;
}
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-7px); }
}

/* Input */
.input-area {
  border-top: 1px solid #f0f0f0;
  padding: 14px 20px 12px;
  background: #fff;
}
.input-wrap {
  display: flex; align-items: flex-end; gap: 10px;
  background: #f3f4f6;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 8px 8px 8px 14px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.input-wrap:focus-within {
  border-color: #1f3ab0;
  box-shadow: 0 0 0 3px rgba(31,58,176,0.1);
  background: #fff;
}
.chat-input {
  flex: 1;
  border: none; outline: none;
  background: transparent;
  font-size: 14px; color: #222;
  resize: none;
  line-height: 1.5;
  font-family: inherit;
  min-height: 22px;
  max-height: 140px;
  overflow-y: auto;
}
.chat-input::placeholder { color: #aaa; }

.btn-send {
  width: 38px; height: 38px; flex-shrink: 0;
  border-radius: 9px;
  border: none;
  background: #1f3ab0;
  color: #fff;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.15s;
}
.btn-send:hover:not(:disabled) { background: #162d8a; }
.btn-send:disabled { background: #c5cbe8; cursor: not-allowed; }

.input-hint {
  font-size: 11px; color: #bbb;
  margin-top: 7px; text-align: center;
}
.input-hint kbd {
  background: #f0f0f0; border: 1px solid #d0d0d0;
  border-radius: 3px; padding: 0 4px;
  font-size: 10px; font-family: inherit;
}

/* Scrollbar */
.messages-area::-webkit-scrollbar,
.history-list::-webkit-scrollbar { width: 5px; }
.messages-area::-webkit-scrollbar-track,
.history-list::-webkit-scrollbar-track { background: transparent; }
.messages-area::-webkit-scrollbar-thumb,
.history-list::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 10px; }

/* Search Online button (shown in bot bubble when DB data is poor) */
.btn-search-online {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 10px;
  padding: 7px 14px;
  background: #1f3ab0;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-search-online:hover { background: #162d8a; }

/* Delete session button */
.btn-del-session {
  flex-shrink: 0; margin-left: auto;
  width: 18px; height: 18px;
  border: none; background: none; cursor: pointer;
  border-radius: 4px; color: #bbb;
  display: none; align-items: center; justify-content: center;
  padding: 0;
}
.history-item:hover .btn-del-session { display: flex; }
.btn-del-session:hover { background: #fce8e8; color: #d32f2f; }

/* Unicode box-drawing tables from bot messages */
:deep(.box-table) {
  font-family: 'Courier New', Consolas, monospace;
  font-size: 0.82em;
  background: #f8f9fa;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 12px 16px;
  overflow-x: auto;
  white-space: pre;
  line-height: 1.6;
  margin: 8px 0;
  display: block;
  color: #1e293b;
}

/* Markdown pipe table (fallback) */
:deep(.chat-table) {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
  font-size: 13px;
}
:deep(.chat-table th),
:deep(.chat-table td) {
  border: 1px solid #d1d5db;
  padding: 6px 10px;
  text-align: left;
}
:deep(.chat-table th) { background: #f0f4f8; font-weight: 700; }
:deep(.chat-table tr:nth-child(even) td) { background: #f9fafb; }
:deep(.bubble-bot ul) { padding-left: 18px; margin: 4px 0; }
:deep(.bubble-bot li) { margin-bottom: 2px; }
:deep(.bubble-bot code) {
  background: #f0f4f8; padding: 1px 5px;
  border-radius: 4px; font-size: 12px; font-family: monospace;
}

/* Responsive */
@media (max-width: 768px) {
  .chatbot-layout { flex-direction: column; padding: 0 12px; margin: 12px auto; }
  .sidebar { width: 100%; max-height: 180px; }
  .bubble { max-width: 85%; }
}
</style>
