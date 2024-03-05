/**
 * Selectors
 */
const historyContainer = document.getElementById(`history-container`);
const messageInput = document.getElementById(`prompt-input`);
const sendButton = document.getElementById(`send-button`);

/**
 * Global variables
 */
const serverAddress = 'http://localhost:5000';
const md = window.markdownit({
  html: true, // Enable HTML tags in source
  langPrefix: 'language-', // CSS language prefix for fenced blocks
  linkify: true, // autoconvert URL-like texts to links
  typographer: true, // Enable smartypants and other sweet transforms
  highlight: function (str, lang) { // Highlight code using highlight.js
    if (lang && hljs.getLanguage(lang)) {
      try {
        return '<pre class="hljs"><code>' +
                hljs.highlight(str, { language: lang, ignoreIllegals: true }).value +
                '</code></pre>';
      } catch (__) {}
    }

    return ''; // use external default escaping
  }
});
let lock = false; // lock the chat while waiting for a response
let responseMsgRaw = ''; // keep track of the raw response message per sse event

/**
 * SSE
 */
function registerSSE() {
  // close existing connection
  if (typeof eventSource !== 'undefined' && eventSource) {
    eventSource.close();
  }

  eventSource = new EventSource(serverAddress + '/sse');

  eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);

    // add token to history
    if (data.type === 'token') {
      const message = data.content;

      // find last ai-message
      const aiMessage = getLastAIMessage();

      // append to .content
      aiMessage.querySelector('.content').innerHTML  += message;

      responseMsgRaw += message;

    } else if (data.type === 'error') {
      console.error(content);
      responseMsgRaw = '';
      lock = false;
    } else if (data.type === 'end') {
      console.info('end');
      // apply markdown and code highlighting
      const aiMessage = getLastAIMessage();
      const content = aiMessage.querySelector('.content');
      content.innerHTML = addMarkdownToText(responseMsgRaw);
      responseMsgRaw = '';
      lock = false;
    }
  };

  eventSource.onopen = function(event) {
    console.info('SSE connection opened.');
  };

  // handle errors
  eventSource.onerror = function(event) {
    lock = false;
    console.error('EventSource failed:', event);
    eventSource.close();
  };

  // close the EventSource when the page is unloaded
  window.onbeforeunload = function() {
    console.info('SSE connection closed.');
    eventSource.close();
  };
}

/**
 * Helper functions
 */
function scrollToBottom() {
  window.scrollTo(0, document.body.scrollHeight);
}

function formatText(text) {
  return text.replace(/(?:\r\n|\r|\n)/g, '<br>');
}

function addMarkdownToText(text) {
  return md.render(text);
}

function getLastAIMessage() {
  return document.querySelector('.ai-message:last-child');
}

function getCurrentTimeString() {
  return new Date().toUTCString();
}

/**
 * Chat functions
 */
async function startQA() {
  const message = messageInput.value;

  if (!message) {
    console.error('No message entered.');
    return false;
  }

  messageInput.value = '';
  scrollToBottom();
  await addMessage(message);
  await startGeneratig(message);

  return false;
}

async function addMessage(message) {
  // add human message and add div for bot message
  historyContainer.innerHTML += `
  <div class="message user-message">
    <strong>User:</strong>
    <div class="content">${formatText(message)}</div>
  </div>
`;

  historyContainer.innerHTML += `
 <div class="message ai-message">
   <strong>AI:</strong>
   <div class="content"></div>
   <span class="metadata"></span>
 </div>
`;
}

async function startGeneratig(message) {
  lock = true;
  responseMsgRaw = '';

  try {
    const response = await fetch(serverAddress + '/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(
        { prompt: message }
      )
    });

    const data = await response.json();
    console.log(data);
  } catch (error) {
    lock = false;
    console.error(error);
  }
}

/**
 * Existing chat history
 */
function addMarkdownToAiMessages() {
  // TODO: load from data-attribute
  const aiMessages = document.querySelectorAll('.ai-message .content');
  aiMessages.forEach((message) => {
    message.innerHTML = addMarkdownToText(String(message.innerHTML));
  });
}

/**
 * DOM loaded
 */
document.addEventListener('DOMContentLoaded', function() {
  console.info('chat.js loaded');

  registerSSE();

  // add focus to message input
  messageInput.focus();

  // message input
  messageInput.addEventListener(`keydown`, async (event) => {
    if (lock) return;

    // enter without shift
    if (event.keyCode === 13 && !event.shiftKey) {
      event.preventDefault();
      console.log('pressed enter');
      await startQA();
    }
  });

  // send button
  sendButton.addEventListener(`click`, async (event) => {
    if (lock) return;
    await startQA();
  });

  addMarkdownToAiMessages();
});
