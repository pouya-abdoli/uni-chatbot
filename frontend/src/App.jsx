import { AssistantRuntimeProvider, useLocalRuntime } from "@assistant-ui/react";
import { Thread } from "./components/thread.aui";
import axios from "axios";

// FastAPI chat endpoint.
const API_URL = "http://localhost:8000/chat";

// Extracts all text parts from a message and combines them into one string.
const getMessageText = (message) =>
  message.content
    .filter((part) => part.type === "text")
    .map((part) => part.text)
    .join("");

// Connects assistant-ui to the FastAPI backend.
const adapter = {
  // "async *run" (a generator) lets us show the answer while it is still arriving.
  async *run({ messages, abortSignal }) {
    // The user's newest message (the rest is context).
    const latestMessage = messages[messages.length - 1];

    // Convert prior messages into the {role, content} format the backend expects.
    const conversationHistory = messages.slice(0, -1).map((message) => ({
      role: message.role,
      content: getMessageText(message),
    }));

    // fetch (not axios): axios cannot read a stream in the browser.
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      // Send the new message plus history; abortSignal lets the user cancel.
      body: JSON.stringify({
        message: getMessageText(latestMessage),
        history: conversationHistory,
      }),
      signal: abortSignal,
    });

    // Bail out if the server returned an error status.
    if (!response.ok) throw new Error("Chat request failed");

    // Read the answer piece by piece.
    const reader = response.body.getReader();
    // Decoder turns raw bytes into text (stream: true handles split chars).
    const decoder = new TextDecoder();
    let text = "";

    // Loop until the stream is exhausted.
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      // Append the newly received chunk to the accumulated text.
      text += decoder.decode(value, { stream: true });

      // Always send the full text so far, not just the new piece.
      yield { content: [{ type: "text", text }] };
    }
  },
};

const App = () => {
  // Creates the chat runtime using the custom adapter.
  const runtime = useLocalRuntime(adapter);

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <div dir="rtl" className="h-dvh">
        <Thread />
      </div>
    </AssistantRuntimeProvider>
  );
};

export default App;
